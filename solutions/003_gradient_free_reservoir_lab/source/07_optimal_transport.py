"""
#07 - Optimal Transport Learning
Use Sinkhorn distances to match layer activations to target distributions.
No gradients: adjust weights to minimize transport cost locally.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu

def sinkhorn_distance(a, b, cost_matrix, reg=0.1, n_iter=20):
    """Compute Sinkhorn divergence between distributions a and b."""
    K = np.exp(-cost_matrix / reg)
    n, m = len(a), len(b)
    u = np.ones(n) / n
    for _ in range(n_iter):
        v = b / (K.T @ u + 1e-8)
        u = a / (K @ v + 1e-8)
    transport = np.sum(u[:, None] * K * v[None, :] * cost_matrix)
    return transport

class OTLayer:
    def __init__(self, in_dim, out_dim, lr=0.01):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.05
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr

    def forward(self, x):
        return relu(x @ self.W + self.b)

    def ot_update(self, x, h, target_dist):
        """Update weights to push activations toward target distribution."""
        # Current activation distribution (normalized)
        h_dist = np.mean(h, axis=0)
        h_dist = h_dist / (h_dist.sum() + 1e-8)

        # Perturbation-based gradient of OT distance
        n_perturb = 10
        sigma = 0.01
        ot_grads_W = np.zeros_like(self.W)

        # Cost matrix (simple: squared difference of indices)
        n = len(h_dist)
        idx = np.arange(n, dtype=np.float32)
        C = (idx[:, None] - idx[None, :]) ** 2

        base_dist = sinkhorn_distance(h_dist, target_dist, C)

        for _ in range(n_perturb):
            noise = np.random.randn(*self.W.shape).astype(np.float32)
            W_pert = self.W + sigma * noise
            h_pert = relu(x @ W_pert + self.b)
            h_pert_dist = np.mean(h_pert, axis=0)
            h_pert_dist = h_pert_dist / (h_pert_dist.sum() + 1e-8)
            ot_dist = sinkhorn_distance(h_pert_dist, target_dist, C)
            ot_grads_W += (ot_dist - base_dist) / sigma * noise

        ot_grads_W /= n_perturb
        self.W -= self.lr * ot_grads_W

class OTNetwork:
    def __init__(self, layer_sizes, lr=0.005):
        self.layers = []
        for i in range(len(layer_sizes)-1):
            self.layers.append(OTLayer(layer_sizes[i], layer_sizes[i+1], lr=lr))

    def forward(self, x):
        h = x
        for layer in self.layers[:-1]:
            h = layer.forward(h)
        return h @ self.layers[-1].W + self.layers[-1].b

    def train_step(self, x, y, n_classes=10):
        # Forward pass
        activations = [x]
        h = x
        for layer in self.layers:
            h = layer.forward(h)
            activations.append(h)

        # For hidden layers: match to class-conditional uniform distributions
        for i, layer in enumerate(self.layers[:-1]):
            # Target: uniform-ish activation (sparse but diverse)
            target = np.ones(layer.W.shape[1], dtype=np.float32) / layer.W.shape[1]
            # Add class-conditional bias
            for c in range(n_classes):
                mask = y == c
                if mask.any():
                    target_c = target.copy()
                    # Each class activates a different region
                    start = (c * len(target)) // n_classes
                    end = ((c+1) * len(target)) // n_classes
                    target_c[start:end] *= 3.0
                    target_c /= target_c.sum()
                    layer.ot_update(activations[i][mask], activations[i+1][mask], target_c)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=3000, n_test=1000)

    net = OTNetwork([784, 200, 10], lr=0.005)
    n_epochs = 15
    batch_size = 128

    with Timer("Optimal Transport Learning") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                net.train_step(X_train[idx], y_train[idx])

            if (epoch + 1) % 5 == 0:
                # Evaluate with readout
                h = X_train
                for layer in net.layers[:-1]:
                    h = layer.forward(h)
                ht = X_test
                for layer in net.layers[:-1]:
                    ht = layer.forward(ht)

                # Ridge readout
                lam = 1.0
                W_out = np.linalg.solve(h.T @ h + lam * np.eye(h.shape[1]),
                                        h.T @ one_hot(y_train))
                preds = np.argmax(ht @ W_out, axis=1)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        # Final eval
        h = X_train
        for layer in net.layers[:-1]:
            h = layer.forward(h)
        ht = X_test
        for layer in net.layers[:-1]:
            ht = layer.forward(ht)
        lam = 0.5
        W_out = np.linalg.solve(h.T @ h + lam * np.eye(h.shape[1]),
                                h.T @ one_hot(y_train))
        preds = np.argmax(ht @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("Optimal Transport Learning", final_acc, t.elapsed,
           "Sinkhorn divergence drives local weight updates. Novel combination.")

if __name__ == "__main__":
    main()
