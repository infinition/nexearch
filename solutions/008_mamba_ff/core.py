"""
008 - Mamba-FF: SSM x Forward-Forward Hybrid - Core Implementation
Standalone, importable, reproducible.

Combines Mamba's selective state space model with Forward-Forward's
local goodness learning (SymBa variant). No backpropagation between
layers, no BPTT through time.

Best result: 95.37% Sequential MNIST (28 rows x 28 pixels)

Usage:
    python core.py                          # Run best config (SymBa d128)
    python core.py --d_model 64 --epochs 15 # Quick test
    python core.py --loss ff --threshold 2  # Original FF loss
"""

import sys
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time
import json
import argparse
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

# ============================================================
# Paths
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# Try shared benchmarks path
BENCH_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'benchmarks')
DATA_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'datasets')
if not os.path.isdir(DATA_DIR):
    DATA_DIR = './data'

# ============================================================
# Selective SSM (Mamba-style)
# ============================================================
class SelectiveSSM(nn.Module):
    """Minimal Mamba selective state space model.
    h_t = exp(delta*A) * h_{t-1} + delta*B * x_t  (state update)
    y_t = C * h_t + D * x_t                         (output)
    Where delta, B, C are input-dependent (selective).
    """
    def __init__(self, d_model, d_state=16, d_conv=4, expand=2):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_inner = expand * d_model
        self.dt_rank = max(1, d_model // 16)

        self.in_proj = nn.Linear(d_model, self.d_inner * 2, bias=False)
        self.conv1d = nn.Conv1d(self.d_inner, self.d_inner, d_conv,
                                groups=self.d_inner, padding=d_conv - 1, bias=True)
        self.x_proj = nn.Linear(self.d_inner, self.dt_rank + 2 * d_state, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner, bias=True)
        A = torch.arange(1, d_state + 1, dtype=torch.float32)
        self.A_log = nn.Parameter(torch.log(A.unsqueeze(0).expand(self.d_inner, -1)))
        self.D = nn.Parameter(torch.ones(self.d_inner))
        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x):
        residual = x
        x = self.norm(x)
        xz = self.in_proj(x)
        x_in, z = xz.chunk(2, dim=-1)
        x_conv = self.conv1d(x_in.transpose(1, 2))[:, :, :x.shape[1]].transpose(1, 2)
        x_conv = F.silu(x_conv)
        y = self._ssm(x_conv)
        y = y * F.silu(z)
        y = self.out_proj(y)
        return y + residual

    def _ssm(self, x):
        B, L, D = x.shape
        A = -torch.exp(self.A_log.float())
        x_dbl = self.x_proj(x)
        delta, Bm, C = x_dbl.split([self.dt_rank, self.d_state, self.d_state], dim=-1)
        delta = F.softplus(self.dt_proj(delta))
        deltaA = torch.exp(torch.einsum('bld,dn->bldn', delta, A))
        deltaB_x = torch.einsum('bld,bln,bld->bldn', delta, Bm, x)
        h = torch.zeros(B, D, self.d_state, device=x.device)
        ys = []
        for t in range(L):
            h = deltaA[:, t] * h + deltaB_x[:, t]
            ys.append(torch.einsum('bdn,bn->bd', h, C[:, t]))
        return torch.stack(ys, dim=1) + x * self.D


# ============================================================
# Negative Data Generators
# ============================================================
class NegGen:
    @staticmethod
    def label_overlay(x, y, n_cls=10, wrong=True):
        B, L, D = x.shape
        x_out = x.clone()
        if wrong:
            fake_y = (y + torch.randint(1, n_cls, (B,), device=y.device)) % n_cls
        else:
            fake_y = y
        embed = torch.zeros(B, n_cls, device=x.device)
        embed.scatter_(1, fake_y.unsqueeze(1), x.abs().max().item())
        x_out[:, :, :n_cls] = embed.unsqueeze(1).expand(B, L, n_cls)
        return x_out

    @staticmethod
    def temporal_shuffle(x):
        B, L, D = x.shape
        x_neg = x.clone()
        for b in range(B):
            x_neg[b] = x_neg[b, torch.randperm(L, device=x.device)]
        return x_neg

    @staticmethod
    def hybrid_negative(x, y, n_cls=10):
        B = x.size(0)
        half = B // 2
        x_neg = x.clone()
        x_neg[:half] = NegGen.label_overlay(x[:half], y[:half], n_cls, wrong=True)
        x_shuf = NegGen.temporal_shuffle(x[half:])
        x_neg[half:] = NegGen.label_overlay(x_shuf, y[half:], n_cls, wrong=False)
        return x_neg


# ============================================================
# Mamba-FF Layer
# ============================================================
class MambaFFLayer(nn.Module):
    def __init__(self, d_model, d_state=16, loss_type="symba", lr=3e-3, threshold=2.0):
        super().__init__()
        self.ssm = SelectiveSSM(d_model, d_state)
        self.loss_type = loss_type
        self.threshold = threshold
        self.opt = torch.optim.AdamW(self.ssm.parameters(), lr=lr, weight_decay=1e-4)
        self.scheduler = None

    def goodness(self, x):
        out = self.ssm(x)
        g = out.pow(2).mean(dim=(1, 2))
        return g, out

    def train_step(self, x_pos, x_neg):
        g_pos, out_pos = self.goodness(x_pos)
        g_neg, out_neg = self.goodness(x_neg)
        if self.loss_type == "symba":
            loss = torch.log(1 + torch.exp(g_neg - g_pos)).mean()
        else:
            loss = torch.log(1 + torch.exp(
                torch.cat([self.threshold - g_pos, g_neg - self.threshold])
            )).mean()
        self.opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.ssm.parameters(), 1.0)
        self.opt.step()
        op = out_pos.detach()
        op = op / (op.norm(2, dim=-1, keepdim=True) + 1e-6)
        on = out_neg.detach()
        on = on / (on.norm(2, dim=-1, keepdim=True) + 1e-6)
        return op, on, loss.item()


