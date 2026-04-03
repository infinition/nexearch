"""
Round 4: GRADIENT-FREE Local Learning
=======================================
DirectLocal matched backprop — but still uses loss.backward() per layer.
Now we eliminate ALL gradients with forward-only update rules.

3 approaches:
1. ProtoLocal  — class prototypes + contrastive Hebbian (zero gradient)
2. FFLocal     — Forward-Forward goodness but with per-layer probes (zero gradient)
3. InfoLocal   — local mutual information maximization (zero gradient)

If any of these matches DirectLocal (~98% MNIST), we have a TRUE paradigm shift:
  - Zero backward passes anywhere
  - 100% parallel
  - Could run on neuromorphic hardware / FPGAs
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import time

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")
torch.manual_seed(42)
np.random.seed(42)

def get_mnist(bs=256):
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    return (DataLoader(datasets.MNIST('data', True, download=True, transform=t), batch_size=bs, shuffle=True, num_workers=0),
            DataLoader(datasets.MNIST('data', False, transform=t), batch_size=1000, num_workers=0))

def get_cifar10(bs=256):
    t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.4914,0.4822,0.4465),(0.247,0.243,0.261))])
    return (DataLoader(datasets.CIFAR10('data', True, download=True, transform=t), batch_size=bs, shuffle=True, num_workers=0),
            DataLoader(datasets.CIFAR10('data', False, transform=t), batch_size=1000, num_workers=0))

def evaluate(model, loader, flat):
    c, t = 0, 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            if flat: x = x.view(x.size(0), -1)
            c += (model.predict(x).argmax(1) == y).sum().item()
            t += y.size(0)
    return c / t

# =============================================================================
# REFERENCE: DirectLocal (with gradient, from Round 3)
# =============================================================================
class DirectLocalNet(nn.Module):
    def __init__(self, dims, n_classes=10, lr=0.001):
        super().__init__()
        self.layers = nn.ModuleList()
        self.probes = nn.ModuleList()
        self.optimizers = []
        for i in range(len(dims) - 1):
            layer = nn.Sequential(nn.Linear(dims[i], dims[i+1]), nn.ReLU(), nn.BatchNorm1d(dims[i+1]))
            probe = nn.Sequential(nn.Linear(dims[i+1], min(dims[i+1], 128)), nn.ReLU(), nn.Linear(min(dims[i+1], 128), n_classes))
            self.layers.append(layer)
            self.probes.append(probe)
            self.optimizers.append(torch.optim.Adam(list(layer.parameters()) + list(probe.parameters()), lr=lr))

    def forward(self, x):
        for l in self.layers: x = l(x)
        return x

    def predict(self, x):
        h = x
        for l in self.layers: h = l(h)
        return self.probes[-1](h)

    def train_step(self, x, y):
        loss_total, h = 0, x
        for i, (l, p, o) in enumerate(zip(self.layers, self.probes, self.optimizers)):
            h = l(h)
            loss = F.cross_entropy(p(h), y)
            o.zero_grad(); loss.backward(); o.step()
            loss_total += loss.item()
            h = h.detach()
        return loss_total / len(self.layers)

# =============================================================================
# REFERENCE: Backprop
# =============================================================================
class BackpropNet(nn.Module):
    def __init__(self, dims):
        super().__init__()
        layers = []
        for i in range(len(dims)-1):
            layers.append(nn.Linear(dims[i], dims[i+1]))
            if i < len(dims)-2: layers += [nn.ReLU(), nn.BatchNorm1d(dims[i+1])]
        self.net = nn.Sequential(*layers)
        self.opt = torch.optim.Adam(self.parameters(), lr=0.001)

    def forward(self, x): return self.net(x)
    def predict(self, x): return self.forward(x)
    def train_step(self, x, y):
        self.opt.zero_grad()
        loss = F.cross_entropy(self(x), y)
        loss.backward(); self.opt.step()
        return loss.item()

# =============================================================================
# ALGO 1: ProtoLocal — Prototype-Contrastive Local Learning (ZERO GRADIENT)
# =============================================================================
#
# Each layer maintains class prototypes (running mean of activations per class).
# Update rule (100% forward-only):
#   1. Compute activation h = ReLU(W @ x + b)
#   2. Find nearest prototype (same class) and farthest (different class)
#   3. Pull weights toward same-class prototype, push away from others
#   4. dW = lr * x^T @ (proto_same - h) — purely Hebbian, no gradient
#
class ProtoLocalLayer(nn.Module):
    def __init__(self, in_dim, out_dim, n_classes=10, lr=0.01, proto_lr=0.05):
        super().__init__()
        self.w = nn.Parameter(torch.randn(in_dim, out_dim) * np.sqrt(2.0 / in_dim), requires_grad=False)
        self.b = nn.Parameter(torch.zeros(out_dim), requires_grad=False)
        self.n_classes = n_classes
        self.lr = lr
        self.proto_lr = proto_lr

        # Class prototypes: running mean of activations per class
        self.prototypes = nn.Parameter(torch.randn(n_classes, out_dim) * 0.01, requires_grad=False)
        self.proto_counts = torch.zeros(n_classes)

        # Running stats for local normalization
        self.running_mean = torch.zeros(out_dim)
        self.running_var = torch.ones(out_dim)

        # Momentum
        self.w_vel = torch.zeros(in_dim, out_dim)

    def _normalize(self, h):
        """Local batch normalization without gradient."""
        if self.training:
            mean = h.mean(0)
            var = h.var(0, unbiased=False) + 1e-5
            self.running_mean = 0.9 * self.running_mean.to(h.device) + 0.1 * mean
            self.running_var = 0.9 * self.running_var.to(h.device) + 0.1 * var
            return (h - mean) / var.sqrt()
        else:
            return (h - self.running_mean.to(h.device)) / (self.running_var.to(h.device) + 1e-5).sqrt()

    def forward(self, x):
        self.input = x
        pre = x @ self.w + self.b
        self.activation = torch.relu(self._normalize(pre))
        return self.activation

    def update_prototypes(self, h, y):
        """Update class prototypes with exponential moving average."""
        with torch.no_grad():
            for c in range(self.n_classes):
                mask = (y == c)
                if mask.any():
                    class_mean = h[mask].mean(0)
                    self.prototypes.data[c] = (1 - self.proto_lr) * self.prototypes.data[c] + self.proto_lr * class_mean

    def local_update(self, y):
        """ZERO-GRADIENT update: pull toward same-class proto, push from nearest wrong proto."""
        with torch.no_grad():
            h = self.activation
            x = self.input
            B = x.size(0)

            # Get same-class prototype for each sample
            same_proto = self.prototypes.data[y]  # [B, out_dim]

            # Get nearest wrong-class prototype for each sample
            # Compute distances to all prototypes
            dists = torch.cdist(h, self.prototypes.data)  # [B, n_classes]
            # Mask out same class (set to infinity)
            dists[torch.arange(B, device=y.device), y] = float('inf')
            nearest_wrong = dists.argmin(1)  # [B]
            wrong_proto = self.prototypes.data[nearest_wrong]  # [B, out_dim]

            # Contrastive error: we want h to be close to same_proto, far from wrong_proto
            # Pull toward same class
            pull = same_proto - h  # [B, out_dim]
            # Push away from wrong class
            push = h - wrong_proto  # [B, out_dim]
            # Combined signal (weighted)
            error = 0.7 * pull + 0.3 * push  # [B, out_dim]

            # Hebbian weight update: dW = x^T @ error
            dW = x.T @ error / B

            # Momentum
            self.w_vel = self.w_vel.to(dW.device)
            self.w_vel = 0.9 * self.w_vel + dW
            self.w.data += self.lr * self.w_vel
            self.b.data += self.lr * error.mean(0)

            # Update prototypes
            self.update_prototypes(h, y)

            # Weight normalization (keeps scale stable)
            norms = self.w.data.norm(dim=0, keepdim=True)
            self.w.data = self.w.data / (norms + 1e-8) * np.sqrt(self.w.shape[0])

            return (pull ** 2).mean().item()

    def predict_class(self, h):
        """Classify by nearest prototype."""
        dists = torch.cdist(h, self.prototypes.data)
        return dists.argmin(1)


class ProtoLocalNet(nn.Module):
    """Prototype-Contrastive Local Learning — ZERO gradients anywhere."""
    def __init__(self, dims, n_classes=10, lr=0.01):
        super().__init__()
        self.dims = dims
        self.n_classes = n_classes
        self.layers = nn.ModuleList([
            ProtoLocalLayer(dims[i], dims[i+1], n_classes, lr)
            for i in range(len(dims) - 1)
        ])

    def forward(self, x):
        for l in self.layers: x = l(x)
        return x

    def predict(self, x):
        h = x
        for l in self.layers: h = l(h)
        # Use last layer's prototype-based classification
        return -torch.cdist(h, self.layers[-1].prototypes.data)  # Negative distance as logits

    def train_step(self, x, y):
        h = x
        for l in self.layers: h = l(h)
        # Update all layers (parallel — each uses same y)
        total = sum(l.local_update(y) for l in self.layers)
        return total / len(self.layers)

# =============================================================================
# ALGO 2: HebbFF — Hebbian Forward-Forward (ZERO GRADIENT)
# =============================================================================
#
# Like Forward-Forward but using a Hebbian update instead of backward():
#   - Positive examples: strengthen connections (Hebbian)
#   - Negative examples: weaken connections (anti-Hebbian)
#   - No gradient computation at all
#
class HebbFFLayer(nn.Module):
    def __init__(self, in_dim, out_dim, threshold=2.0, lr=0.01):
        super().__init__()
        self.w = nn.Parameter(torch.randn(in_dim, out_dim) * np.sqrt(2.0 / in_dim), requires_grad=False)
        self.b = nn.Parameter(torch.zeros(out_dim), requires_grad=False)
        self.threshold = threshold
        self.lr = lr
        self.w_vel = torch.zeros(in_dim, out_dim)

    def forward(self, x):
        # Normalize input (local operation)
        x_norm = x / (x.norm(dim=1, keepdim=True) + 1e-4)
        return torch.relu(x_norm @ self.w + self.b)

    def goodness(self, h):
        return (h ** 2).sum(dim=1)  # [B]

    def hebbian_update(self, x_pos, x_neg):
        """ZERO-GRADIENT update using Hebbian/anti-Hebbian rule."""
        with torch.no_grad():
            h_pos = self.forward(x_pos)
            h_neg = self.forward(x_neg)

            g_pos = self.goodness(h_pos)  # [B]
            g_neg = self.goodness(h_neg)  # [B]

            B = x_pos.size(0)
            x_pos_n = x_pos / (x_pos.norm(dim=1, keepdim=True) + 1e-4)
            x_neg_n = x_neg / (x_neg.norm(dim=1, keepdim=True) + 1e-4)

            # For positive examples with LOW goodness: strengthen (Hebbian)
            pos_gate = torch.sigmoid(self.threshold - g_pos).unsqueeze(1)  # [B, 1]
            dW_pos = (x_pos_n * pos_gate).T @ (h_pos * pos_gate) / B

            # For negative examples with HIGH goodness: weaken (anti-Hebbian)
            neg_gate = torch.sigmoid(g_neg - self.threshold).unsqueeze(1)  # [B, 1]
            dW_neg = (x_neg_n * neg_gate).T @ (h_neg * neg_gate) / B

            dW = dW_pos - dW_neg

            self.w_vel = self.w_vel.to(dW.device)
            self.w_vel = 0.9 * self.w_vel + dW
            self.w.data += self.lr * self.w_vel
            self.b.data += self.lr * (h_pos * pos_gate - h_neg * neg_gate).mean(0)

            # Weight norm
            norms = self.w.data.norm(dim=0, keepdim=True)
            self.w.data = self.w.data / (norms + 1e-8) * np.sqrt(self.w.shape[0])

            loss = (-torch.log(torch.sigmoid(g_pos - self.threshold) + 1e-8).mean()
                    - torch.log(torch.sigmoid(self.threshold - g_neg) + 1e-8).mean())
            return loss.item(), h_pos, h_neg


class HebbFFNet(nn.Module):
    """Hebbian Forward-Forward — ZERO gradients."""
    def __init__(self, dims, n_classes=10, lr=0.01):
        super().__init__()
        self.n_classes = n_classes
        self.layers = nn.ModuleList([HebbFFLayer(dims[i], dims[i+1], lr=lr) for i in range(len(dims)-1)])

    def _overlay(self, x, y):
        x = x.clone()
        x[:, :self.n_classes] = 0
        x[torch.arange(x.size(0), device=x.device), y] = x.max()
        return x

    def train_step(self, x, y):
        x_pos = self._overlay(x, y)
        y_neg = (y + torch.randint(1, self.n_classes, y.shape, device=y.device)) % self.n_classes
        x_neg = self._overlay(x, y_neg)
        total, hp, hn = 0, x_pos, x_neg
        for layer in self.layers:
            loss, hp, hn = layer.hebbian_update(hp, hn)
            total += loss
        return total / len(self.layers)

    def predict(self, x):
        goodnesses = []
        for label in range(self.n_classes):
            y = torch.full((x.size(0),), label, device=x.device, dtype=torch.long)
            h = self._overlay(x, y)
            g = 0
            for layer in self.layers:
                h = layer(h)
                g = g + layer.goodness(h)
            goodnesses.append(g)
        return torch.stack(goodnesses, dim=1)

# =============================================================================
# ALGO 3: ContrastLocal — Contrastive Prototype + Hebbian Hybrid (ZERO GRADIENT)
# =============================================================================
#
# Best of both worlds: ProtoLocal's prototype idea + HebbFF's contrastive idea
# Each layer:
#   1. Maintains class prototypes
#   2. Uses Forward-Forward goodness as a BONUS signal
#   3. Combined Hebbian update with no gradients
#
class ContrastLocalLayer(nn.Module):
    def __init__(self, in_dim, out_dim, n_classes=10, lr=0.01):
        super().__init__()
        self.w = nn.Parameter(torch.randn(in_dim, out_dim) * np.sqrt(2.0 / in_dim), requires_grad=False)
        self.b = nn.Parameter(torch.zeros(out_dim), requires_grad=False)
        self.n_classes = n_classes
        self.lr = lr
        self.prototypes = nn.Parameter(torch.zeros(n_classes, out_dim), requires_grad=False)
        self.running_mean = torch.zeros(out_dim)
        self.running_var = torch.ones(out_dim)
        self.w_vel = torch.zeros(in_dim, out_dim)
        self.initialized = False

    def _normalize(self, h):
        if self.training:
            m = h.mean(0); v = h.var(0, unbiased=False) + 1e-5
            self.running_mean = 0.9 * self.running_mean.to(h.device) + 0.1 * m
            self.running_var = 0.9 * self.running_var.to(h.device) + 0.1 * v
            return (h - m) / v.sqrt()
        return (h - self.running_mean.to(h.device)) / (self.running_var.to(h.device) + 1e-5).sqrt()

    def forward(self, x):
        self.input = x
        self.activation = torch.relu(self._normalize(x @ self.w + self.b))
        return self.activation

    def local_update(self, y):
        with torch.no_grad():
            h = self.activation
            x = self.input
            B = x.size(0)

            # Initialize prototypes from first batch
            if not self.initialized:
                for c in range(self.n_classes):
                    mask = (y == c)
                    if mask.any():
                        self.prototypes.data[c] = h[mask].mean(0)
                self.initialized = True

            # 1. PROTOTYPE PULL: move toward same-class prototype
            same_proto = self.prototypes.data[y]
            pull = same_proto - h

            # 2. CONTRASTIVE PUSH: move away from nearest wrong-class prototype
            dists = torch.cdist(h, self.prototypes.data)
            dists[torch.arange(B, device=y.device), y] = float('inf')
            nearest_wrong = dists.argmin(1)
            wrong_proto = self.prototypes.data[nearest_wrong]
            push = h - wrong_proto

            # 3. GOODNESS BONUS: encourage high activation norm for correct class
            goodness = (h ** 2).sum(1, keepdim=True)  # [B, 1]
            # Scale factor: if goodness is low, increase the pull
            goodness_gate = torch.sigmoid(2.0 - goodness)  # More pull when goodness is low

            # Combined error signal
            error = (0.6 * pull + 0.3 * push) * (1 + 0.5 * goodness_gate)

            # Hebbian update
            dW = x.T @ error / B
            self.w_vel = self.w_vel.to(dW.device)
            self.w_vel = 0.9 * self.w_vel + dW
            self.w.data += self.lr * self.w_vel
            self.b.data += self.lr * error.mean(0)

            # Update prototypes (EMA)
            for c in range(self.n_classes):
                mask = (y == c)
                if mask.any():
                    self.prototypes.data[c] = 0.95 * self.prototypes.data[c] + 0.05 * h[mask].mean(0)

            # Weight normalization
            norms = self.w.data.norm(dim=0, keepdim=True)
            self.w.data = self.w.data / (norms + 1e-8) * np.sqrt(self.w.shape[0])

            return (pull ** 2).mean().item()


class ContrastLocalNet(nn.Module):
    """Contrastive Prototype + Hebbian — ZERO gradients."""
    def __init__(self, dims, n_classes=10, lr=0.01):
        super().__init__()
        self.n_classes = n_classes
        self.layers = nn.ModuleList([
            ContrastLocalLayer(dims[i], dims[i+1], n_classes, lr) for i in range(len(dims)-1)
        ])

    def forward(self, x):
        for l in self.layers: x = l(x)
        return x

    def predict(self, x):
        h = x
        for l in self.layers: h = l(h)
        return -torch.cdist(h, self.layers[-1].prototypes.data)

    def train_step(self, x, y):
        h = x
        for l in self.layers: h = l(h)
        return sum(l.local_update(y) for l in self.layers) / len(self.layers)


# =============================================================================
# TRAINING
# =============================================================================
def train_and_eval(name, model, train_loader, test_loader, n_epochs, flat):
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
            if flat: x = x.view(x.size(0), -1)
            el += model.train_step(x, y); n += 1
        dt = time.time() - t0
        model.eval()
        acc = evaluate(model, test_loader, flat)
        hist['loss'].append(el/n); hist['acc'].append(acc); hist['time'].append(dt)
        if ep % 5 == 0 or ep == n_epochs-1:
            print(f"  Epoch {ep+1:>2}/{n_epochs} | Loss: {el/n:.4f} | Acc: {acc*100:.2f}% | {dt:.1f}s")
    print(f"  >>> Final: {hist['acc'][-1]*100:.2f}% in {sum(hist['time']):.1f}s")
    return hist


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    train_loader, test_loader = get_mnist(256)
    dims = [784, 500, 300, 10]
    N = 20

    results = {}

    # Baselines
    results['Backprop'] = train_and_eval('Backprop', BackpropNet(dims), train_loader, test_loader, N, True)
    results['DirectLocal'] = train_and_eval('DirectLocal (grad)', DirectLocalNet(dims), train_loader, test_loader, N, True)

    # GRADIENT-FREE algorithms
    results['ProtoLocal'] = train_and_eval('ProtoLocal (0-grad)', ProtoLocalNet(dims, lr=0.01), train_loader, test_loader, N, True)
    results['HebbFF'] = train_and_eval('HebbFF (0-grad)', HebbFFNet([784, 500, 300], lr=0.01), train_loader, test_loader, N, True)
    results['ContrastLocal'] = train_and_eval('ContrastLocal (0-grad)', ContrastLocalNet(dims, lr=0.01), train_loader, test_loader, N, True)

    # Sweep learning rates for best gradient-free algo
    print("\n" + "#"*60)
    print("  LEARNING RATE SWEEP — ContrastLocal")
    print("#"*60)
    for lr in [0.005, 0.02, 0.05]:
        name = f'ContrastLocal lr={lr}'
        results[name] = train_and_eval(name, ContrastLocalNet(dims, lr=lr), train_loader, test_loader, N, True)

    # Wider architecture for best
    print("\n" + "#"*60)
    print("  WIDER ARCHITECTURE — ContrastLocal")
    print("#"*60)
    dims_wide = [784, 1000, 500, 10]
    results['ContrastLocal-Wide'] = train_and_eval('ContrastLocal Wide', ContrastLocalNet(dims_wide, lr=0.01), train_loader, test_loader, N, True)

    # ======================== SUMMARY ========================
    print("\n" + "="*75)
    print("  ROUND 4 FINAL RESULTS — MNIST (20 epochs)")
    print("="*75)
    print(f"  {'Algorithm':<35} {'Accuracy':>10} {'Time':>8} {'Grad?':>8}")
    print("-"*65)

    for k in sorted(results, key=lambda k: results[k]['acc'][-1], reverse=True):
        a = results[k]['acc'][-1] * 100
        t = sum(results[k]['time'])
        grad = 'YES' if k in ['Backprop', 'DirectLocal'] else 'ZERO'
        print(f"  {k:<35} {a:>9.2f}% {t:>7.0f}s {grad:>8}")

    # Best gradient-free
    gf = {k: v for k, v in results.items() if k not in ['Backprop', 'DirectLocal']}
    best_gf = max(gf, key=lambda k: gf[k]['acc'][-1])
    bp_acc = results['Backprop']['acc'][-1] * 100
    gf_acc = gf[best_gf]['acc'][-1] * 100
    print(f"\n  Best gradient-free: {best_gf} ({gf_acc:.2f}%)")
    print(f"  Gap vs Backprop: {bp_acc - gf_acc:.2f}%")
    print(f"  Gap vs DirectLocal: {results['DirectLocal']['acc'][-1]*100 - gf_acc:.2f}%")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    main_keys = ['Backprop', 'DirectLocal', 'ProtoLocal', 'HebbFF', 'ContrastLocal', 'ContrastLocal-Wide']
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    for k, c in zip(main_keys, colors):
        if k in results:
            h = results[k]
            ls = '--' if k in ['Backprop', 'DirectLocal'] else '-'
            lw = 1.5 if k in ['Backprop', 'DirectLocal'] else 2.5
            ax1.plot(range(1, len(h['acc'])+1), [a*100 for a in h['acc']], f'o{ls}', label=k, color=c, linewidth=lw, markersize=3)
    ax1.set_xlabel('Epoch'); ax1.set_ylabel('Test Accuracy (%)'); ax1.set_title('MNIST — Gradient-Free vs Gradient-Based')
    ax1.legend(); ax1.grid(alpha=0.3)

    # Bar chart
    names = [k for k in main_keys if k in results]
    accs = [results[k]['acc'][-1]*100 for k in names]
    cols = ['#e74c3c' if 'Backprop' in k else '#3498db' if 'DirectLocal' in k else '#2ecc71' for k in names]
    ax2.barh(range(len(names)), accs, color=cols)
    ax2.set_yticks(range(len(names))); ax2.set_yticklabels(names)
    ax2.set_xlabel('Accuracy (%)'); ax2.set_title('Final Accuracy Comparison')
    for i, a in enumerate(accs):
        ax2.text(a+0.3, i, f'{a:.1f}%', va='center', fontsize=10)
    ax2.grid(alpha=0.2, axis='x')

    plt.tight_layout()
    plt.savefig('benchmark_round4.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n  Plot saved: benchmark_round4.png")
