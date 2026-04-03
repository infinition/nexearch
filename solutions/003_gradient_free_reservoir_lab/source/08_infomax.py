"""
#08 - Information-Theoretic Learning (InfoMax / HSIC)
Maximize mutual information between input and representation using HSIC.
No gradients: use kernel trick + closed-form or perturbation updates.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu

def rbf_kernel(X, sigma=1.0):
    """Gaussian RBF kernel matrix."""
    sq_dists = np.sum(X**2, axis=1, keepdims=True) - 2 * X @ X.T + np.sum(X**2, axis=1)
    return np.exp(-sq_dists / (2 * sigma**2))

def hsic(K1, K2):
    """Hilbert-Schmidt Independence Criterion (unbiased estimator)."""
    n = len(K1)
    H = np.eye(n) - np.ones((n, n)) / n
    return np.trace(K1 @ H @ K2 @ H) / ((n - 1) ** 2)

class HSICLayer:
    def __init__(self, in_dim, out_dim, lr=0.01):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.05
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr

    def forward(self, x):
        return relu(x @ self.W + self.b)

    def hsic_update(self, x, y_kernel, sigma_h=1.0):
        """Update weights to maximize HSIC between hidden activations and labels."""
        h = self.forward(x)
        K_h = rbf_kernel(h, sigma=sigma_h)
        base_hsic = hsic(K_h, y_kernel)

        # Perturbation gradient
        n_perturb = 15
        sigma = 0.01
        grad_W = np.zeros_like(self.W)
        grad_b = np.zeros_like(self.b)

        for _ in range(n_perturb):
            noise_W = np.random.randn(*self.W.shape).astype(np.float32)
            noise_b = np.random.randn(*self.b.shape).astype(np.float32)

            h_pert = relu(x @ (self.W + sigma * noise_W) + self.b + sigma * noise_b)
            K_pert = rbf_kernel(h_pert, sigma=sigma_h)
            pert_hsic = hsic(K_pert, y_kernel)

            grad_W += (pert_hsic - base_hsic) / sigma * noise_W
            grad_b += (pert_hsic - base_hsic) / sigma * noise_b

        grad_W /= n_perturb
        grad_b /= n_perturb

        # Maximize HSIC (gradient ascent)
        self.W += self.lr * grad_W
        self.b += self.lr * grad_b

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=3000, n_test=1000)

    layer1 = HSICLayer(784, 300, lr=0.02)
    layer2 = HSICLayer(300, 100, lr=0.02)

    n_epochs = 15
    batch_size = 200  # HSIC needs O(n^2) so keep batches small

    with Timer("InfoMax (HSIC)") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                y_oh = one_hot(y_train[idx])
                K_y = rbf_kernel(y_oh, sigma=0.5)

                # Layer 1: maximize HSIC(h1, y)
                layer1.hsic_update(X_train[idx], K_y, sigma_h=1.0)

                # Layer 2: maximize HSIC(h2, y)
                h1 = layer1.forward(X_train[idx])
                layer2.hsic_update(h1, K_y, sigma_h=1.0)

            if (epoch + 1) % 5 == 0:
                h1 = layer1.forward(X_train)
                h2 = layer2.forward(h1)
                h1t = layer1.forward(X_test)
                h2t = layer2.forward(h1t)

                lam = 1.0
                W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                        h2.T @ one_hot(y_train))
                preds = np.argmax(h2t @ W_out, axis=1)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        # Final
        h1 = layer1.forward(X_train)
        h2 = layer2.forward(h1)
        h1t = layer1.forward(X_test)
        h2t = layer2.forward(h1t)
        lam = 0.5
        W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                h2.T @ one_hot(y_train))
        preds = np.argmax(h2t @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("InfoMax (HSIC)", final_acc, t.elapsed,
           "Maximize HSIC between representations and labels. Info-theoretic.")

if __name__ == "__main__":
    main()