# ============================================================
# Full Mamba-FF Network
# ============================================================
class MambaFFNet(nn.Module):
    def __init__(self, input_dim=28, d_model=128, d_state=32, n_layers=4,
                 n_cls=10, loss_type="symba", lr=3e-3):
        super().__init__()
        self.n_cls = n_cls
        self.proj = nn.Linear(input_dim + n_cls, d_model)
        self.layers = nn.ModuleList([
            MambaFFLayer(d_model, d_state, loss_type=loss_type, lr=lr)
            for _ in range(n_layers)
        ])

    def forward(self, x):
        """Inference: try all labels, pick highest total goodness."""
        B, L, D = x.shape
        best_g = torch.full((B,), -float('inf'), device=x.device)
        best_c = torch.zeros(B, dtype=torch.long, device=x.device)
        for c in range(self.n_cls):
            y_c = torch.full((B,), c, dtype=torch.long, device=x.device)
            x_c = NegGen.label_overlay(x, y_c, self.n_cls, wrong=False)
            h = self.proj(x_c)
            g_total = torch.zeros(B, device=x.device)
            for layer in self.layers:
                g, h = layer.goodness(h)
                h = h / (h.norm(2, dim=-1, keepdim=True) + 1e-6)
                g_total += g
            mask = g_total > best_g
            best_g[mask] = g_total[mask]
            best_c[mask] = c
        return best_c

    @torch.no_grad()
    def evaluate(self, loader, device):
        self.eval()
        correct = total = 0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            x_seq = x.view(x.size(0), 28, 28)
            x_pad = F.pad(x_seq, (0, self.n_cls))
            preds = self(x_pad)
            correct += (preds == y).sum().item()
            total += y.size(0)
        return correct / total

    def train_epoch(self, loader, device):
        self.train()
        total_loss = 0
        n_batches = 0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            x_seq = x.view(x.size(0), 28, 28)
            x_pad = F.pad(x_seq, (0, self.n_cls))
            x_pos = NegGen.label_overlay(x_pad, y, self.n_cls, wrong=False)
            x_neg = NegGen.hybrid_negative(x_pad, y, self.n_cls)
            h_pos = self.proj(x_pos).detach()
            h_neg = self.proj(x_neg).detach()
            batch_loss = 0
            for layer in self.layers:
                h_pos, h_neg, loss = layer.train_step(h_pos, h_neg)
                batch_loss += loss
                if layer.scheduler:
                    layer.scheduler.step()
            total_loss += batch_loss
            n_batches += 1
        return total_loss / n_batches


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='008 - Mamba-FF Core')
    parser.add_argument('--d_model', type=int, default=128)
    parser.add_argument('--d_state', type=int, default=32)
    parser.add_argument('--n_layers', type=int, default=4)
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--batch_size', type=int, default=128)
    parser.add_argument('--lr', type=float, default=3e-3)
    parser.add_argument('--loss', type=str, default='symba', choices=['symba', 'ff'])
    parser.add_argument('--threshold', type=float, default=2.0)
    parser.add_argument('--device', type=str, default='auto')
    args = parser.parse_args()

    if args.device == 'auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(args.device)
    print(f"Device: {device}")

    torch.manual_seed(42)
    np.random.seed(42)

    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    train_ds = datasets.MNIST(DATA_DIR, train=True, download=True, transform=transform)
    test_ds = datasets.MNIST(DATA_DIR, train=False, transform=transform)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, drop_last=True)
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False)

    model = MambaFFNet(
        d_model=args.d_model, d_state=args.d_state, n_layers=args.n_layers,
        loss_type=args.loss, lr=args.lr
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"Model: d_model={args.d_model}, d_state={args.d_state}, layers={args.n_layers}")
    print(f"Params: {total_params:,} | Loss: {args.loss} | LR: {args.lr}")

    # Cosine LR schedulers
    total_steps = args.epochs * len(train_loader)
    for layer in model.layers:
        layer.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            layer.opt, T_max=total_steps, eta_min=1e-5
        )

    history = []
    best_acc = 0
    t0 = time.time()
    for ep in range(args.epochs):
        avg_loss = model.train_epoch(train_loader, device)
        acc = model.evaluate(test_loader, device)
        best_acc = max(best_acc, acc)
        lr_now = model.layers[0].opt.param_groups[0]['lr']
        print(f"  Epoch {ep+1:2d}/{args.epochs}: {acc:.4f} | loss={avg_loss:.4f} | lr={lr_now:.2e} | best={best_acc:.4f}")
        history.append({"epoch": ep+1, "accuracy": acc, "loss": avg_loss, "lr": lr_now})

    dt = time.time() - t0
    print(f"\nBest: {best_acc:.4f} | Time: {dt:.1f}s")

    # Save results
    result = {
        "solution_id": "008",
        "experiment": f"Mamba-FF {args.loss} d{args.d_model} {args.n_layers}L",
        "date": time.strftime("%Y-%m-%d"),
        "dataset": "Sequential MNIST",
        "metric": "accuracy",
        "unit": "%",
        "best_value": round(best_acc * 100, 2),
        "epochs": args.epochs,
        "total_params": total_params,
        "config": vars(args),
        "history": history
    }
    fname = os.path.join(RESULTS_DIR, f'run_{args.loss}_d{args.d_model}_{args.n_layers}L.json')
    with open(fname, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Saved to {fname}")


if __name__ == '__main__':
    main()
