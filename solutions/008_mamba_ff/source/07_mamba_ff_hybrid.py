"""
07 - Mamba x Forward-Forward Hybrid: Beyond Backpropagation
============================================================
Prototype validating 3 hybrid architectures that combine:
- Mamba's selective state space (temporal compression)
- Forward-Forward's local goodness learning (no backprop between layers)
- Predictive Coding's local error signals (no BPTT within layers)

Task: Row-Sequential MNIST (28 rows of 28 pixels = 28 timesteps)
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

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# ============================================================
# CONFIG
# ============================================================
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")
torch.manual_seed(42)
np.random.seed(42)

D_MODEL = 64
D_STATE = 16
D_CONV = 4
EXPAND = 2
NUM_LAYERS = 3
NUM_CLASSES = 10
SEQ_LEN = 28         # 28 rows
INPUT_DIM = 28        # 28 pixels per row
BATCH_SIZE = 128
EPOCHS = 15
LR = 3e-3
FF_THRESHOLD = 2.0

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)
test_loader_small = DataLoader(test_dataset, batch_size=64, shuffle=False)  # for FF eval

results = {}

# ============================================================
# CORE: Selective SSM (Mamba-style, optimized)
# ============================================================
class SelectiveSSM(nn.Module):
    """Minimal Mamba selective SSM. Optimized for short sequences."""

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
        """x: (B, L, d_model) -> (B, L, d_model)"""
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

        # Vectorized discretization
        deltaA = torch.exp(torch.einsum('bld,dn->bldn', delta, A))
        deltaB_x = torch.einsum('bld,bln,bld->bldn', delta, Bm, x)

        # Sequential scan (L=28, fast enough)
        h = torch.zeros(B, D, self.d_state, device=x.device)
        ys = []
        hs = []
        for t in range(L):
            h = deltaA[:, t] * h + deltaB_x[:, t]
            hs.append(h)
            y_t = torch.einsum('bdn,bn->bd', h, C[:, t])
            ys.append(y_t)

        y = torch.stack(ys, dim=1)
        hidden = torch.stack(hs, dim=1)  # (B, L, D, N)
        return y + x * self.D, hidden


# ============================================================
# NEGATIVE DATA GENERATORS
# ============================================================
class NegGen:
    @staticmethod
    def label_overlay(x, y, n_cls=10, wrong=True):
        """Embed label in first n_cls dims of each timestep."""
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
        """Shuffle rows (temporal order)."""
        B, L, D = x.shape
        x_neg = x.clone()
        for b in range(B):
            perm = torch.randperm(L, device=x.device)
            x_neg[b] = x_neg[b, perm]
        return x_neg

    @staticmethod
    def hybrid_negative(x, y, n_cls=10):
        """50% label overlay wrong + 50% temporal shuffle."""
        B = x.size(0)
        half = B // 2
        x_neg = x.clone()
        # First half: wrong labels
        x_neg[:half] = NegGen.label_overlay(x[:half], y[:half], n_cls, wrong=True)
        # Second half: temporal shuffle with correct labels
        x_shuf = NegGen.temporal_shuffle(x[half:])
        x_neg[half:] = NegGen.label_overlay(x_shuf, y[half:], n_cls, wrong=False)
        return x_neg


# ============================================================
# VARIANT A: Mamba-FF
# ============================================================
class MambaFFLayer(nn.Module):
    def __init__(self, d_model, d_state=16, threshold=FF_THRESHOLD, lr=LR):
        super().__init__()
        self.ssm = SelectiveSSM(d_model, d_state)
        self.threshold = threshold
        self.opt = torch.optim.Adam(self.ssm.parameters(), lr=lr)

    def forward(self, x):
        return self.ssm(x)

    def goodness(self, x):
        out, hidden = self.ssm(x, return_hidden=True)
        g = hidden.pow(2).mean(dim=(1, 2, 3))  # (B,)
        return g, out

    def train_step(self, x_pos, x_neg):
        g_pos, out_pos = self.goodness(x_pos)
        g_neg, out_neg = self.goodness(x_neg)

        loss = torch.log(1 + torch.exp(
            torch.cat([self.threshold - g_pos, g_neg - self.threshold])
        )).mean()

        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

        # L2 normalize outputs (prevent magnitude leakage)
        op = out_pos.detach()
        op = op / (op.norm(2, dim=-1, keepdim=True) + 1e-6)
        on = out_neg.detach()
        on = on / (on.norm(2, dim=-1, keepdim=True) + 1e-6)
        return op, on, loss.item()


class MambaFF(nn.Module):
    def __init__(self, input_dim=INPUT_DIM, d_model=D_MODEL, n_layers=NUM_LAYERS, n_cls=NUM_CLASSES):
        super().__init__()
        self.n_cls = n_cls
        self.proj = nn.Linear(input_dim + n_cls, d_model)
        self.layers = nn.ModuleList([MambaFFLayer(d_model) for _ in range(n_layers)])

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
        x_neg = NegGen.hybrid_negative(x, y, self.n_cls)
        h_pos = self.proj(x_pos).detach()
        h_neg = self.proj(x_neg).detach()
        total_loss = 0
        for layer in self.layers:
            h_pos, h_neg, loss = layer.train_step(h_pos, h_neg)
            total_loss += loss
        return total_loss


# ============================================================
# VARIANT B: Mamba-PC
# ============================================================
class MambaPCLayer(nn.Module):
    def __init__(self, d_model, d_state=16, lr=LR):
        super().__init__()
        self.ssm = SelectiveSSM(d_model, d_state)
        self.predictor = nn.Linear(d_model, d_model)
        self.opt = torch.optim.Adam(
            list(self.ssm.parameters()) + list(self.predictor.parameters()), lr=lr
        )

    def forward(self, x):
        return self.ssm(x)

    def train_step(self, x):
        out = self.ssm(x)
        pred = self.predictor(out[:, :-1])
        target = out[:, 1:].detach()
        loss = (pred - target).pow(2).mean()
        self.opt.zero_grad()
        loss.backward()
        self.opt.step()
        return out.detach(), loss.item()


class MambaPC(nn.Module):
    def __init__(self, input_dim=INPUT_DIM, d_model=D_MODEL, n_layers=NUM_LAYERS, n_cls=NUM_CLASSES):
        super().__init__()
        self.proj = nn.Linear(input_dim, d_model)
        self.layers = nn.ModuleList([MambaPCLayer(d_model) for _ in range(n_layers)])
        self.head = nn.Linear(d_model, n_cls)
        self.head_opt = torch.optim.Adam(
            list(self.proj.parameters()) + list(self.head.parameters()), lr=LR
        )

    def forward(self, x):
        h = self.proj(x)
        for layer in self.layers:
            h = layer(h)
        return self.head(h.mean(dim=1))

    def train_step(self, x, y):
        h = self.proj(x).detach()
        pc_loss = 0
        for layer in self.layers:
            h, loss = layer.train_step(h)
            pc_loss += loss

        logits = self.head(h.mean(dim=1))
        cls_loss = F.cross_entropy(logits, y)
        self.head_opt.zero_grad()
        cls_loss.backward()
        self.head_opt.step()
        return pc_loss, cls_loss.item()


# ============================================================
# VARIANT C: Mamba-HYB (PC + FF)
# ============================================================
class MambaHybLayer(nn.Module):
    def __init__(self, d_model, d_state=16, threshold=FF_THRESHOLD, lr=LR, alpha=0.5):
        super().__init__()
        self.ssm = SelectiveSSM(d_model, d_state)
        self.predictor = nn.Linear(d_model, d_model)
        self.threshold = threshold
        self.alpha = alpha
        self.opt = torch.optim.Adam(
            list(self.ssm.parameters()) + list(self.predictor.parameters()), lr=lr
        )

    def forward(self, x):
        return self.ssm(x)

    def goodness(self, x):
        out, hidden = self.ssm(x, return_hidden=True)
        g = hidden.pow(2).mean(dim=(1, 2, 3))
        return g, out

    def train_step(self, x_pos, x_neg):
        g_pos, out_pos = self.goodness(x_pos)
        g_neg, out_neg = self.goodness(x_neg)

        loss_ff = torch.log(1 + torch.exp(
            torch.cat([self.threshold - g_pos, g_neg - self.threshold])
        )).mean()

        pred = self.predictor(out_pos[:, :-1])
        target = out_pos[:, 1:].detach()
        loss_pc = (pred - target).pow(2).mean()

        loss = self.alpha * loss_pc + (1 - self.alpha) * loss_ff

        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

        op = out_pos.detach()
        op = op / (op.norm(2, dim=-1, keepdim=True) + 1e-6)
        on = out_neg.detach()
        on = on / (on.norm(2, dim=-1, keepdim=True) + 1e-6)
        return op, on, loss.item()


class MambaHyb(nn.Module):
    def __init__(self, input_dim=INPUT_DIM, d_model=D_MODEL, n_layers=NUM_LAYERS,
                 n_cls=NUM_CLASSES, alpha=0.5):
        super().__init__()
        self.n_cls = n_cls
        self.proj = nn.Linear(input_dim + n_cls, d_model)
        self.layers = nn.ModuleList([
            MambaHybLayer(d_model, alpha=alpha) for _ in range(n_layers)
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
        x_neg = NegGen.hybrid_negative(x, y, self.n_cls)
        h_pos = self.proj(x_pos).detach()
        h_neg = self.proj(x_neg).detach()
        total_loss = 0
        for layer in self.layers:
            h_pos, h_neg, loss = layer.train_step(h_pos, h_neg)
            total_loss += loss
        return total_loss


# ============================================================
# BASELINES
# ============================================================
class MambaBPTT(nn.Module):
    """Standard Mamba + backprop (gold standard baseline)."""
    def __init__(self, input_dim=INPUT_DIM, d_model=D_MODEL, n_layers=NUM_LAYERS, n_cls=NUM_CLASSES):
        super().__init__()
        self.proj = nn.Linear(input_dim, d_model)
        self.layers = nn.ModuleList([SelectiveSSM(d_model) for _ in range(n_layers)])
        self.head = nn.Linear(d_model, n_cls)

    def forward(self, x):
        h = self.proj(x)
        for layer in self.layers:
            h = layer(h)
        return self.head(h.mean(dim=1))


class PureFF(nn.Module):
    """Pure Forward-Forward MLP (Hinton baseline)."""
    def __init__(self, input_dim=784, d_hidden=256, n_layers=NUM_LAYERS, n_cls=NUM_CLASSES):
        super().__init__()
        self.n_cls = n_cls
        self.input_dim = input_dim
        self.threshold = FF_THRESHOLD
        dims = [input_dim + n_cls] + [d_hidden] * n_layers
        self.layers = nn.ModuleList([nn.Linear(dims[i], dims[i+1]) for i in range(n_layers)])
        self.opts = [torch.optim.Adam(l.parameters(), lr=0.03) for l in self.layers]

    def _fwd(self, layer, x):
        return F.relu(layer(x / (x.norm(2, dim=-1, keepdim=True) + 1e-6)))

    def _overlay(self, x, y, wrong=False):
        """Overlay label in first n_cls dims. Input x must be (B, input_dim)."""
        B = x.shape[0]
        if wrong:
            y = (y + torch.randint(1, self.n_cls, y.shape, device=y.device)) % self.n_cls
        # Concatenate label one-hot to input
        label = torch.zeros(B, self.n_cls, device=x.device)
        label[torch.arange(B), y] = x.abs().max()
        return torch.cat([label, x], dim=1)  # (B, n_cls + input_dim)

    def forward(self, x_flat):
        B = x_flat.shape[0]
        best_g = torch.full((B,), -float('inf'), device=x_flat.device)
        best_c = torch.zeros(B, dtype=torch.long, device=x_flat.device)
        for c in range(self.n_cls):
            y_c = torch.full((B,), c, dtype=torch.long, device=x_flat.device)
            h = self._overlay(x_flat, y_c, wrong=False)
            g_total = torch.zeros(B, device=x_flat.device)
            for layer in self.layers:
                h = self._fwd(layer, h)
                g_total += h.pow(2).mean(dim=1)
            mask = g_total > best_g
            best_g[mask] = g_total[mask]
            best_c[mask] = c
        return best_c

    def train_ff(self, x_flat, y):
        # x_flat is (B, 784), overlay concatenates label
        x_pos = self._overlay(x_flat, y, wrong=False)
        x_neg = self._overlay(x_flat, y, wrong=True)
        h_pos, h_neg = x_pos, x_neg
        total_loss = 0
        for i, layer in enumerate(self.layers):
            hp = self._fwd(layer, h_pos)
            hn = self._fwd(layer, h_neg)
            gp = hp.pow(2).mean(dim=1)
            gn = hn.pow(2).mean(dim=1)
            loss = torch.log(1 + torch.exp(
                torch.cat([self.threshold - gp, gn - self.threshold])
            )).mean()
            self.opts[i].zero_grad()
            loss.backward()
            self.opts[i].step()
            total_loss += loss.item()
            h_pos, h_neg = hp.detach(), hn.detach()
        return total_loss


# ============================================================
# TRAINING & EVALUATION
# ============================================================
def evaluate(model, sequential=True, ff_mode=False):
    model.eval()
    correct = total = 0
    eval_loader = test_loader_small if ff_mode else test_loader
    with torch.no_grad():
        for x, y in eval_loader:
            x, y = x.to(device), y.to(device)
            if sequential:
                x_in = x.view(x.size(0), SEQ_LEN, INPUT_DIM)
            else:
                x_in = x.view(x.size(0), -1)

            if ff_mode and sequential:
                x_in = F.pad(x_in, (0, NUM_CLASSES))
                preds = model(x_in)
            elif ff_mode:
                preds = model(x_in)
            else:
                logits = model(x_in)
                preds = logits.argmax(dim=1)

            correct += (preds == y).sum().item()
            total += y.size(0)
            if ff_mode and device.type == 'cuda':
                torch.cuda.empty_cache()
    return correct / total


def run(name, train_fn, epochs=EPOCHS):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    try:
        t0 = time.time()
        hist = train_fn(epochs)
        dt = time.time() - t0
        best = max(hist) if hist else 0
        final = hist[-1] if hist else 0
        status = 'PROMISING' if best > 0.5 else ('WEAK' if best > 0.15 else 'ELIMINATED')
        print(f"  >> Best: {best:.4f} | Final: {final:.4f} | Time: {dt:.1f}s | {status}")
        results[name] = dict(best=best, final=final, time=dt, history=hist, status=status)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"  >> CRASHED: {e}")
        results[name] = dict(best=0, final=0, time=0, history=[], status='CRASHED')


# ---- Training functions ----
def train_bptt(epochs):
    model = MambaBPTT().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    hist = []
    for ep in range(epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            logits = model(x.view(x.size(0), SEQ_LEN, INPUT_DIM))
            loss = F.cross_entropy(logits, y)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        acc = evaluate(model)
        hist.append(acc)
        print(f"    Epoch {ep+1}: {acc:.4f}")
    return hist

def train_ff_baseline(epochs):
    model = PureFF().to(device)
    hist = []
    for ep in range(epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            model.train_ff(x.view(x.size(0), -1), y)
        acc = evaluate(model, sequential=False, ff_mode=True)
        hist.append(acc)
        print(f"    Epoch {ep+1}: {acc:.4f}")
    return hist

def train_mamba_ff(epochs):
    model = MambaFF().to(device)
    hist = []
    for ep in range(epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            x_seq = x.view(x.size(0), SEQ_LEN, INPUT_DIM)
            x_pad = F.pad(x_seq, (0, NUM_CLASSES))  # (B, 28, 38)
            model.train_step(x_pad, y)
        acc = evaluate(model, sequential=True, ff_mode=True)
        hist.append(acc)
        print(f"    Epoch {ep+1}: {acc:.4f}")
    return hist

def train_mamba_pc(epochs):
    model = MambaPC().to(device)
    hist = []
    for ep in range(epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            model.train_step(x.view(x.size(0), SEQ_LEN, INPUT_DIM), y)
        acc = evaluate(model)
        hist.append(acc)
        print(f"    Epoch {ep+1}: {acc:.4f}")
    return hist

def train_mamba_hyb(epochs):
    model = MambaHyb().to(device)
    hist = []
    for ep in range(epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            x_seq = x.view(x.size(0), SEQ_LEN, INPUT_DIM)
            x_pad = F.pad(x_seq, (0, NUM_CLASSES))
            model.train_step(x_pad, y)
        acc = evaluate(model, sequential=True, ff_mode=True)
        hist.append(acc)
        print(f"    Epoch {ep+1}: {acc:.4f}")
    return hist


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print(f"\n{'#'*60}")
    print(f"  MAMBA x FORWARD-FORWARD HYBRID EXPERIMENTS")
    print(f"  Row-Sequential MNIST: {SEQ_LEN} steps x {INPUT_DIM} dims")
    print(f"  d_model={D_MODEL}, d_state={D_STATE}, layers={NUM_LAYERS}")
    print(f"{'#'*60}")

    # Baseline already run: 99.09%
    results["0. Mamba+BPTT (baseline)"] = dict(
        best=0.9909, final=0.9895, time=946.5, history=[
            0.9816,0.9847,0.9854,0.9878,0.9858,0.9860,0.9879,0.9880,
            0.9909,0.9890,0.9891,0.9894,0.9895,0.9887,0.9895
        ], status='PROMISING'
    )
    print("0. Mamba+BPTT: best=0.9909 (cached)")

    run("1. Pure FF (Hinton)", train_ff_baseline)
    run("A. Mamba-FF", train_mamba_ff)
    run("B. Mamba-PC", train_mamba_pc)
    run("C. Mamba-HYB (PC+FF)", train_mamba_hyb)

    # ---- Summary ----
    print(f"\n\n{'='*60}")
    print(f"  FINAL RESULTS")
    print(f"{'='*60}")
    print(f"{'Model':<35} {'Best':>8} {'Final':>8} {'Time':>8} {'Status'}")
    print(f"{'-'*75}")
    for name, r in results.items():
        print(f"{name:<35} {r['best']:>8.4f} {r['final']:>8.4f} {r['time']:>7.1f}s {r['status']}")

    with open('mamba_ff_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to mamba_ff_results.json")
