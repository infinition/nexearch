"""
#11 - Thermodynamic Learning (Free Energy Minimization)
Treat network as a thermodynamic system. Minimize free energy locally.
Inspired by Boltzmann machines but with modern architecture.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, sigmoid

class ThermodynamicLayer:
    def __init__(self, in_dim, out_dim, lr=0.01, temperature=1.0):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.05
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr
        self.T = temperature

    def energy(self, x, h):
        """Energy function: -x^T W h - b^T h"""
        return -np.sum(x @ self.W * h, axis=1) - np.sum(self.b * h, axis=1)

    def forward(self, x):
        """Compute probabilities and sample."""
        prob = sigmoid((x @ self.W + self.b) / self.T)
        return prob

    def gibbs_step(self, x, h):
        """One step of Gibbs sampling."""
        # P(h|x)
        prob_h = sigmoid((x @ self.W + self.b) / self.T)
        h_new = (np.random.rand(*prob_h.shape) < prob_h).astype(np.float32)
        return h_new, prob_h

    def contrastive_divergence(self, x, n_steps=1):
        """CD-k learning rule (local, no backprop)."""
        # Positive phase
        prob_h_pos = sigmoid((x @ self.W + self.b) / self.T)
        h_pos = (np.random.rand(*prob_h_pos.shape) < prob_h_pos).astype(np.float32)

        # Negative phase (Gibbs chain)
        h_neg = h_pos.copy()
        for _ in range(n_steps):
            # Reconstruct x
            x_neg = sigmoid(h_neg @ self.W.T / self.T)
            # Resample h
            prob_h_neg = sigmoid((x_neg @ self.W + self.b) / self.T)
            h_neg = (np.random.rand(*prob_h_neg.shape) < prob_h_neg).astype(np.float32)

        # Update (contrastive divergence)
        batch_size = len(x)
        self.W += self.lr * (x.T @ prob_h_pos - x_neg.T @ prob_h_neg) / batch_size
        self.b += self.lr * (prob_h_pos - prob_h_neg).mean(axis=0)

        # Cool down
        self.T = max(0.5, self.T * 0.999)

        return prob_h_pos

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    layer1 = ThermodynamicLayer(784, 500, lr=0.01, temperature=1.0)
    layer2 = ThermodynamicLayer(500, 200, lr=0.01, temperature=1.0)

    n_epochs = 15
    batch_size = 128

    with Timer("Thermodynamic Learning") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]

                h1 = layer1.contrastive_divergence(X_train[idx], n_steps=1)
                layer2.contrastive_divergence(h1, n_steps=1)

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

        h1 = layer1.forward(X_train)
        h2 = layer2.forward(h1)
        h1t = layer1.forward(X_test)
        h2t = layer2.forward(h1t)
        lam = 0.5
        W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                h2.T @ one_hot(y_train))
        preds = np.argmax(h2t @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("Thermodynamic Learning", final_acc, t.elapsed,
           "Free energy minimization, contrastive divergence, cooling schedule.")

if __name__ == "__main__":
    main()
