"""
CPU vs GPU Timing: DirectLocal vs Backprop
============================================
The key promise of local learning: since all layers update independently,
the CPU advantage should grow with depth because:
- Backprop: sequential forward + backward (2N serial ops for N layers)
- DirectLocal: parallel forward + N independent local updates

On CPU, DirectLocal's parallelism should shine.
On GPU, both are fast but backprop has kernel fusion advantage.
"""
import sys
sys.stdout.reconfigure(line_buffering=True)

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.utils.data import DataLoader, TensorDataset
import time

torch.manual_seed(42)
np.random.seed(42)

# =============================================================================
# MODELS
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

    def train_step(self, x, y):
        self.opt.zero_grad()
        loss = F.cross_entropy(self.net(x), y)
        loss.backward()
        self.opt.step()
        return loss.item()


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

    def train_step(self, x, y):
        total_loss, h = 0, x
        for i, (l, p, o) in enumerate(zip(self.layers, self.probes, self.optimizers)):
            h = l(h)
            loss = F.cross_entropy(p(h), y)
            o.zero_grad(); loss.backward(); o.step()
            total_loss += loss.item()
            h = h.detach()
        return total_loss / len(self.layers)


# =============================================================================
# SYNTHETIC DATA (to avoid data loading overhead in timing)
# =============================================================================
def make_synthetic(n_samples=10000, in_dim=784, n_classes=10, batch_size=256):
    X = torch.randn(n_samples, in_dim)
    Y = torch.randint(0, n_classes, (n_samples,))
    return DataLoader(TensorDataset(X, Y), batch_size=batch_size, shuffle=True)


def time_one_epoch(model, loader, dev):
    model = model.to(dev)
    model.train()
    # Warmup
    for x, y in loader:
        x, y = x.to(dev), y.to(dev)
        model.train_step(x, y)
        break

    if dev.type == 'cuda':
        torch.cuda.synchronize()

    t0 = time.time()
    for x, y in loader:
        x, y = x.to(dev), y.to(dev)
        model.train_step(x, y)

    if dev.type == 'cuda':
        torch.cuda.synchronize()

    return time.time() - t0


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    print("="*70)
    print("  CPU vs GPU TIMING — DirectLocal vs Backprop")
    print("="*70)

    configs = [
        ("Shallow (3 layers)", [784, 500, 300, 10]),
        ("Medium (5 layers)", [784, 500, 400, 300, 200, 10]),
        ("Deep (8 layers)", [784, 500, 400, 350, 300, 250, 200, 100, 10]),
        ("Very Deep (12 layers)", [784, 500, 450, 400, 380, 350, 320, 300, 280, 250, 200, 100, 10]),
    ]

    devices = [('CPU', torch.device('cpu'))]
    if torch.cuda.is_available():
        devices.append(('GPU', torch.device('cuda')))

    loader = make_synthetic(10000, 784, 10, 256)

    all_results = []

    for config_name, dims in configs:
        print(f"\n--- {config_name}: {len(dims)-1} layers ---")
        row = {'config': config_name, 'n_layers': len(dims)-1}

        for dev_name, dev in devices:
            # Backprop
            bp = BackpropNet(dims)
            bp_time = time_one_epoch(bp, loader, dev)

            # DirectLocal
            dl = DirectLocalNet(dims)
            dl_time = time_one_epoch(dl, loader, dev)

            ratio = dl_time / bp_time
            row[f'{dev_name}_bp'] = bp_time
            row[f'{dev_name}_dl'] = dl_time
            row[f'{dev_name}_ratio'] = ratio

            print(f"  {dev_name}: Backprop={bp_time:.3f}s  DirectLocal={dl_time:.3f}s  ratio={ratio:.2f}x")

        all_results.append(row)

    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"  {'Config':<25} {'Layers':>6} ", end="")
    for dev_name, _ in devices:
        print(f"| {dev_name+' BP':>8} {dev_name+' DL':>8} {'Ratio':>7}", end="")
    print()
    print("-"*70)
    for r in all_results:
        print(f"  {r['config']:<25} {r['n_layers']:>6} ", end="")
        for dev_name, _ in devices:
            bp = r[f'{dev_name}_bp']
            dl = r[f'{dev_name}_dl']
            ratio = r[f'{dev_name}_ratio']
            print(f"| {bp:>7.3f}s {dl:>7.3f}s {ratio:>6.2f}x", end="")
        print()

    print("""
  INTERPRETATION:
  - ratio < 1.0 = DirectLocal FASTER than backprop
  - ratio > 1.0 = DirectLocal SLOWER than backprop
  - If ratio DECREASES with depth -> local learning scales better

  The key insight: on CPU, DirectLocal should show advantage at depth
  because backprop's sequential backward pass becomes the bottleneck,
  while DirectLocal's per-layer updates are independent.

  Note: In this PyTorch implementation, layers still run sequentially
  because Python is single-threaded. The TRUE advantage would appear with:
  1. Multi-threaded C++ implementation
  2. FPGA/neuromorphic hardware
  3. Multiple CPU cores with one layer per core
    """)
