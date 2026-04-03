"""
#16 - HYBRID: Entropy-Gated Tropical Network (ORIGINAL INVENTION)
Combine tropical (max-plus) algebra with entropy-gated plasticity.
Idea: The tropical max operation naturally creates competition.
Entropy gating ensures neurons stay in optimal learning regime.
The max-plus structure gives us piecewise-linear decision boundaries
that are adjusted ONLY when the entropy gate is open.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

def neuron_entropy(h, eps=1e-8):
    h_pos = np.abs(h) + eps
    p = h_pos / h_pos.sum(axis=0, keepdims=True)
    entropy = -np.sum(p * np.log(p + eps), axis=0)
    return entropy / (np.log(len(h)) + eps)

class EntropyTropicalLayer:
    def __init__(self, in_dim, out_dim, lr=0.01, e_low=0.3, e_high=0.85):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.1
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr
        self.e_low = e_low
        self.e_high = e_high

    def tropical_forward(self, x):
        """Max-plus forward: h_j = max_i(x_i + W_ij) + b_j"""
        # Vectorized: expand dims and broadcast
        extended = x[:, :, None] + self.W[None, :, :]  # (batch, in, out)
        h = np.max(extended, axis=1) + self.b  # (batch, out)
        winners = np.argmax(extended, axis=1)  # (batch, out) - which input won
        return h, winners

    def update(self, x, h, winners):
        """Entropy-gated tropical weight update."""
        ent = neuron_entropy(h)
        gate = np.where((ent > self.e_low) & (ent < self.e_high), 1.0, 0.05)

        batch_size = len(x)
        dW = np.zeros_like(self.W)

        # For each output neuron, update the winning input's weight
        for j in range(self.W.shape[1]):
            if gate[j] < 0.1:
                continue  # Skip gated neurons

            for i in range(batch_size):
                w = winners[i, j]
                # Competitive: strengthen winner, weaken others slightly
                dW[w, j] += h[i, j] * 0.01
                dW[:, j] -= 0.001  # decay

        self.W += self.lr * gate[None, :] * dW / batch_size

        # Normalize columns
        col_norms = np.linalg.norm(self.W, axis=0, keepdims=True) + 1e-8
        self.W /= col_norms

        return ent

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    layer1 = EntropyTropicalLayer(784, 500, lr=0.02, e_low=0.25, e_high=0.9)
    layer2 = EntropyTropicalLayer(500, 300, lr=0.02, e_low=0.25, e_high=0.9)

    n_epochs = 25
    batch_size = 256

    with Timer("Entropy-Gated Tropical") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                x = X_train[idx]

                h1, w1 = layer1.tropical_forward(x)
                h1_act = np.maximum(h1, 0)  # ReLU on top of tropical
                layer1.update(x, h1_act, w1)

                h2, w2 = layer2.tropical_forward(h1_act)
                h2_act = np.maximum(h2, 0)
                layer2.update(h1_act, h2_act, w2)

            if (epoch + 1) % 5 == 0:
                h1, _ = layer1.tropical_forward(X_train)
                h1 = np.maximum(h1, 0)
                h2, _ = layer2.tropical_forward(h1)
                h2 = np.maximum(h2, 0)

                h1t, _ = layer1.tropical_forward(X_test)
                h1t = np.maximum(h1t, 0)
                h2t, _ = layer2.tropical_forward(h1t)
                h2t = np.maximum(h2t, 0)

                lam = 0.5
                W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                        h2.T @ one_hot(y_train))
                preds = np.argmax(h2t @ W_out, axis=1)
                acc = accuracy(preds, y_test)

                e1 = neuron_entropy(h1[:1000])
                e2 = neuron_entropy(h2[:1000])
                print(f"  Epoch {epoch+1}: {acc:.2f}% | Entropy L1={e1.mean():.3f} L2={e2.mean():.3f}")

        # Final eval
        h1, _ = layer1.tropical_forward(X_train)
        h1 = np.maximum(h1, 0)
        h2, _ = layer2.tropical_forward(h1)
        h2 = np.maximum(h2, 0)
        h1t, _ = layer1.tropical_forward(X_test)
        h1t = np.maximum(h1t, 0)
        h2t, _ = layer2.tropical_forward(h1t)
        h2t = np.maximum(h2t, 0)

        lam = 0.3
        W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                h2.T @ one_hot(y_train))
        preds = np.argmax(h2t @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("Entropy-Gated Tropical (HYBRID)", final_acc, t.elapsed,
           "ORIGINAL: Tropical max-plus + entropy gating. Piecewise-linear + optimal plasticity.")

if __name__ == "__main__":
    main()
