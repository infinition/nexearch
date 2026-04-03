"""
Mono-Forward Learning - Core Implementation
=============================================
Based on arXiv:2501.09238 (Auckland, January 2025).
Each layer classifies via projection matrix M.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class MonoForwardLayer(nn.Module):
    def __init__(self, in_dim, out_dim, n_classes=10, lr=0.01):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)
        nn.init.kaiming_normal_(self.linear.weight)
        self.bn = nn.BatchNorm1d(out_dim)
        self.M = nn.Linear(out_dim, n_classes, bias=False)
        self.opt = torch.optim.Adam(
            list(self.linear.parameters()) + [self.bn.weight, self.bn.bias] + list(self.M.parameters()), lr=lr)

    def forward(self, x):
        return torch.relu(self.bn(self.linear(x / (x.norm(dim=1, keepdim=True) + 1e-4))))

    def train_on_batch(self, x, y):
        h = self.forward(x)
        loss = F.cross_entropy(self.M(h), y)
        self.opt.zero_grad(); loss.backward(); self.opt.step()
        return loss.item(), h.detach()


class MonoForwardNet(nn.Module):
    def __init__(self, dims, n_classes=10, lr=0.01):
        super().__init__()
        self.layers = nn.ModuleList([MonoForwardLayer(dims[i], dims[i+1], n_classes, lr) for i in range(len(dims)-1)])

    def train_step(self, x, y):
        total, h = 0, x
        for layer in self.layers:
            loss, h = layer.train_on_batch(h, y)
            total += loss
        return total / len(self.layers)

    def predict(self, x):
        h = x
        for layer in self.layers: h = layer(h)
        return self.layers[-1].M(h)
