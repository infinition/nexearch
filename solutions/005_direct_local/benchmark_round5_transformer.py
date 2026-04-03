"""
Round 5: DirectLocal on TRANSFORMERS + HSIC Gradient-Free
==========================================================
Two critical experiments:

1. DirectLocal-Transformer: Can local learning work with attention?
   - Each transformer block has its own probe and optimizer
   - No gradient flows between blocks
   - If this works -> applicable to LLM training

2. HSIC-Local: Hilbert-Schmidt Independence Criterion as local loss
   - HSIC measures statistical dependence WITHOUT gradients through the loss
   - Each layer maximizes HSIC(activations, labels)
   - Known to work better than raw Hebbian (Ma et al., 2020)
"""
import sys
sys.stdout.reconfigure(line_buffering=True)

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import time
import math

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")
torch.manual_seed(42)

def get_mnist(bs=256):
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    return (DataLoader(datasets.MNIST('data', True, download=True, transform=t), batch_size=bs, shuffle=True, num_workers=0),
            DataLoader(datasets.MNIST('data', False, transform=t), batch_size=1000, num_workers=0))

def evaluate(model, loader, preprocess=None):
    c, t = 0, 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            if preprocess: x = preprocess(x)
            c += (model.predict(x).argmax(1) == y).sum().item()
            t += y.size(0)
    return c / t

# =============================================================================
# BACKPROP TRANSFORMER BASELINE
# =============================================================================
class TransformerBlock(nn.Module):
    def __init__(self, d_model, n_heads, ff_dim, dropout=0.1):
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.ff = nn.Sequential(nn.Linear(d_model, ff_dim), nn.GELU(), nn.Linear(ff_dim, d_model))
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        x2 = self.norm1(x)
        x = x + self.drop(self.attn(x2, x2, x2, need_weights=False)[0])
        x = x + self.drop(self.ff(self.norm2(x)))
        return x


class BackpropTransformer(nn.Module):
    """Standard transformer for image classification (ViT-tiny style)."""
    def __init__(self, img_size=28, patch_size=7, d_model=64, n_heads=4, n_blocks=4, n_classes=10):
        super().__init__()
        self.patch_size = patch_size
        n_patches = (img_size // patch_size) ** 2
        patch_dim = patch_size * patch_size  # For grayscale

        self.patch_embed = nn.Linear(patch_dim, d_model)
        self.pos_embed = nn.Parameter(torch.randn(1, n_patches + 1, d_model) * 0.02)
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)

        self.blocks = nn.ModuleList([TransformerBlock(d_model, n_heads, d_model * 4) for _ in range(n_blocks)])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, n_classes)
        self.opt = torch.optim.Adam(self.parameters(), lr=3e-4)

    def _patchify(self, x):
        # x: [B, 1, 28, 28] -> [B, n_patches, patch_dim]
        B = x.size(0)
        p = self.patch_size
        x = x.view(B, 1, 28 // p, p, 28 // p, p)
        x = x.permute(0, 2, 4, 1, 3, 5).reshape(B, -1, p * p)
        return x

    def forward(self, x):
        patches = self._patchify(x)
        B = patches.size(0)
        x = self.patch_embed(patches)
        cls = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls, x], dim=1)
        x = x + self.pos_embed
        for block in self.blocks:
            x = block(x)
        x = self.norm(x[:, 0])  # CLS token
        return self.head(x)

    def predict(self, x): return self.forward(x)

    def train_step(self, x, y):
        self.opt.zero_grad()
        loss = F.cross_entropy(self(x), y)
        loss.backward()
        self.opt.step()
        return loss.item()

