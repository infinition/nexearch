"""
NoProp Diffusion Learning - Core Implementation
=================================================
Based on arXiv:2503.24322 (DeepMind, March 2025).
Each block independently denoises a noisy label embedding.
No global forward or backward pass.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class NoPropBlock(nn.Module):
    def __init__(self, input_dim, label_dim, hidden_dim=256):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        self.label_proj = nn.Linear(label_dim, hidden_dim)
        self.time_proj = nn.Linear(1, hidden_dim)
        self.net = nn.Sequential(
            nn.LayerNorm(hidden_dim), nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(), nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(), nn.Linear(hidden_dim, label_dim),
        )

    def forward(self, x_features, z_noisy, t):
        h = self.input_proj(x_features) + self.label_proj(z_noisy) + self.time_proj(t.unsqueeze(-1))
        return self.net(h)


class NoPropNet(nn.Module):
    def __init__(self, input_dim, n_classes=10, n_blocks=4, hidden_dim=256, label_dim=32, lr=0.001):
        super().__init__()
        self.n_classes, self.n_blocks, self.label_dim = n_classes, n_blocks, label_dim
        self.feature_net = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.ReLU(), nn.BatchNorm1d(hidden_dim))
        self.label_embed = nn.Linear(n_classes, label_dim)
        self.blocks = nn.ModuleList([NoPropBlock(hidden_dim, label_dim, hidden_dim) for _ in range(n_blocks)])
        self.output_proj = nn.Linear(label_dim, n_classes)
        self.optimizers = []
        for i, block in enumerate(self.blocks):
            params = list(block.parameters()) + list(self.output_proj.parameters())
            if i == 0: params += list(self.feature_net.parameters()) + list(self.label_embed.parameters())
            self.optimizers.append(torch.optim.Adam(params, lr=lr))

    def _noise_schedule(self, t):
        return torch.cos(t * math.pi / 2), torch.sin(t * math.pi / 2)

    def train_step(self, x, y):
        B = x.size(0)
        y_oh = F.one_hot(y, self.n_classes).float()
        z_0 = self.label_embed(y_oh).detach()
        total_loss = 0
        for i, (block, opt) in enumerate(zip(self.blocks, self.optimizers)):
            t = torch.rand(B, device=x.device)
            alpha, sigma = self._noise_schedule(t)
            z_noisy = alpha.unsqueeze(1) * z_0 + sigma.unsqueeze(1) * torch.randn_like(z_0)
            features = self.feature_net(x) if i == 0 else self.feature_net(x).detach()
            z_pred = block(features, z_noisy, t)
            loss = F.mse_loss(z_pred, z_0.detach() if i > 0 else z_0) + 0.5 * F.cross_entropy(self.output_proj(z_pred), y)
            opt.zero_grad(); loss.backward(); opt.step()
            total_loss += loss.item()
        return total_loss / self.n_blocks

    def predict(self, x):
        features = self.feature_net(x)
        z = torch.randn(x.size(0), self.label_dim, device=x.device)
        for i, block in enumerate(self.blocks):
            t = torch.full((x.size(0),), 1.0 - i / self.n_blocks, device=x.device)
            z = block(features, z, t)
        return self.output_proj(z)
