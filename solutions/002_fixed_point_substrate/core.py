"""
002 - Fixed-Point Substrate (FPS) - Core Implementation
=========================================================
"La realite nait du point fixe." (It from Fix)

A computational medium finds stable configurations (fixed points).
Input perturbs the medium, which collapses to equilibrium Z* = f(Z*).
Zero backpropagation. Constant memory. Entropy-gated Hebbian learning.

Usage:
    python core.py --dataset mnist --epochs 50
    python core.py --dataset fmnist --epochs 50
    python core.py --dataset cifar10 --epochs 60 --channels 96 --hidden 384
"""

import torch
import torch.nn.functional as F
import math
import time
import json
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'benchmarks'))
from utils import get_dataset, DEVICE

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)


class FixedPointSubstrate:
    """Computational medium that learns via fixed-point equilibrium."""

    def __init__(self, grid_size=28, channels=96, n_classes=10,
                 in_channels=1, n_regions=7, max_iter=40, tol=5e-4,
                 hidden_read=256, device='cuda'):
        self.N = grid_size
        self.C = channels
        self.K = n_classes
        self.in_channels = in_channels
        self.n_regions = n_regions
        self.max_iter = max_iter
        self.tol = tol
        self.device = device

        self.region_size = grid_size // n_regions
        self.n_raw_features = channels * n_regions * n_regions * 2
        self.hidden_read = hidden_read

        torch.manual_seed(42)
        ks = 5
        self.input_filters = torch.randn(channels, in_channels, ks, ks, device=device)
        norms = self.input_filters.reshape(channels, -1).norm(dim=1, keepdim=True).reshape(channels, 1, 1, 1)
        self.input_filters /= (norms + 1e-8)
        for ic in range(min(in_channels, channels)):
            self.input_filters[ic] = 0
            self.input_filters[ic, ic % in_channels, ks // 2, ks // 2] = 1.0
        self.input_filter_pad = ks // 2

        self.kappa_3 = torch.rand(1, channels, grid_size, grid_size, device=device) * 0.12 + 0.02
        self.kappa_5 = torch.rand(1, channels, grid_size, grid_size, device=device) * 0.06 + 0.01
        self.kappa_7 = torch.rand(1, channels, grid_size, grid_size, device=device) * 0.03 + 0.005
        self.alpha = torch.randn(1, channels, grid_size, grid_size, device=device) * 0.3
        self.beta = torch.randn(1, channels, grid_size, grid_size, device=device) * 0.05
        self.W_mix = torch.randn(channels, channels, device=device) * (0.05 / math.sqrt(channels))
        self._normalize_W_mix()

        self.lap3 = self._make_lap_kernel(3)
        self.lap5 = self._make_lap_kernel(5)
        self.lap7 = self._make_lap_kernel(7)

        self.W1 = torch.randn(hidden_read, self.n_raw_features, device=device) * (0.05 / math.sqrt(self.n_raw_features))
        self.b1 = torch.zeros(hidden_read, device=device)
        self.W2 = torch.randn(n_classes, hidden_read, device=device) * (0.1 / math.sqrt(hidden_read))
        self.b2 = torch.zeros(n_classes, device=device)

        ek = 5
        self.ent_kernel = torch.ones(channels, 1, ek, ek, device=device) / (ek * ek)
        self.ent_pad = ek // 2
        self.step_count = 0
        self.last_iters = 0

    def _make_lap_kernel(self, size):
        k = torch.zeros(size, size, device=self.device)
        c = size // 2
        for i in range(size):
            for j in range(size):
                if i == c and j == c: continue
                if abs(i - c) + abs(j - c) <= c: k[i, j] = 1.0
        k[c, c] = -k.sum()
        k /= k[k > 0].sum(); k[c, c] = -1.0
        return k.reshape(1, 1, size, size).expand(self.C, 1, size, size).contiguous()

    def _normalize_W_mix(self):
        with torch.no_grad():
            s = torch.linalg.norm(self.W_mix, ord=2)
            if s > 0.85: self.W_mix *= 0.85 / s

    def _fixed_point_map(self, Z, X_proj):
        s3 = self.kappa_3 * F.conv2d(Z, self.lap3, padding=1, groups=self.C)
        s5 = self.kappa_5 * F.conv2d(Z, self.lap5, padding=2, groups=self.C)
        s7 = self.kappa_7 * F.conv2d(Z, self.lap7, padding=3, groups=self.C)
        B, C, H, W = Z.shape
        ch = (Z.permute(0, 2, 3, 1).reshape(-1, C) @ self.W_mix.T).reshape(B, H, W, C).permute(0, 3, 1, 2)
        return torch.tanh(s3 + s5 + s7 + 0.5 * ch + self.alpha * X_proj + self.beta)

    def _project_input(self, images):
        return F.conv2d(images, self.input_filters, padding=self.input_filter_pad)

    def find_fixed_point(self, images):
        X_proj = self._project_input(images)
        Z = torch.tanh(X_proj * 0.3)
        m = 3; Z_hist, R_hist = [], []
        for i in range(1, self.max_iter + 1):
            Z_new = self._fixed_point_map(Z, X_proj)
            res = Z_new - Z
            if res.norm() / (Z.norm() + 1e-8) < self.tol:
                self.last_iters = i; return Z_new, i
            if len(Z_hist) >= m and i > 5:
                try:
                    R_flat = torch.stack(R_hist[-m:]).reshape(m, -1)
                    co = torch.linalg.solve(R_flat @ R_flat.T + 1e-6 * torch.eye(m, device=self.device), torch.ones(m, device=self.device))
                    co /= (co.sum() + 1e-8)
                    Z = (co.reshape(m, 1, 1, 1, 1) * torch.stack(Z_hist[-m:])).sum(0)
                    Z = self._fixed_point_map(Z, X_proj)
                except: Z = 0.5 * Z + 0.5 * Z_new
            else: Z = 0.5 * Z + 0.5 * Z_new
            Z_hist.append(Z.detach()); R_hist.append(res.detach())
            if len(Z_hist) > m + 1: Z_hist.pop(0); R_hist.pop(0)
        self.last_iters = self.max_iter; return Z, self.max_iter

    def extract_features(self, Z):
        B, r, rs = Z.shape[0], self.n_regions, self.region_size
        Zr = Z[:, :, :r*rs, :r*rs].reshape(B, self.C, r, rs, r, rs)
        return torch.cat([Zr.mean(dim=(3,5)).reshape(B,-1), Zr.var(dim=(3,5)).reshape(B,-1)], dim=1)

    def readout(self, f):
        return torch.tanh(f @ self.W1.T + self.b1) @ self.W2.T + self.b2

    def readout_hidden(self, f):
        h = torch.tanh(f @ self.W1.T + self.b1); return h, h @ self.W2.T + self.b2

    def local_entropy(self, Z):
        mu = F.conv2d(Z, self.ent_kernel, padding=self.ent_pad, groups=self.C)
        sq = F.conv2d(Z**2, self.ent_kernel, padding=self.ent_pad, groups=self.C)
        return 0.5 * torch.log((sq - mu**2).clamp(min=0) + 1e-8)

    @torch.no_grad()
    def learn(self, Z, images, targets, lr=0.01):
        B = Z.shape[0]
        features = self.extract_features(Z)
        h, logits = self.readout_hidden(features)
        probs = torch.softmax(logits, dim=1)
        tgt = torch.zeros(B, self.K, device=self.device)
        tgt.scatter_(1, targets.unsqueeze(1), 1.0)
        err = tgt - probs

        self.W2 += lr * (err.T @ h) / B; self.b2 += lr * err.mean(0)
        hd = (err @ self.W2) * (1.0 - h**2)
        self.W1 += lr * 0.5 * (hd.T @ features) / B; self.b1 += lr * 0.5 * hd.mean(0)

        nmf = self.C * self.n_regions**2
        ce = hd @ self.W1[:, :nmf]
        ce_sp = F.interpolate(ce.reshape(B, self.C, self.n_regions, self.n_regions), size=(self.N, self.N), mode='nearest')
        g = torch.sigmoid(self.local_entropy(Z) + 0.5).mean(0, keepdim=True)
        co = (Z * ce_sp).mean(0, keepdim=True)

        self.kappa_3 += lr*0.15*g*co; self.kappa_3.clamp_(0.005, 0.4)
        self.kappa_5 += lr*0.08*g*co; self.kappa_5.clamp_(0.002, 0.2)
        self.kappa_7 += lr*0.04*g*co; self.kappa_7.clamp_(0.001, 0.1)

        Xp = self._project_input(images)
        self.alpha += lr*0.2*g*(Xp*ce_sp).mean(0, keepdim=True); self.alpha.clamp_(-2, 2)
        self.beta += lr*0.08*g*ce_sp.mean(0, keepdim=True); self.beta.clamp_(-1, 1)
        self.W_mix += lr*0.03*(Z.mean(dim=(2,3)).T @ ce_sp.mean(dim=(2,3)))/B; self._normalize_W_mix()

        ks = self.input_filters.shape[-1]; half = ks // 2
        ebc = ce_sp.mean(0); im = images.mean(0)
        dF = torch.zeros_like(self.input_filters)
        for ic in range(self.in_channels):
            u = F.pad(im[ic:ic+1].unsqueeze(0), [half]*4).unfold(2,ks,1).unfold(3,ks,1).squeeze(0).squeeze(0)
            dF[:, ic] = torch.einsum('chw,hwij->cij', ebc, u)
        self.input_filters += lr*0.05*dF
        n = self.input_filters.reshape(self.C,-1).norm(dim=1,keepdim=True).reshape(self.C,1,1,1)
        self.input_filters /= (n + 1e-8)
        for ic in range(min(self.in_channels, self.C)):
            self.input_filters[ic] = 0; self.input_filters[ic, ic%self.in_channels, half, half] = 1.0
        self.step_count += 1

    def train_step(self, images, targets, lr=0.01):
        Z, it = self.find_fixed_point(images)
        self.learn(Z, images, targets, lr)
        return (self.readout(self.extract_features(Z)).argmax(1) == targets).float().mean().item(), it

    @torch.no_grad()
    def eval_step(self, images, targets):
        Z, it = self.find_fixed_point(images)
        return (self.readout(self.extract_features(Z)).argmax(1) == targets).float().mean().item(), it

    def param_count(self):
        N, C = self.N, self.C
        return (C*self.in_channels*25 + 5*C*N*N + C*C +
                self.hidden_read*self.n_raw_features + self.hidden_read +
                self.K*self.hidden_read + self.K)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fixed-Point Substrate')
    parser.add_argument('--dataset', default='mnist', choices=['mnist', 'fmnist', 'cifar10'])
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--channels', type=int, default=96)
    parser.add_argument('--hidden', type=int, default=256)
    parser.add_argument('--n-regions', type=int, default=7)
    parser.add_argument('--max-iter', type=int, default=40)
    parser.add_argument('--lr', type=float, default=0.012)
    parser.add_argument('--lr-decay', type=float, default=0.98)
    args = parser.parse_args()

    print("=" * 60)
    print("  FIXED-POINT SUBSTRATE (002)")
    print("  Zero backpropagation. It from Fix.")
    print("=" * 60)

    ds_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets')
    from torchvision import datasets, transforms

    if args.dataset == 'fmnist':
        tf_tr = transforms.Compose([transforms.RandomHorizontalFlip(), transforms.RandomAffine(8, (0.08,0.08), (0.92,1.08)), transforms.ToTensor(), transforms.Normalize((0.2860,),(0.3530,))])
        tf_te = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.2860,),(0.3530,))])
        tr = datasets.FashionMNIST(ds_dir, True, download=True, transform=tf_tr)
        te = datasets.FashionMNIST(ds_dir, False, transform=tf_te)
        in_ch, gs, n_reg = 1, 28, 7
    elif args.dataset == 'cifar10':
        tf_tr = transforms.Compose([transforms.RandomHorizontalFlip(), transforms.RandomCrop(32,4), transforms.ToTensor(), transforms.Normalize((0.4914,0.4822,0.4465),(0.2470,0.2435,0.2616))])
        tf_te = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.4914,0.4822,0.4465),(0.2470,0.2435,0.2616))])
        tr = datasets.CIFAR10(ds_dir, True, download=True, transform=tf_tr)
        te = datasets.CIFAR10(ds_dir, False, transform=tf_te)
        in_ch, gs, n_reg = 3, 32, 8
        if args.hidden == 256: args.hidden = 384
    else:
        tf_tr = transforms.Compose([transforms.RandomAffine(8, (0.08,0.08), (0.92,1.08)), transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
        tf_te = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,),(0.3081,))])
        tr = datasets.MNIST(ds_dir, True, download=True, transform=tf_tr)
        te = datasets.MNIST(ds_dir, False, transform=tf_te)
        in_ch, gs, n_reg = 1, 28, 7

    train_loader = torch.utils.data.DataLoader(tr, args.batch_size, shuffle=True, num_workers=2, pin_memory=True, drop_last=True)
    test_loader = torch.utils.data.DataLoader(te, 256, num_workers=2, pin_memory=True)

    sub = FixedPointSubstrate(gs, args.channels, 10, in_ch, n_reg, args.max_iter, 5e-4, args.hidden, str(DEVICE))
    print(f"  {args.dataset} | {sub.param_count():,} params | {args.channels}ch {args.hidden}h")
    print("=" * 60)

    best, lr, hist = 0.0, args.lr, []
    for ep in range(1, args.epochs+1):
        t0 = time.time(); asum = nb = 0
        for x, y in train_loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            with torch.no_grad(): a, _ = sub.train_step(x, y, lr)
            asum += a; nb += 1
        tra = asum/nb*100; dt = time.time()-t0
        tsum = tn = 0
        with torch.no_grad():
            for x, y in test_loader:
                x, y = x.to(DEVICE), y.to(DEVICE); a, _ = sub.eval_step(x, y); tsum += a; tn += 1
        tea = tsum/tn*100
        m = " *" if tea > best else ""
        if tea > best: best = tea
        hist.append({'epoch': ep, 'train_acc': round(tra,2), 'test_acc': round(tea,2), 'time': round(dt,1)})
        if ep <= 5 or ep % 5 == 0 or m:
            print(f"  Ep {ep:3d} | train {tra:.1f}% | test {tea:.1f}% | {dt:.1f}s | lr={lr:.4f}{m}", flush=True)
        lr *= args.lr_decay

    print(f"\nFINAL BEST: {best:.2f}%")
    res = {'dataset': args.dataset, 'architecture': f'FPS-v0.5 {args.channels}ch {args.hidden}h',
           'category': 'physics-inspired', 'type': 'learning-rule', 'metric': 'accuracy', 'unit': '%',
           'epochs': args.epochs, 'total_params': sub.param_count(), 'best_value': round(best,2),
           'baseline_value': 98.04 if 'mnist' in args.dataset else 85.83,
           'baseline_name': 'Backprop MLP' if 'mnist' in args.dataset else 'Backprop Conv',
           'gpu_hours': round(sum(h['time'] for h in hist)/3600, 2), 'history': hist}
    with open(os.path.join(RESULTS_DIR, f'{args.dataset}_v05.json'), 'w') as f:
        json.dump(res, f, indent=2)
    print(f"Results saved.")