# =============================================================================
# DIRECTLOCAL TRANSFORMER
# =============================================================================
class DirectLocalTransformer(nn.Module):
    """Transformer where each block learns independently with its own probe.
    No gradient flows between blocks — each block is a self-contained learner.
    """
    def __init__(self, img_size=28, patch_size=7, d_model=64, n_heads=4, n_blocks=4, n_classes=10, lr=3e-4):
        super().__init__()
        self.patch_size = patch_size
        n_patches = (img_size // patch_size) ** 2
        patch_dim = patch_size * patch_size

        self.patch_embed = nn.Linear(patch_dim, d_model)
        self.pos_embed = nn.Parameter(torch.randn(1, n_patches + 1, d_model) * 0.02)
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)

        self.blocks = nn.ModuleList()
        self.probes = nn.ModuleList()
        self.optimizers = []

        for i in range(n_blocks):
            block = TransformerBlock(d_model, n_heads, d_model * 4)
            # Each block has its own classification probe on CLS token
            probe = nn.Sequential(
                nn.LayerNorm(d_model),
                nn.Linear(d_model, d_model),
                nn.GELU(),
                nn.Linear(d_model, n_classes)
            )
            self.blocks.append(block)
            self.probes.append(probe)

        # Embedding optimizer (shared, trained by first block's loss)
        embed_params = [self.patch_embed.weight, self.patch_embed.bias, self.pos_embed, self.cls_token]
        for i in range(n_blocks):
            block_params = list(self.blocks[i].parameters()) + list(self.probes[i].parameters())
            if i == 0:
                block_params += embed_params
            self.optimizers.append(torch.optim.Adam(block_params, lr=lr))

    def _patchify(self, x):
        B = x.size(0)
        p = self.patch_size
        x = x.view(B, 1, 28 // p, p, 28 // p, p)
        x = x.permute(0, 2, 4, 1, 3, 5).reshape(B, -1, p * p)
        return x

    def forward(self, x):
        patches = self._patchify(x)
        B = patches.size(0)
        x = self.patch_embed(patches)
        cls = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls, x], dim=1) + self.pos_embed
        for block in self.blocks:
            x = block(x)
        return x[:, 0]  # CLS token

    def predict(self, x):
        patches = self._patchify(x)
        B = patches.size(0)
        h = self.patch_embed(patches)
        cls = self.cls_token.expand(B, -1, -1)
        h = torch.cat([cls, h], dim=1) + self.pos_embed
        for block in self.blocks:
            h = block(h)
        return self.probes[-1](h[:, 0])  # Last probe on CLS token

    def train_step(self, x, y):
        patches = self._patchify(x)
        B = patches.size(0)
        h = self.patch_embed(patches)
        cls = self.cls_token.expand(B, -1, -1)
        h = torch.cat([cls, h], dim=1) + self.pos_embed

        total_loss = 0
        for i, (block, probe, opt) in enumerate(zip(self.blocks, self.probes, self.optimizers)):
            h = block(h)
            # Local loss on CLS token
            cls_repr = h[:, 0]
            logits = probe(cls_repr)
            loss = F.cross_entropy(logits, y)
            opt.zero_grad()
            loss.backward(retain_graph=(i < len(self.blocks) - 1))
            opt.step()
            total_loss += loss.item()
            h = h.detach()  # CUT — no gradient between blocks

        return total_loss / len(self.blocks)


