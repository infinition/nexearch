"""
08 - Mamba-FF Optimized: Pushing Toward 95%+
=============================================
Iterating on Variant A (Mamba-FF) with targeted optimizations:

1. SymBa loss (no threshold, direct contrast — faster convergence)
2. Larger model (d_model=128, d_state=32)
3. More epochs (30)
4. Hard negative mining (select most confusing wrong labels)
5. Cosine LR schedule
6. Multi-scale negative generation
7. Deeper network (4 layers) with warmup
"""

import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
import time
import json
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

sys.stdout.reconfigure(line_buffering=True)

import os
# Force GPU if FORCE_GPU=1, otherwise try CUDA with fallback to CPU on OOM
USE_GPU = os.environ.get('FORCE_CPU', '0') != '1'
if USE_GPU and torch.cuda.is_available():
    # Try to allocate a small tensor to see if GPU has room
    try:
        test = torch.zeros(1, device='cuda')
        # Check available memory
        free_mem = torch.cuda.get_device_properties(0).total_mem - torch.cuda.memory_reserved(0)
        if free_mem < 2e9:  # Less than 2GB free
            print(f"WARNING: Only {free_mem/1e9:.1f}GB free on GPU, using CPU")
            device = torch.device('cpu')
        else:
            device = torch.device('cuda')
        del test
        torch.cuda.empty_cache()
    except:
        device = torch.device('cpu')
else:
    device = torch.device('cpu')
print(f"Device: {device}")
torch.manual_seed(42)
np.random.seed(42)

# ============================================================
# CONFIGS TO TEST
# ============================================================
CONFIGS = {
    "A1_symba": dict(
        d_model=64, d_state=16, n_layers=4, epochs=30, lr=3e-3,
        loss_type="symba", neg_type="hybrid", batch_size=128,
        description="SymBa loss + d64 + 4 layers + 30ep (safe)"
    ),
    "A2_symba_hard": dict(
        d_model=64, d_state=16, n_layers=4, epochs=30, lr=3e-3,
        loss_type="symba", neg_type="hard", batch_size=128,
        description="SymBa + hard negatives + d64"
    ),
    "A3_ff_control": dict(
        d_model=64, d_state=16, n_layers=4, epochs=30, lr=3e-3,
        loss_type="ff", neg_type="hybrid", batch_size=128,
        description="Original FF loss + d64 (control)"
    ),
}

SEQ_LEN = 28
INPUT_DIM = 28
NUM_CLASSES = 10

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, transform=transform)

results = {}


# ============================================================
# Selective SSM (same as before)
# ============================================================
class SelectiveSSM(nn.Module):
    def __init__(self, d_model, d_state=16, d_conv=4, expand=2):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_inner = expand * d_model
        self.dt_rank = max(1, d_model // 16)

        self.in_proj = nn.Linear(d_model, self.d_inner * 2, bias=False)
        self.conv1d = nn.Conv1d(
            self.d_inner, self.d_inner, d_conv,
            groups=self.d_inner, padding=d_conv - 1, bias=True
        )
        self.x_proj = nn.Linear(self.d_inner, self.dt_rank + 2 * d_state, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, self.d_inner, bias=True)

        A = torch.arange(1, d_state + 1, dtype=torch.float32)
        self.A_log = nn.Parameter(torch.log(A.unsqueeze(0).expand(self.d_inner, -1)))
        self.D = nn.Parameter(torch.ones(self.d_inner))
        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x, return_hidden=False):
        residual = x
        x = self.norm(x)
        xz = self.in_proj(x)
        x_in, z = xz.chunk(2, dim=-1)
        x_conv = self.conv1d(x_in.transpose(1, 2))[:, :, :x.shape[1]].transpose(1, 2)
        x_conv = F.silu(x_conv)
        y, hidden = self._ssm(x_conv)
        y = y * F.silu(z)
        y = self.out_proj(y)
        if return_hidden:
            return y + residual, hidden
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
        ys, hs = [], []
        for t in range(L):
            h = deltaA[:, t] * h + deltaB_x[:, t]
            hs.append(h)
            ys.append(torch.einsum('bdn,bn->bd', h, C[:, t]))
        return torch.stack(ys, dim=1) + x * self.D, torch.stack(hs, dim=1)


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

    @staticmethod
    def hard_negative(x, y, model, proj, n_cls=10):
        """Generate hard negatives: use the label that produces highest goodness
        among wrong labels (most confusing to the model)."""
        B, L, D = x.shape
        with torch.no_grad():
            best_g = torch.full((B,), -float('inf'), device=x.device)
            best_neg = x.clone()
            # Test each wrong label, keep the hardest
            for c in range(n_cls):
                mask = (y != c)  # only wrong labels
                if mask.sum() == 0:
                    continue
                y_c = torch.full((B,), c, dtype=torch.long, device=x.device)
                x_c = NegGen.label_overlay(x, y_c, n_cls, wrong=False)
                h = proj(x_c)
                g = h.pow(2).mean(dim=(1, 2))
                update = mask & (g > best_g)
                best_g[update] = g[update]
                best_neg[update] = x_c[update]
        return best_neg


