"""
DirectLocal Learning - Core Implementation
============================================
Each layer has its own classifier probe and optimizer.
Gradient NEVER flows between layers (h.detach()).
All layers train in parallel.

Usage:
    python core.py              # Train on MNIST
    python core.py --cifar10    # Train on CIFAR-10
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import time
import argparse

def get_device():
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# =============================================================================
# DIRECTLOCAL v2 - The winning algorithm
# =============================================================================
class DirectLocalNet(nn.Module):
    """Each layer learns independently with its own classifier probe.
    Gradient NEVER flows between layers - each layer is updated in isolation.
    """
    def __init__(self, dims, n_classes=10, lr=0.001, dropout=0.1):
        super().__init__()
        self.n_classes = n_classes
        self.layers = nn.ModuleList()
        self.probes = nn.ModuleList()
        self.optimizers = []

        for i in range(len(dims) - 1):
            layer = nn.Sequential(
                nn.Linear(dims[i], dims[i+1]),
                nn.ReLU(),
                nn.BatchNorm1d(dims[i+1]),
                nn.Dropout(dropout)
            )
            probe = nn.Sequential(
                nn.Linear(dims[i+1], min(dims[i+1], 128)),
                nn.ReLU(),
                nn.Linear(min(dims[i+1], 128), n_classes)
            )
            self.layers.append(layer)
            self.probes.append(probe)
            self.optimizers.append(torch.optim.Adam(
                list(layer.parameters()) + list(probe.parameters()), lr=lr
            ))

    def forward(self, x):
        h = x
        for layer in self.layers:
            h = layer(h)
        return h

    def predict(self, x):
        self.eval()
        h = x
        for layer in self.layers:
            h = layer(h)
        return self.probes[-1](h)

    def train_step(self, x, y):
        total_loss = 0
        h = x
        for i, (layer, probe, opt) in enumerate(zip(self.layers, self.probes, self.optimizers)):
            h = layer(h)
            logits = probe(h)
            loss = F.cross_entropy(logits, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total_loss += loss.item()
            h = h.detach()  # THE KEY: cut gradient between layers
        return total_loss / len(self.layers)


# =============================================================================
# DIRECTLOCAL TRANSFORMER
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


class DirectLocalTransformer(nn.Module):
    """Transformer where each block learns independently."""
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
            probe = nn.Sequential(nn.LayerNorm(d_model), nn.Linear(d_model, d_model), nn.GELU(), nn.Linear(d_model, n_classes))
            self.blocks.append(block)
            self.probes.append(probe)
            params = list(block.parameters()) + list(probe.parameters())
            if i == 0:
                params += [self.patch_embed.weight, self.patch_embed.bias, self.pos_embed, self.cls_token]
            self.optimizers.append(torch.optim.Adam(params, lr=lr))

    def _patchify(self, x):
        B = x.size(0)
        p = self.patch_size
        x = x.view(B, 1, 28 // p, p, 28 // p, p)
        return x.permute(0, 2, 4, 1, 3, 5).reshape(B, -1, p * p)

    def predict(self, x):
        patches = self._patchify(x)
        B = patches.size(0)
        h = self.patch_embed(patches)
        h = torch.cat([self.cls_token.expand(B, -1, -1), h], dim=1) + self.pos_embed
        for block in self.blocks:
            h = block(h)
        return self.probes[-1](h[:, 0])

    def train_step(self, x, y):
        patches = self._patchify(x)
        B = patches.size(0)
        h = self.patch_embed(patches)
        h = torch.cat([self.cls_token.expand(B, -1, -1), h], dim=1) + self.pos_embed
        total_loss = 0
        for i, (block, probe, opt) in enumerate(zip(self.blocks, self.probes, self.optimizers)):
            h = block(h)
            logits = probe(h[:, 0])
            loss = F.cross_entropy(logits, y)
            opt.zero_grad()
            loss.backward(retain_graph=(i < len(self.blocks) - 1))
            opt.step()
            total_loss += loss.item()
            h = h.detach()
        return total_loss / len(self.blocks)


# =============================================================================
# TRAINING
# =============================================================================
def evaluate(model, test_loader, device, preprocess=None):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            if preprocess: x = preprocess(x)
            pred = model.predict(x)
            correct += (pred.argmax(1) == y).sum().item()
            total += y.size(0)
    return correct / total


def train(model, train_loader, test_loader, n_epochs, device, preprocess=None):
    model = model.to(device)
    for epoch in range(n_epochs):
        model.train()
        total_loss, n = 0, 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            if preprocess: x = preprocess(x)
            total_loss += model.train_step(x, y)
            n += 1
        model.eval()
        acc = evaluate(model, test_loader, device, preprocess)
        print(f"  Epoch {epoch+1}/{n_epochs} | Loss: {total_loss/n:.4f} | Acc: {acc*100:.2f}%")
    return acc


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cifar10', action='store_true')
    parser.add_argument('--transformer', action='store_true')
    parser.add_argument('--epochs', type=int, default=15)
    args = parser.parse_args()

    device = get_device()
    print(f"Device: {device}")
    torch.manual_seed(42)

    if args.cifar10:
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.4914,0.4822,0.4465),(0.247,0.243,0.261))])
        train_loader = DataLoader(datasets.CIFAR10('data', True, download=True, transform=t), batch_size=256, shuffle=True)
        test_loader = DataLoader(datasets.CIFAR10('data', False, transform=t), batch_size=1000)
        dims = [3072, 2000, 1000, 500, 10]
        model = DirectLocalNet(dims, lr=0.001, dropout=0.2)
        preprocess = lambda x: x.view(x.size(0), -1)
    elif args.transformer:
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        train_loader = DataLoader(datasets.MNIST('data', True, download=True, transform=t), batch_size=256, shuffle=True)
        test_loader = DataLoader(datasets.MNIST('data', False, transform=t), batch_size=1000)
        model = DirectLocalTransformer(n_blocks=8, d_model=64)
        preprocess = None
    else:
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        train_loader = DataLoader(datasets.MNIST('data', True, download=True, transform=t), batch_size=256, shuffle=True)
        test_loader = DataLoader(datasets.MNIST('data', False, transform=t), batch_size=1000)
        dims = [784, 500, 300, 10]
        model = DirectLocalNet(dims)
        preprocess = lambda x: x.view(x.size(0), -1)

    print(f"\nTraining DirectLocal {'Transformer' if args.transformer else 'MLP'}...")
    acc = train(model, train_loader, test_loader, args.epochs, device, preprocess)
    print(f"\nFinal accuracy: {acc*100:.2f}%")
