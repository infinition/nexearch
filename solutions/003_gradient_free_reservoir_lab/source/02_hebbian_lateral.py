"""
#02 - Competitive Hebbian Learning with Lateral Inhibition
Oja's rule + winner-take-all + readout layer (least squares).
Purely local, biologically plausible feature extraction.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, accuracy, report, Timer, relu

class HebbianLayer:
    def __init__(self, in_dim, out_dim, lr=0.01, k_winners=50):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.01
        self.lr = lr
        self.k_winners = k_winners

    def forward(self, x):
        h = x @ self.W
        # Winner-take-all: keep top k activations per sample
        if self.k_winners < h.shape[1]:
            thresholds = np.partition(h, -self.k_winners, axis=1)[:, -self.k_winners:].min(axis=1, keepdims=True)
            h = h * (h >= thresholds)
        return relu(h)

    def train_step(self, x):
        h = self.forward(x)
        # Oja's rule: dW = lr * (x^T h - diag(h^T h) W)
        # Simplified competitive Hebbian
        self.W += self.lr * (x.T @ h / len(x) - self.W * np.mean(h ** 2, axis=0, keepdims=True))
        # Normalize columns
        norms = np.linalg.norm(self.W, axis=0, keepdims=True) + 1e-8
        self.W /= norms
        return h

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    # Multi-layer Hebbian feature extractor
    layer1 = HebbianLayer(784, 1000, lr=0.005, k_winners=100)
    layer2 = HebbianLayer(1000, 500, lr=0.005, k_winners=50)

    n_epochs = 20
    batch_size = 256

    with Timer("Hebbian + Lateral Inhibition") as t:
        # Phase 1: Unsupervised feature learning
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                h1 = layer1.train_step(X_train[idx])
                layer2.train_step(h1)

            if (epoch + 1) % 5 == 0:
                # Quick eval
                h1 = layer1.forward(X_train)
                h2 = layer2.forward(h1)
                h1t = layer1.forward(X_test)
                h2t = layer2.forward(h1t)

                # Ridge regression readout (closed form, no gradients)
                lam = 1.0
                W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                        h2.T @ np.eye(10)[y_train])
                preds = np.argmax(h2t @ W_out, axis=1)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        # Final readout
        h1 = layer1.forward(X_train)
        h2 = layer2.forward(h1)
        h1t = layer1.forward(X_test)
        h2t = layer2.forward(h1t)

        lam = 0.1
        W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                h2.T @ np.eye(10)[y_train])
        preds = np.argmax(h2t @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("Hebbian + Lateral Inhibition", final_acc, t.elapsed,
           "Oja's rule, WTA competition, ridge regression readout.")

if __name__ == "__main__":
    main()