# =============================================================================
# HSIC-LOCAL: Gradient-free local learning via kernel independence
# =============================================================================
class HSICLocalLayer(nn.Module):
    """Layer that learns by maximizing HSIC(activations, labels).
    HSIC = Hilbert-Schmidt Independence Criterion.
    Uses a linear kernel for simplicity.

    The weight update is derived analytically from HSIC — NO autograd needed.
    dW = x^T @ (K_y @ h) / B^2  where K_y is the label kernel matrix
    """
    def __init__(self, in_dim, out_dim, n_classes=10, lr=0.01):
        super().__init__()
        self.w = nn.Parameter(torch.randn(in_dim, out_dim) * np.sqrt(2.0 / in_dim), requires_grad=False)
        self.b = nn.Parameter(torch.zeros(out_dim), requires_grad=False)
        self.lr = lr
        self.n_classes = n_classes
        self.w_vel = torch.zeros(in_dim, out_dim)
        self.running_mean = torch.zeros(out_dim)
        self.running_var = torch.ones(out_dim)

    def forward(self, x):
        self.input = x
        pre = x @ self.w + self.b
        if self.training:
            m = pre.mean(0); v = pre.var(0, unbiased=False) + 1e-5
            self.running_mean = 0.9 * self.running_mean.to(x.device) + 0.1 * m
            self.running_var = 0.9 * self.running_var.to(x.device) + 0.1 * v
            pre = (pre - m) / v.sqrt()
        else:
            pre = (pre - self.running_mean.to(x.device)) / (self.running_var.to(x.device) + 1e-5).sqrt()
        self.activation = torch.relu(pre)
        return self.activation

    def hsic_update(self, y):
        """Analytically-derived HSIC gradient — NO autograd."""
        with torch.no_grad():
            h = self.activation  # [B, out]
            x = self.input       # [B, in]
            B = x.size(0)

            # Label kernel: K_y[i,j] = 1 if y[i]==y[j] else 0
            y_onehot = F.one_hot(y, self.n_classes).float()  # [B, C]
            K_y = y_onehot @ y_onehot.T  # [B, B] — same-class kernel

            # Center the kernel
            H = torch.eye(B, device=x.device) - 1.0 / B
            K_y_centered = H @ K_y @ H

            # HSIC gradient w.r.t. activations:
            # d(HSIC)/dh = (2/B^2) * K_y_centered @ h
            dh = (2.0 / (B * B)) * K_y_centered @ h  # [B, out]

            # Chain to weights via Hebbian: dW = x^T @ dh
            dW = x.T @ dh / B

            # Momentum
            self.w_vel = self.w_vel.to(dW.device)
            self.w_vel = 0.9 * self.w_vel + dW
            self.w.data += self.lr * self.w_vel
            self.b.data += self.lr * dh.mean(0)

            # Weight norm
            norms = self.w.data.norm(dim=0, keepdim=True)
            self.w.data = self.w.data / (norms + 1e-8) * np.sqrt(self.w.shape[0])

            # HSIC value for monitoring
            K_h = h @ h.T  # Linear kernel on activations
            hsic = (K_y_centered * (H @ K_h @ H)).sum() / (B * B)
            return hsic.item()


class HSICLocalNet(nn.Module):
    """HSIC-based local learning — analytically derived, ZERO autograd."""
    def __init__(self, dims, n_classes=10, lr=0.01):
        super().__init__()
        self.n_classes = n_classes
        self.layers = nn.ModuleList([
            HSICLocalLayer(dims[i], dims[i+1], n_classes, lr)
            for i in range(len(dims) - 1)
        ])
        # Lightweight readout (trained with a simple delta rule, no autograd)
        self.readout_w = nn.Parameter(torch.randn(dims[-1], n_classes) * 0.01, requires_grad=False)
        self.readout_b = nn.Parameter(torch.zeros(n_classes), requires_grad=False)

    def forward(self, x):
        for l in self.layers: x = l(x)
        return x

    def predict(self, x):
        h = x
        for l in self.layers: h = l(h)
        return h @ self.readout_w + self.readout_b

    def train_step(self, x, y):
        # Forward
        h = x
        for l in self.layers: h = l(h)

        # HSIC updates (zero gradient, fully local)
        total_hsic = sum(l.hsic_update(y) for l in self.layers)

        # Update readout with delta rule (also gradient-free)
        with torch.no_grad():
            logits = h @ self.readout_w + self.readout_b
            probs = F.softmax(logits, dim=1)
            target = F.one_hot(y, self.n_classes).float()
            error = target - probs  # [B, C]
            self.readout_w.data += 0.01 * h.T @ error / x.size(0)
            self.readout_b.data += 0.01 * error.mean(0)

        return -total_hsic / len(self.layers)  # Negative HSIC as "loss"


