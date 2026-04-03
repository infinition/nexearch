"""
Round 2: Deep-dive on Equilibrium Propagation variants
=======================================================
EqProp was the only local algo that genuinely learned (78% after 5 epochs).
Now we iterate aggressively to close the gap with backprop (97.7%).

Variants:
1. EqProp-Tuned    — hyperparameter optimization
2. EqProp-Deep     — deeper architecture + more relaxation
3. EqProp-Augmented — with local batch norm + momentum
4. HESP (Hybrid Equilibrium-Signal Propagation) — NEW PARADIGM
   Combines EqProp's physical equilibrium with direct error signal injection.
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
            pred = model.predict(x)
            correct += (pred.argmax(1) == y).sum().item()
            total += y.size(0)
    return correct / total

# =============================================================================
# BASELINE: Backprop
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
# VARIANT 1: EqProp-Tuned (better hyperparams)
# =============================================================================
class EqPropTuned(nn.Module):
    def __init__(self, dims, beta=0.5, n_relax=25, relax_lr=0.3, lr=0.02):
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
                    ds += self.rho(states[l-1]) @ self.weights[l-1].detach()
                if l < len(states) - 1:
                    ds += self.rho(states[l+1]) @ self.weights[l].detach().T
                if l == len(states) - 1 and target is not None and beta > 0:
                    ds -= beta * (states[l] - target)
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
                hf = self.rho(s_free[l]).T @ self.rho(s_free[l+1]) / x.size(0)
                hc = self.rho(s_clamp[l]).T @ self.rho(s_clamp[l+1]) / x.size(0)
                self.weights[l].data += (self.lr / self.beta) * (hc - hf)
            for l in range(len(s_free)):
                db = (self.rho(s_clamp[l]) - self.rho(s_free[l])).mean(0)
                self.biases[l].data += (self.lr / self.beta) * db
        return F.mse_loss(s_free[-1], target).item()

# =============================================================================
# VARIANT 2: EqProp with momentum + weight decay
# =============================================================================
class EqPropMomentum(nn.Module):
    def __init__(self, dims, beta=0.5, n_relax=20, relax_lr=0.3, lr=0.02, momentum=0.9, wd=1e-4):
        super().__init__()
        self.dims = dims
        self.beta = beta
        self.n_relax = n_relax
        self.relax_lr = relax_lr
        self.lr = lr
        self.momentum = momentum
        self.wd = wd
        self.weights = nn.ParameterList([
            nn.Parameter(torch.randn(dims[i], dims[i+1]) * np.sqrt(2.0 / dims[i]))
            for i in range(len(dims) - 1)
        ])
        self.biases = nn.ParameterList([
            nn.Parameter(torch.zeros(dims[i])) for i in range(len(dims))
        ])
        # Momentum buffers
        self.w_vel = [torch.zeros_like(w) for w in self.weights]
        self.b_vel = [torch.zeros_like(b) for b in self.biases]

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
                    ds += self.rho(states[l-1]) @ self.weights[l-1].detach()
                if l < len(states) - 1:
                    ds += self.rho(states[l+1]) @ self.weights[l].detach().T
                if l == len(states) - 1 and target is not None and beta > 0:
                    ds -= beta * (states[l] - target)
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
                hf = self.rho(s_free[l]).T @ self.rho(s_free[l+1]) / x.size(0)
                hc = self.rho(s_clamp[l]).T @ self.rho(s_clamp[l+1]) / x.size(0)
                grad = (self.lr / self.beta) * (hc - hf) - self.wd * self.weights[l].data
                self.w_vel[l] = self.w_vel[l].to(grad.device)
                self.w_vel[l] = self.momentum * self.w_vel[l] + grad
                self.weights[l].data += self.w_vel[l]

            for l in range(len(s_free)):
                db = (self.lr / self.beta) * (self.rho(s_clamp[l]) - self.rho(s_free[l])).mean(0)
                self.b_vel[l] = self.b_vel[l].to(db.device)
                self.b_vel[l] = self.momentum * self.b_vel[l] + db
                self.biases[l].data += self.b_vel[l]

        return F.mse_loss(s_free[-1], target).item()

# =============================================================================
# VARIANT 3: HESP — Hybrid Equilibrium-Signal Propagation (NEW PARADIGM)
# =============================================================================
#
# Key insight: EqProp works but is slow because it needs 2 full relaxations.
# What if we could INJECT a "hint" signal that accelerates convergence?
#
# HESP = EqProp skeleton + direct local error injection at each layer
#
# Each layer computes:
#   1. Its equilibrium contribution (Hebbian correlation)
#   2. A LOCAL error signal from a tiny per-layer classifier
#      (each layer tries to classify the input using just its activations)
#   3. The weight update combines both: physical equilibrium + error correction
#
# This is NOT backprop because:
#   - No gradient flows between layers
#   - Each layer has its OWN loss function
#   - The "hint" is purely local (per-layer linear probe)
#
# The equilibrium part ensures stability; the error injection accelerates learning.

class HESPLayer(nn.Module):
    """One HESP layer: equilibrium dynamics + local error signal."""
    def __init__(self, in_dim, out_dim, n_classes, lr=0.02, eq_weight=0.5):
        super().__init__()
        # Main weights (equilibrium)
        self.w = nn.Parameter(torch.randn(in_dim, out_dim) * np.sqrt(2.0 / in_dim))
        self.b = nn.Parameter(torch.zeros(out_dim))
        # Local classifier (tiny linear probe for error signal)
        self.probe_w = nn.Parameter(torch.randn(out_dim, n_classes) * 0.01)
        self.probe_b = nn.Parameter(torch.zeros(n_classes))

        self.lr = lr
        self.eq_weight = eq_weight  # Balance between equilibrium and error signal
        self.n_classes = n_classes
        # Momentum
        self.w_vel = None
        self.momentum = 0.9

    def rho(self, x): return torch.clamp(x, 0, 1)

    def forward(self, x):
        self.input = x.detach()
        self.activation = self.rho(x @ self.w.detach() + self.b.detach())
        return self.activation

    def local_loss(self, y):
        """Per-layer classification loss — purely local."""
        logits = self.activation @ self.probe_w + self.probe_b
        return F.cross_entropy(logits, y)

    def accuracy(self, y):
        """Per-layer accuracy for monitoring."""
        with torch.no_grad():
            logits = self.activation @ self.probe_w + self.probe_b
            return (logits.argmax(1) == y).float().mean().item()

    def update(self, s_free, s_clamp, s_free_next, s_clamp_next, y, beta):
        """Combined update: equilibrium Hebbian + local error correction."""
        B = self.input.size(0)

        # 1. EQUILIBRIUM COMPONENT (classical EqProp Hebbian) — no grad needed
        with torch.no_grad():
            hebb_free = self.rho(s_free).T @ self.rho(s_free_next) / B
            hebb_clamp = self.rho(s_clamp).T @ self.rho(s_clamp_next) / B
            dW_eq = (1.0 / beta) * (hebb_clamp - hebb_free)

        # 2. ERROR SIGNAL COMPONENT — recompute activation WITH gradient
        a = self.rho(self.input @ self.w + self.b)  # This has grad_fn via self.w
        logits = a @ self.probe_w + self.probe_b
        loss = F.cross_entropy(logits, y)
        loss.backward()

        with torch.no_grad():
            # Error signal from the local probe
            dW_err = self.w.grad if self.w.grad is not None else torch.zeros_like(self.w.data)

            # 3. COMBINED UPDATE
            dW = self.eq_weight * dW_eq - (1 - self.eq_weight) * dW_err

            # Momentum
            if self.w_vel is None:
                self.w_vel = torch.zeros_like(dW)
            self.w_vel = self.momentum * self.w_vel + dW
            self.w.data += self.lr * self.w_vel

            if self.b.grad is not None:
                self.b.data -= self.lr * (1 - self.eq_weight) * self.b.grad

            # Update probe weights (simple SGD)
            if self.probe_w.grad is not None:
                self.probe_w.data -= 0.01 * self.probe_w.grad
            if self.probe_b.grad is not None:
                self.probe_b.data -= 0.01 * self.probe_b.grad

            # Zero grads
            self.w.grad = None
            self.b.grad = None
            self.probe_w.grad = None
            self.probe_b.grad = None

            return loss.item()


class HESPNet(nn.Module):
    """HESP: Hybrid Equilibrium-Signal Propagation.
    Each layer learns via dual signals:
    1. Physical equilibrium (Hebbian diff between free and clamped)
    2. Local error injection (per-layer classifier probe)
    """
    def __init__(self, dims, n_classes=10, beta=0.5, n_relax=15, relax_lr=0.3, lr=0.02, eq_weight=0.5):
        super().__init__()
        self.dims = dims
        self.n_classes = n_classes
        self.beta = beta
        self.n_relax = n_relax
        self.relax_lr = relax_lr

        self.layers = nn.ModuleList([
            HESPLayer(dims[i], dims[i+1], n_classes, lr, eq_weight)
            for i in range(len(dims) - 1)
        ])

    def rho(self, x): return torch.clamp(x, 0, 1)

    def relax(self, x, target=None, beta=0):
        """Same relaxation as EqProp."""
        states = [x.detach()]
        h = x.detach()
        for layer in self.layers:
            h = layer.rho(h @ layer.w.detach() + layer.b.detach())
            states.append(h.clone())

        for _ in range(self.n_relax):
            for l in range(1, len(states)):
                layer_l = self.layers[l-1] if l-1 < len(self.layers) else self.layers[-1]
                ds = -states[l]
                if l > 0 and l-1 < len(self.layers):
                    ds += self.rho(states[l-1]) @ self.layers[l-1].w.detach()
                    ds += self.layers[l-1].b.detach()
                if l < len(states) - 1:
                    ds += self.rho(states[l+1]) @ self.layers[l].w.detach().T
                if l == len(states) - 1 and target is not None and beta > 0:
                    ds -= beta * (states[l] - target)
                states[l] = self.rho(states[l] + self.relax_lr * ds)
        return states

    def forward(self, x):
        h = x
        for layer in self.layers:
            h = layer(h)
        return h

    def predict(self, x):
        # Use last layer's output directly
        h = x
        for layer in self.layers:
            h = layer(h)
        # Use the last layer's probe for prediction
        logits = h @ self.layers[-1].probe_w + self.layers[-1].probe_b
        return logits

    def train_step(self, x, y):
        # 1. Forward pass
        h = x
        for layer in self.layers:
            h = layer(h)

        # 2. Relaxation phases (EqProp)
        target = F.one_hot(y, self.n_classes).float()
        s_free = self.relax(x)
        s_clamp = self.relax(x, target, self.beta)

        # 3. Combined updates per layer
        total_loss = 0
        for l, layer in enumerate(self.layers):
            total_loss += layer.update(
                s_free[l], s_clamp[l],
                s_free[l+1], s_clamp[l+1],
                y, self.beta
            )

        return total_loss / len(self.layers)


# =============================================================================
# VARIANT 4: Pure Local Error — Direct Feedback Alignment style but simpler
# =============================================================================
class DirectLocalNet(nn.Module):
    """Each layer has its own classifier head and trains independently.
    No equilibrium, no relaxation — just pure local objectives.
    Similar to Hinton's Forward-Forward but with cross-entropy instead of goodness.
    """
    def __init__(self, dims, n_classes=10, lr=0.001):
        super().__init__()
        self.dims = dims
        self.n_classes = n_classes
        self.layers = nn.ModuleList()
        self.probes = nn.ModuleList()
        self.optimizers = []

        for i in range(len(dims) - 1):
            layer = nn.Sequential(nn.Linear(dims[i], dims[i+1]), nn.ReLU(), nn.BatchNorm1d(dims[i+1]))
            probe = nn.Linear(dims[i+1], n_classes)
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
            loss.backward(retain_graph=(i < len(self.layers) - 1))
            opt.step()

            total_loss += loss.item()
            h = h.detach()  # Stop gradient between layers

        return total_loss / len(self.layers)

# =============================================================================
# TRAINING LOOP
# =============================================================================
def train_and_eval(name, model, train_loader, test_loader, n_epochs=10):
    model = model.to(device)
    history = {'loss': [], 'acc': [], 'time': []}
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
        history['time'].append(dt)
        print(f"  Epoch {epoch+1:>2}/{n_epochs} | Loss: {epoch_loss/n:.4f} | Acc: {acc*100:.2f}% | {dt:.1f}s")

    total = sum(history['time'])
    print(f"  >>> Final: {history['acc'][-1]*100:.2f}% in {total:.1f}s")
    return history

# =============================================================================
# RUN
# =============================================================================
if __name__ == '__main__':
    train_loader, test_loader = get_mnist(256)
    dims = [784, 500, 300, 10]
    N = 10  # 10 epochs this time

    results = {}
    results['Backprop'] = train_and_eval('Backprop (baseline)', BackpropNet(dims), train_loader, test_loader, N)
    results['EqProp-Tuned'] = train_and_eval('EqProp-Tuned', EqPropTuned(dims, beta=0.5, n_relax=25, relax_lr=0.3, lr=0.02), train_loader, test_loader, N)
    results['EqProp-Momentum'] = train_and_eval('EqProp + Momentum', EqPropMomentum(dims, beta=0.5, n_relax=20, relax_lr=0.3, lr=0.02), train_loader, test_loader, N)
    results['HESP'] = train_and_eval('HESP (Hybrid Eq-Signal Prop)', HESPNet(dims, beta=0.5, n_relax=10, relax_lr=0.3, lr=0.02, eq_weight=0.3), train_loader, test_loader, N)
    results['DirectLocal'] = train_and_eval('Direct Local Probes', DirectLocalNet(dims, lr=0.001), train_loader, test_loader, N)

    # =================================================================
    print("\n" + "="*70)
    print("  ROUND 2 RESULTS — MNIST (10 epochs)")
    print("="*70)
    print(f"  {'Algorithm':<30} {'Accuracy':>10} {'Time':>10}")
    print("-"*55)
    for k in sorted(results, key=lambda k: results[k]['acc'][-1], reverse=True):
        a = results[k]['acc'][-1] * 100
        t = sum(results[k]['time'])
        marker = " <<<" if k in ['HESP', 'DirectLocal'] else ""
        print(f"  {k:<30} {a:>9.2f}% {t:>9.1f}s{marker}")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    for (k, h), c in zip(results.items(), colors):
        ax1.plot(range(1, N+1), [a*100 for a in h['acc']], 'o-', label=k, color=c, linewidth=2)
        ax2.plot(range(1, N+1), h['loss'], 'o-', label=k, color=c, linewidth=2)
    ax1.set_xlabel('Epoch'); ax1.set_ylabel('Accuracy (%)'); ax1.set_title('Test Accuracy'); ax1.legend(); ax1.grid(alpha=0.3)
    ax2.set_xlabel('Epoch'); ax2.set_ylabel('Loss'); ax2.set_title('Training Loss'); ax2.legend(); ax2.set_yscale('log'); ax2.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('benchmark_round2.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n  Plot saved: benchmark_round2.png")
