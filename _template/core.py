"""
NNN — Solution Name — Core Implementation
============================================
Standalone, importable, reproducible.

Usage:
    python core.py --dataset mnist --epochs 100
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import time
import json
import argparse
import os
import sys

# Use shared benchmarks
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarks'))
from utils import get_dataset, evaluate, count_params, DEVICE

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# YOUR ALGORITHM HERE
# ============================================================
class YourLayer(nn.Module):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        # TODO: implement

    def forward(self, x):
        # TODO: implement
        pass

    @torch.no_grad()
    def local_update(self, x):
        # TODO: implement local learning rule
        pass


class YourNetwork(nn.Module):
    def __init__(self, input_dim=784, num_classes=10):
        super().__init__()
        # TODO: implement
        self.probe = nn.Linear(256, num_classes)  # small supervised head
        self.probe_opt = torch.optim.Adam(self.probe.parameters(), lr=1e-3)

    def train_epoch(self, loader):
        tl = 0
        for x, y in loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            h = x.view(x.size(0), -1)
            # TODO: local updates
            self.probe_opt.zero_grad()
            loss = F.cross_entropy(self.probe(h), y)
            loss.backward(); self.probe_opt.step()
            tl += loss.item()
        return tl / len(loader)

    def evaluate(self, loader):
        self.probe.eval(); c = t = 0
        with torch.no_grad():
            for x, y in loader:
                x, y = x.to(DEVICE), y.to(DEVICE)
                h = x.view(x.size(0), -1)
                # TODO: forward
                c += (self.probe(h).argmax(1) == y).sum().item(); t += y.size(0)
        return c / t


# ============================================================
# CLI
# ============================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='mnist', choices=['mnist', 'cifar10'])
    parser.add_argument('--epochs', type=int, default=100)
    args = parser.parse_args()

    train_loader, test_loader, info = get_dataset(args.dataset)
    model = YourNetwork(input_dim=info['input_dim'], num_classes=info['num_classes']).to(DEVICE)

    print(f"Params: {count_params(model)}")
    best = 0
    for ep in range(1, args.epochs + 1):
        t0 = time.time()
        loss = model.train_epoch(train_loader)
        acc = model.evaluate(test_loader)
        best = max(best, acc)
        if ep <= 10 or ep % 10 == 0 or acc >= best:
            print(f"Ep {ep:3d} | Loss {loss:.4f} | Acc {acc*100:.2f}% | {time.time()-t0:.1f}s", flush=True)

    print(f"\nFINAL BEST: {best*100:.2f}%")