# =============================================================================
# HSIC + PROBE HYBRID: HSIC for features, local gradient for readout
# =============================================================================
class HSICProbeNet(nn.Module):
    """Hybrid: HSIC (zero-grad) for feature layers + local gradient probes for readout."""
    def __init__(self, dims, n_classes=10, hsic_lr=0.01, probe_lr=0.001):
        super().__init__()
        self.n_classes = n_classes
        self.layers = nn.ModuleList([
            HSICLocalLayer(dims[i], dims[i+1], n_classes, hsic_lr)
            for i in range(len(dims) - 1)
        ])
        # Per-layer probes (with gradient, but local only)
        self.probes = nn.ModuleList([
            nn.Sequential(nn.Linear(dims[i+1], n_classes))
            for i in range(len(dims) - 1)
        ])
        self.probe_opts = [torch.optim.Adam(p.parameters(), lr=probe_lr) for p in self.probes]

    def forward(self, x):
        for l in self.layers: x = l(x)
        return x

    def predict(self, x):
        h = x
        for l in self.layers: h = l(h)
        return self.probes[-1](h)

    def train_step(self, x, y):
        # Forward
        h = x
        for l in self.layers: h = l(h)

        # HSIC updates for feature layers (ZERO gradient)
        for l in self.layers:
            l.hsic_update(y)

        # Probe updates (local gradient only, for readout accuracy)
        total_loss = 0
        h = x
        for i, (l, p, o) in enumerate(zip(self.layers, self.probes, self.probe_opts)):
            h = l(h).detach()  # HSIC already updated weights, just forward
            logits = p(h)
            loss = F.cross_entropy(logits, y)
            o.zero_grad(); loss.backward(); o.step()
            total_loss += loss.item()

        return total_loss / len(self.layers)


# =============================================================================
# REFERENCE: MLP DirectLocal
# =============================================================================
class DirectLocalMLP(nn.Module):
    def __init__(self, dims, n_classes=10, lr=0.001):
        super().__init__()
        self.layers = nn.ModuleList()
        self.probes = nn.ModuleList()
        self.optimizers = []
        for i in range(len(dims) - 1):
            layer = nn.Sequential(nn.Linear(dims[i], dims[i+1]), nn.ReLU(), nn.BatchNorm1d(dims[i+1]))
            probe = nn.Sequential(nn.Linear(dims[i+1], min(dims[i+1],128)), nn.ReLU(), nn.Linear(min(dims[i+1],128), n_classes))
            self.layers.append(layer); self.probes.append(probe)
            self.optimizers.append(torch.optim.Adam(list(layer.parameters())+list(probe.parameters()), lr=lr))

    def predict(self, x):
        h = x
        for l in self.layers: h = l(h)
        return self.probes[-1](h)

    def train_step(self, x, y):
        total, h = 0, x
        for i, (l, p, o) in enumerate(zip(self.layers, self.probes, self.optimizers)):
            h = l(h); loss = F.cross_entropy(p(h), y)
            o.zero_grad(); loss.backward(); o.step()
            total += loss.item(); h = h.detach()
        return total / len(self.layers)

class BackpropMLP(nn.Module):
    def __init__(self, dims):
        super().__init__()
        layers = []
        for i in range(len(dims)-1):
            layers.append(nn.Linear(dims[i], dims[i+1]))
            if i < len(dims)-2: layers += [nn.ReLU(), nn.BatchNorm1d(dims[i+1])]
        self.net = nn.Sequential(*layers)
        self.opt = torch.optim.Adam(self.parameters(), lr=0.001)
    def predict(self, x): return self.net(x)
    def train_step(self, x, y):
        self.opt.zero_grad(); loss = F.cross_entropy(self.net(x), y)
        loss.backward(); self.opt.step(); return loss.item()


