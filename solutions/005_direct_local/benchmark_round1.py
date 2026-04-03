"""
Local Learning Paradigm — Focused Benchmark
=============================================
4 finalist algorithms vs Backprop baseline on MNIST.
Goal: find a GENUINELY new local learning rule that works.
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
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

torch.manual_seed(42)
np.random.seed(42)

# =============================================================================
# DATA
# =============================================================================
def get_mnist(batch_size=256):
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
    train = datasets.MNIST('data', train=True, download=True, transform=transform)
    test = datasets.MNIST('data', train=False, transform=transform)
    return DataLoader(train, batch_size=batch_size, shuffle=True, num_workers=0), \
           DataLoader(test, batch_size=1000, num_workers=0)

def evaluate(model, test_loader):
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            x = x.view(x.size(0), -1)
            pred = model.predict(x) if hasattr(model, 'predict') else model(x)
            correct += (pred.argmax(1) == y).sum().item()
            total += y.size(0)
    return correct / total

# =============================================================================
# BASELINE: Standard Backprop
# =============================================================================
class BackpropNet(nn.Module):
    def __init__(self, dims):
        super().__init__()
        layers = []
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i+1]))
            if i < len(dims) - 2:
                layers.append(nn.ReLU())
        self.net = nn.Sequential(*layers)
        self.optimizer = torch.optim.Adam(self.parameters(), lr=0.001)

    def forward(self, x): return self.net(x)
    def predict(self, x): return self.forward(x)

    def train_step(self, x, y):
        self.optimizer.zero_grad()
        loss = F.cross_entropy(self.forward(x), y)
        loss.backward()
        self.optimizer.step()
        return loss.item()

# =============================================================================
# ALGO 1: Forward-Forward + Natural Gradient (Hinton 2022 + Amari)
# =============================================================================
class FFLayer(nn.Module):
    def __init__(self, in_dim, out_dim, threshold=2.0, lr=0.03):
        super().__init__()
        self.linear = nn.Linear(in_dim, out_dim)
        nn.init.kaiming_normal_(self.linear.weight)
        self.threshold = threshold
        self.lr = lr
        self.fisher_diag = None

    def forward(self, x):
        x_norm = x / (x.norm(dim=1, keepdim=True) + 1e-4)
        return torch.relu(self.linear(x_norm))

    def goodness(self, h):
        return (h ** 2).sum(dim=1)

    def train_on_batch(self, x_pos, x_neg):
        h_pos, h_neg = self.forward(x_pos), self.forward(x_neg)
        g_pos, g_neg = self.goodness(h_pos), self.goodness(h_neg)

        loss = (torch.log(1 + torch.exp(-(g_pos - self.threshold))).mean() +
                torch.log(1 + torch.exp(g_neg - self.threshold)).mean())

        self.linear.zero_grad()
        loss.backward()

        with torch.no_grad():
            g = self.linear.weight.grad
            gsq = g ** 2
            if self.fisher_diag is None:
                self.fisher_diag = gsq.clone()
            else:
                self.fisher_diag = 0.99 * self.fisher_diag + 0.01 * gsq
            self.linear.weight.data -= self.lr * g / (self.fisher_diag.sqrt() + 1e-8)
            if self.linear.bias is not None and self.linear.bias.grad is not None:
                self.linear.bias.data -= self.lr * self.linear.bias.grad

        return loss.item(), h_pos.detach(), h_neg.detach()


class ForwardForwardNet(nn.Module):
    def __init__(self, dims, n_classes=10):
        super().__init__()
        self.n_classes = n_classes
        self.layers = nn.ModuleList([FFLayer(dims[i], dims[i+1]) for i in range(len(dims)-1)])

    def _overlay(self, x, y):
        x = x.clone()
        x[:, :self.n_classes] = 0
        x[torch.arange(x.size(0), device=x.device), y] = x.max()
        return x

    def train_step(self, x, y):
        x_pos = self._overlay(x, y)
        y_neg = (y + torch.randint(1, self.n_classes, y.shape, device=y.device)) % self.n_classes
        x_neg = self._overlay(x, y_neg)
        total_loss, h_pos, h_neg = 0, x_pos, x_neg
        for layer in self.layers:
            loss, h_pos, h_neg = layer.train_on_batch(h_pos, h_neg)
            total_loss += loss
        return total_loss / len(self.layers)

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
# ALGO 2: Predictive Coding (Friston / Rao-Ballard)
# =============================================================================
class PredCodingNet(nn.Module):
    def __init__(self, dims, lr=0.005, n_iter=15, iter_lr=0.1):
        super().__init__()
        self.dims = dims
        self.lr = lr
        self.n_iter = n_iter
        self.iter_lr = iter_lr
        self.weights = nn.ParameterList([
            nn.Parameter(torch.randn(dims[i+1], dims[i]) * np.sqrt(2.0 / dims[i+1]))
            for i in range(len(dims) - 1)
        ])
        self.biases = nn.ParameterList([
            nn.Parameter(torch.zeros(dims[i])) for i in range(len(dims) - 1)
        ])

    def predict_below(self, mu_above, l):
        return torch.relu(mu_above @ self.weights[l] + self.biases[l])

    def forward(self, x):
        mus = [x]
        h = x
        for i in range(len(self.weights)):
            h = torch.relu(h @ self.weights[i].T)
            mus.append(h)
        for _ in range(self.n_iter):
            for l in range(1, len(mus) - 1):
                pred = self.predict_below(mus[l+1] if l+1 < len(mus) else mus[l], l if l < len(self.weights) else l-1)
                err = mus[l] - pred if pred.shape == mus[l].shape else torch.zeros_like(mus[l])
                mus[l] = torch.relu(mus[l] - self.iter_lr * err)
        return mus[-1]

    def predict(self, x): return self.forward(x)

    def train_step(self, x, y):
        mus = [x]
        h = x
        for i in range(len(self.weights)):
            h = torch.relu(h @ self.weights[i].T)
            mus.append(h)
        mus[-1] = F.one_hot(y, self.dims[-1]).float()

        for _ in range(self.n_iter):
            for l in range(1, len(mus) - 1):
                pred = self.predict_below(mus[l+1], l) if l < len(self.weights) else mus[l]
                if pred.shape == mus[l].shape:
                    err = mus[l] - pred
                    mus[l] = torch.relu(mus[l] - self.iter_lr * err)

        total_loss = 0
        for l in range(len(self.weights)):
            pred = self.predict_below(mus[l+1], l)
            err = mus[l] - pred
            dW = mus[l+1].T @ err / x.size(0)
            db = err.mean(0)
            self.weights[l].data += self.lr * dW
            self.biases[l].data += self.lr * db
            total_loss += (err ** 2).mean().item()
        return total_loss / len(self.weights)

# =============================================================================
# ALGO 3: Equilibrium Propagation (Scellier & Bengio 2017)
# =============================================================================
class EqPropNet(nn.Module):
    def __init__(self, dims, beta=1.0, n_relax=15, relax_lr=0.5, lr=0.01):
        super().__init__()
        self.dims = dims
        self.beta = beta
        self.n_relax = n_relax
        self.relax_lr = relax_lr
        self.lr = lr
        self.weights = nn.ParameterList([
            nn.Parameter(torch.randn(dims[i], dims[i+1]) * np.sqrt(2.0 / dims[i]))
            for i in range(len(dims) - 1)
        ])
        self.biases = nn.ParameterList([
            nn.Parameter(torch.zeros(dims[i])) for i in range(len(dims))
        ])

    def rho(self, x): return torch.clamp(x, 0, 1)

    def relax(self, x, target=None, beta=0):
        states = [x.detach()]
        h = x.detach()
        for l in range(len(self.weights)):
            h = self.rho(h @ self.weights[l].detach() + self.biases[l+1].detach())
            states.append(h.clone())

        for _ in range(self.n_relax):
            for l in range(1, len(states)):
                ds = -states[l] + self.biases[l].detach()
                if l > 0:
                    ds = ds + self.rho(states[l-1]) @ self.weights[l-1].detach()
                if l < len(states) - 1:
                    ds = ds + self.rho(states[l+1]) @ self.weights[l].detach().T
                if l == len(states) - 1 and target is not None and beta > 0:
                    ds = ds - beta * (states[l] - target)
                states[l] = self.rho(states[l] + self.relax_lr * ds)
        return states

    def forward(self, x): return self.relax(x)[-1]
    def predict(self, x): return self.forward(x)

    def train_step(self, x, y):
        target = F.one_hot(y, self.dims[-1]).float()
        s_free = self.relax(x)
        s_clamp = self.relax(x, target, self.beta)

        with torch.no_grad():
            for l in range(len(self.weights)):
                hebb_f = self.rho(s_free[l]).T @ self.rho(s_free[l+1]) / x.size(0)
                hebb_c = self.rho(s_clamp[l]).T @ self.rho(s_clamp[l+1]) / x.size(0)
                self.weights[l].data += (self.lr / self.beta) * (hebb_c - hebb_f)
            for l in range(len(s_free)):
                db = (self.rho(s_clamp[l]) - self.rho(s_free[l])).mean(0)
                self.biases[l].data += (self.lr / self.beta) * db

        return F.mse_loss(s_free[-1], target).item()

# =============================================================================
# ALGO 4: NOVA — Neighbor-Only Variational Alignment (ORIGINAL)
# =============================================================================
class NOVALayer(nn.Module):
    def __init__(self, in_dim, out_dim, alpha=0.3, lr=0.005):
        super().__init__()
        self.w = nn.Parameter(torch.randn(in_dim, out_dim) * np.sqrt(2.0 / in_dim), requires_grad=False)
        self.b = nn.Parameter(torch.zeros(out_dim), requires_grad=False)
        self.alpha = alpha
        self.lr = lr
        self.beliefs = None
        self.w_mom = None
        self.mom_decay = 0.9
        # Local running stats
        self.running_mean = None
        self.running_var = None

    def forward(self, x):
        self.input = x.detach()
        pre = x @ self.w + self.b

        # Local batch normalization (no global stats needed)
        if self.training:
            mean = pre.mean(0)
            var = pre.var(0, unbiased=False) + 1e-5
            if self.running_mean is None:
                self.running_mean = mean.detach().clone()
                self.running_var = var.detach().clone()
            else:
                self.running_mean = 0.9 * self.running_mean + 0.1 * mean.detach()
                self.running_var = 0.9 * self.running_var + 0.1 * var.detach()
            pre = (pre - mean) / var.sqrt()
        else:
            if self.running_mean is not None:
                pre = (pre - self.running_mean) / (self.running_var + 1e-5).sqrt()

        self.activation = torch.relu(pre)
        self.beliefs = self.activation.detach().clone()
        return self.activation.detach()

    def set_beliefs(self, neighbor_beliefs):
        with torch.no_grad():
            self.beliefs = (1 - self.alpha) * self.activation + self.alpha * neighbor_beliefs

    def local_update(self):
        with torch.no_grad():
            error = self.beliefs - self.activation
            # Per-neuron confidence: inverse variance of errors across batch
            var_per_neuron = error.var(dim=0, keepdim=True) + 1e-8
            confidence = 1.0 / (1.0 + var_per_neuron)
            # Modulated Hebbian update
            dW = self.input.T @ (error * confidence) / self.input.size(0)
            db = (error * confidence).mean(0)

            if self.w_mom is None:
                self.w_mom = torch.zeros_like(dW)
            self.w_mom = self.mom_decay * self.w_mom + dW
            self.w.data += self.lr * self.w_mom
            self.b.data += self.lr * db

            # Column-wise weight normalization (local, no global info)
            norms = self.w.data.norm(dim=0, keepdim=True)
            self.w.data = self.w.data / (norms + 1e-8) * np.sqrt(self.w.shape[0])

            return (error ** 2).mean().item()


class NOVANet(nn.Module):
    def __init__(self, dims, n_diffuse=5, alpha=0.3, lr=0.005):
        super().__init__()
        self.dims = dims
        self.n_diffuse = n_diffuse
        self.layers = nn.ModuleList([
            NOVALayer(dims[i], dims[i+1], alpha, lr)
            for i in range(len(dims) - 1)
        ])

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

    def predict(self, x): return self.forward(x)

    def train_step(self, x, y):
        # 1. Forward (all detached)
        h = x
        for layer in self.layers:
            h = layer(h)

        # 2. Clamp output beliefs to target
        target = F.one_hot(y, self.dims[-1]).float()
        self.layers[-1].beliefs = target

        # 3. Diffuse beliefs backward (like a wave)
        for _ in range(self.n_diffuse):
            for i in range(len(self.layers) - 2, -1, -1):
                next_beliefs = self.layers[i + 1].beliefs
                projected = torch.relu(next_beliefs @ self.layers[i + 1].w.data.T)
                # Scale to match activation magnitudes
                act_std = self.layers[i].activation.std() + 1e-8
                proj_std = projected.std() + 1e-8
                projected = projected * (act_std / proj_std).clamp(max=3.0)
                self.layers[i].set_beliefs(projected)

        # 4. Local updates (parallel per layer)
        total_loss = sum(layer.local_update() for layer in self.layers)
        return total_loss / len(self.layers)

# =============================================================================
# TRAINING LOOP
# =============================================================================
def train_and_eval(name, model, train_loader, test_loader, n_epochs=5):
    model = model.to(device)
    history = {'loss': [], 'acc': [], 'time_per_epoch': []}
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    for epoch in range(n_epochs):
        t0 = time.time()
        model.train()
        epoch_loss, n = 0, 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            x = x.view(x.size(0), -1)
            epoch_loss += model.train_step(x, y)
            n += 1

        dt = time.time() - t0
        model.eval()
        acc = evaluate(model, test_loader)
        history['loss'].append(epoch_loss / n)
        history['acc'].append(acc)
        history['time_per_epoch'].append(dt)
        print(f"  Epoch {epoch+1}/{n_epochs} | Loss: {epoch_loss/n:.4f} | Acc: {acc*100:.2f}% | {dt:.1f}s")

    print(f"  >>> Final: {history['acc'][-1]*100:.2f}% in {sum(history['time_per_epoch']):.1f}s total")
    return history

# =============================================================================
# RUN BENCHMARK
# =============================================================================
if __name__ == '__main__':
    train_loader, test_loader = get_mnist(batch_size=256)
    dims = [784, 500, 200, 10]
    N_EPOCHS = 5

    results = {}

    # Baseline
    results['Backprop'] = train_and_eval('Backprop (baseline)', BackpropNet(dims), train_loader, test_loader, N_EPOCHS)

    # Forward-Forward
    results['Forward-Forward'] = train_and_eval('Forward-Forward + NatGrad', ForwardForwardNet([784, 500, 200]), train_loader, test_loader, N_EPOCHS)

    # Predictive Coding
    results['PredCoding'] = train_and_eval('Predictive Coding', PredCodingNet(dims), train_loader, test_loader, N_EPOCHS)

    # Equilibrium Propagation
    results['EqProp'] = train_and_eval('Equilibrium Propagation', EqPropNet(dims), train_loader, test_loader, N_EPOCHS)

    # NOVA
    results['NOVA'] = train_and_eval('NOVA (ours)', NOVANet(dims, n_diffuse=5, alpha=0.3, lr=0.005), train_loader, test_loader, N_EPOCHS)

    # =================================================================
    # RESULTS
    # =================================================================
    print("\n" + "="*70)
    print("  BENCHMARK RESULTS — MNIST (5 epochs)")
    print("="*70)
    print(f"  {'Algorithm':<30} {'Accuracy':>10} {'Time':>10} {'Local?':>8}")
    print("-"*60)
    loc = {'Backprop': 'NO', 'Forward-Forward': 'YES', 'PredCoding': 'YES', 'EqProp': 'YES', 'NOVA': 'YES'}
    for k in results:
        a = results[k]['acc'][-1] * 100
        t = sum(results[k]['time_per_epoch'])
        print(f"  {k:<30} {a:>9.2f}% {t:>9.1f}s {loc[k]:>8}")

    # Find best local
    local_only = {k: v for k, v in results.items() if k != 'Backprop'}
    best = max(local_only, key=lambda k: local_only[k]['acc'][-1])
    print(f"\n  >>> Best local algorithm: {best} ({local_only[best]['acc'][-1]*100:.2f}%)")
    print(f"  >>> Gap vs backprop: {(results['Backprop']['acc'][-1] - local_only[best]['acc'][-1])*100:.2f}%")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    colors = {'Backprop': '#e74c3c', 'Forward-Forward': '#3498db', 'PredCoding': '#9b59b6', 'EqProp': '#f39c12', 'NOVA': '#2ecc71'}
    for k, h in results.items():
        ax1.plot(range(1, N_EPOCHS+1), [a*100 for a in h['acc']], 'o-', label=k, color=colors[k], linewidth=2.5)
        ax2.plot(range(1, N_EPOCHS+1), h['loss'], 'o-', label=k, color=colors[k], linewidth=2.5)
    ax1.set_xlabel('Epoch'); ax1.set_ylabel('Test Accuracy (%)'); ax1.set_title('Accuracy'); ax1.legend(); ax1.grid(alpha=0.3)
    ax2.set_xlabel('Epoch'); ax2.set_ylabel('Loss'); ax2.set_title('Training Loss'); ax2.legend(); ax2.set_yscale('log'); ax2.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('benchmark_round1.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n  Plot saved: benchmark_round1.png")