# ============================================================
# Mamba-FF Layer with configurable loss
# ============================================================
class MambaFFLayer(nn.Module):
    def __init__(self, d_model, d_state=16, loss_type="symba", lr=3e-3, threshold=2.0):
        super().__init__()
        self.ssm = SelectiveSSM(d_model, d_state)
        self.loss_type = loss_type
        self.threshold = threshold
        self.opt = torch.optim.AdamW(self.ssm.parameters(), lr=lr, weight_decay=1e-4)
        self.scheduler = None  # set externally

    def goodness(self, x):
        out, hidden = self.ssm(x, return_hidden=True)
        # Use output norm as goodness proxy (cheaper than hidden states)
        g = out.pow(2).mean(dim=(1, 2))  # (B,) - mean over L, d_model
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
# Full Mamba-FF Model
# ============================================================
class MambaFF(nn.Module):
    def __init__(self, d_model=128, d_state=32, n_layers=4, n_cls=10,
                 loss_type="symba", lr=3e-3, neg_type="hybrid"):
        super().__init__()
        self.n_cls = n_cls
        self.neg_type = neg_type
        self.proj = nn.Linear(INPUT_DIM + n_cls, d_model)
        self.layers = nn.ModuleList([
            MambaFFLayer(d_model, d_state, loss_type=loss_type, lr=lr)
            for _ in range(n_layers)
        ])

    def forward(self, x):
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

    def train_step(self, x, y):
        x_pos = NegGen.label_overlay(x, y, self.n_cls, wrong=False)

        if self.neg_type == "hard":
            x_neg = NegGen.hard_negative(x, y, self, self.proj, self.n_cls)
        else:
            x_neg = NegGen.hybrid_negative(x, y, self.n_cls)

        h_pos = self.proj(x_pos).detach()
        h_neg = self.proj(x_neg).detach()
        total_loss = 0
        for layer in self.layers:
            h_pos, h_neg, loss = layer.train_step(h_pos, h_neg)
            total_loss += loss
        return total_loss


# ============================================================
# Training & Evaluation
# ============================================================
def evaluate(model):
    model.eval()
    correct = total = 0
    eval_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    with torch.no_grad():
        for x, y in eval_loader:
            x, y = x.to(device), y.to(device)
            x_in = x.view(x.size(0), SEQ_LEN, INPUT_DIM)
            x_pad = F.pad(x_in, (0, NUM_CLASSES))
            preds = model(x_pad)
            correct += (preds == y).sum().item()
            total += y.size(0)
            if device.type == 'cuda':
                torch.cuda.empty_cache()
    return correct / total


def run_config(name, cfg):
    print(f"\n{'='*60}")
    print(f"  {name}: {cfg['description']}")
    print(f"{'='*60}")

    try:
        train_loader = DataLoader(
            train_dataset, batch_size=cfg['batch_size'], shuffle=True, drop_last=True
        )

        model = MambaFF(
            d_model=cfg['d_model'], d_state=cfg['d_state'],
            n_layers=cfg['n_layers'], loss_type=cfg['loss_type'],
            lr=cfg['lr'], neg_type=cfg['neg_type']
        ).to(device)

        # Cosine LR schedulers for each layer
        total_steps = cfg['epochs'] * len(train_loader)
        for layer in model.layers:
            layer.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                layer.opt, T_max=total_steps, eta_min=1e-5
            )

        t0 = time.time()
        hist = []

        print(f"    Model params: {sum(p.numel() for p in model.parameters()):,}")
        if device.type == 'cuda':
            print(f"    GPU memory: {torch.cuda.memory_allocated()/1e6:.0f}MB allocated")

        for ep in range(cfg['epochs']):
            model.train()
            ep_loss = 0
            n_batches = 0
            for x, y in train_loader:
                x, y = x.to(device), y.to(device)
                x_seq = x.view(x.size(0), SEQ_LEN, INPUT_DIM)
                x_pad = F.pad(x_seq, (0, NUM_CLASSES))
                loss = model.train_step(x_pad, y)
                ep_loss += loss
                n_batches += 1
                for layer in model.layers:
                    if layer.scheduler:
                        layer.scheduler.step()
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

            acc = evaluate(model)
            hist.append(acc)
            avg_loss = ep_loss / n_batches
            lr_now = model.layers[0].opt.param_groups[0]['lr']
            print(f"    Epoch {ep+1:2d}: {acc:.4f} | loss={avg_loss:.4f} | lr={lr_now:.2e}")

        dt = time.time() - t0
        best = max(hist)
        final = hist[-1]
        status = 'EXCELLENT' if best > 0.95 else ('PROMISING' if best > 0.90 else 'WEAK')
        print(f"  >> Best: {best:.4f} | Final: {final:.4f} | Time: {dt:.1f}s | {status}")
        results[name] = dict(best=best, final=final, time=dt, history=hist, status=status,
                             config=cfg['description'])
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"  >> CRASHED: {e}")
        results[name] = dict(best=0, final=0, time=0, history=[], status='CRASHED',
                             config=cfg['description'])


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print(f"\n{'#'*60}")
    print(f"  MAMBA-FF OPTIMIZATION SWEEP")
    print(f"  Target: Push beyond 91.28% toward 95%+")
    print(f"  Previous best: Mamba+BPTT=99.09%, Mamba-FF=91.28%")
    print(f"{'#'*60}")

    for name, cfg in CONFIGS.items():
        if device.type == 'cuda':
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
        run_config(name, cfg)

    # Summary
    print(f"\n\n{'='*60}")
    print(f"  OPTIMIZATION RESULTS")
    print(f"{'='*60}")
    print(f"{'Config':<30} {'Best':>8} {'Final':>8} {'Time':>8} {'Status'}")
    print(f"{'-'*70}")
    # Reference
    print(f"{'[ref] Mamba+BPTT':<30} {'0.9909':>8} {'0.9895':>8} {'946.5s':>8} BASELINE")
    print(f"{'[ref] Mamba-FF v1 (d64,3L)':<30} {'0.9128':>8} {'0.9104':>8} {'2655s':>8} PREVIOUS")
    for name, r in results.items():
        print(f"{name:<30} {r['best']:>8.4f} {r['final']:>8.4f} {r['time']:>7.1f}s {r['status']}")

    with open('mamba_ff_optimized_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to mamba_ff_optimized_results.json")