# =============================================================================
# TRAINING
# =============================================================================
def train_and_eval(name, model, train_loader, test_loader, n_epochs, preprocess=None):
    model = model.to(device)
    hist = {'loss': [], 'acc': [], 'time': []}
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    for ep in range(n_epochs):
        t0 = time.time()
        model.train()
        el, n = 0, 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            if preprocess: x = preprocess(x)
            el += model.train_step(x, y); n += 1
        dt = time.time() - t0
        model.eval()
        acc = evaluate(model, test_loader, preprocess)
        hist['loss'].append(el/n); hist['acc'].append(acc); hist['time'].append(dt)
        if ep % 3 == 0 or ep == n_epochs-1:
            print(f"  Epoch {ep+1:>2}/{n_epochs} | Loss: {el/n:.4f} | Acc: {acc*100:.2f}% | {dt:.1f}s")
    print(f"  >>> Final: {hist['acc'][-1]*100:.2f}% in {sum(hist['time']):.1f}s")
    return hist


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    train_loader, test_loader = get_mnist(256)
    N = 15

    results = {}
    flatten = lambda x: x.view(x.size(0), -1)

    # ---- MLP BASELINES ----
    print("\n" + "#"*60)
    print("  PART 1: MLP — Backprop vs DirectLocal vs HSIC")
    print("#"*60)
    dims = [784, 500, 300, 10]
    results['MLP-Backprop'] = train_and_eval('MLP Backprop', BackpropMLP(dims), train_loader, test_loader, N, flatten)
    results['MLP-DirectLocal'] = train_and_eval('MLP DirectLocal', DirectLocalMLP(dims), train_loader, test_loader, N, flatten)
    results['MLP-HSIC'] = train_and_eval('MLP HSIC (0-grad)', HSICLocalNet(dims, lr=0.01), train_loader, test_loader, N, flatten)
    results['MLP-HSIC-Probe'] = train_and_eval('MLP HSIC+Probe (hybrid)', HSICProbeNet(dims, hsic_lr=0.01, probe_lr=0.001), train_loader, test_loader, N, flatten)

    # ---- TRANSFORMER ----
    print("\n" + "#"*60)
    print("  PART 2: TRANSFORMER — Backprop vs DirectLocal")
    print("#"*60)
    results['TF-Backprop'] = train_and_eval('Transformer Backprop', BackpropTransformer(n_blocks=4, d_model=64), train_loader, test_loader, N)
    results['TF-DirectLocal'] = train_and_eval('Transformer DirectLocal', DirectLocalTransformer(n_blocks=4, d_model=64), train_loader, test_loader, N)

    # Deeper transformer
    results['TF-Deep-Backprop'] = train_and_eval('Transformer Deep BP (8 blocks)', BackpropTransformer(n_blocks=8, d_model=64), train_loader, test_loader, N)
    results['TF-Deep-DirectLocal'] = train_and_eval('Transformer Deep DL (8 blocks)', DirectLocalTransformer(n_blocks=8, d_model=64), train_loader, test_loader, N)

    # ======================== SUMMARY ========================
    print("\n" + "="*75)
    print("  ROUND 5 FINAL RESULTS — MNIST")
    print("="*75)

    sections = [
        ("MLP", ['MLP-Backprop', 'MLP-DirectLocal', 'MLP-HSIC', 'MLP-HSIC-Probe']),
        ("Transformer (4 blocks)", ['TF-Backprop', 'TF-DirectLocal']),
        ("Transformer (8 blocks)", ['TF-Deep-Backprop', 'TF-Deep-DirectLocal']),
    ]

    for sec_name, keys in sections:
        print(f"\n  --- {sec_name} ---")
        print(f"  {'Algorithm':<35} {'Acc':>8} {'Time':>7} {'Type':>12}")
        print("  " + "-"*65)
        for k in keys:
            a = results[k]['acc'][-1]*100
            t = sum(results[k]['time'])
            typ = 'GLOBAL BP' if 'Backprop' in k else ('ZERO GRAD' if 'HSIC' in k and 'Probe' not in k else 'LOCAL GRAD')
            print(f"  {k:<35} {a:>7.2f}% {t:>6.0f}s {typ:>12}")
