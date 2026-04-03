"""
#14 - Entropy-Gated Local Learning (Your previous discovery!)
Local entropy as a gating signal for Hebbian updates.
Neurons learn when their entropy is neither too high nor too low.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu

def neuron_entropy(h, eps=1e-8):
    """Compute entropy of each neuron's activation distribution across batch."""
    # Normalize activations to probabilities per neuron
    h_pos = np.abs(h) + eps
    p = h_pos / h_pos.sum(axis=0, keepdims=True)
    entropy = -np.sum(p * np.log(p + eps), axis=0)
    max_entropy = np.log(len(h))
    return entropy / (max_entropy + eps)  # normalized 0-1

class EntropyGatedLayer:
    def __init__(self, in_dim, out_dim, lr=0.01, entropy_low=0.3, entropy_high=0.8):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.05
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr
        self.e_low = entropy_low
        self.e_high = entropy_high

    def forward(self, x):
        return relu(x @ self.W + self.b)

    def update(self, x, h, target_signal=None):
        """Entropy-gated Hebbian update."""
        # Compute entropy gate
        ent = neuron_entropy(h)
        gate = np.where(
            (ent > self.e_low) & (ent < self.e_high),
            1.0,  # Goldilocks zone: learn
            0.1   # Outside: barely learn
        )

        # Hebbian update with entropy gating
        if target_signal is not None:
            # Supervised: push representations toward target
            error = target_signal - h
            dW = (x.T @ (error * gate[None, :])) / len(x)
        else:
            # Unsupervised: competitive Hebbian
            dW = (x.T @ (h * gate[None, :])) / len(x)
            # Anti-Hebbian decorrelation
            dW -= self.W * np.mean(h ** 2, axis=0, keepdims=True) * gate[None, :] * 0.1

        self.W += self.lr * dW
        self.b += self.lr * np.mean(h * gate[None, :], axis=0) * 0.1

        # Normalize
        norms = np.linalg.norm(self.W, axis=0, keepdims=True) + 1e-8
        self.W /= norms

        return ent

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    layer1 = EntropyGatedLayer(784, 500, lr=0.01, entropy_low=0.3, entropy_high=0.85)
    layer2 = EntropyGatedLayer(500, 300, lr=0.01, entropy_low=0.3, entropy_high=0.85)

    n_epochs = 25
    batch_size = 256

    with Timer("Entropy-Gated Local Learning") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                x = X_train[idx]

                h1 = layer1.forward(x)
                layer1.update(x, h1)

                h2 = layer2.forward(h1)
                layer2.update(h1, h2)

            if (epoch + 1) % 5 == 0:
                h1 = layer1.forward(X_train)
                h2 = layer2.forward(h1)
                h1t = layer1.forward(X_test)
                h2t = layer2.forward(h1t)

                lam = 0.5
                W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                        h2.T @ one_hot(y_train))
                preds = np.argmax(h2t @ W_out, axis=1)
                acc = accuracy(preds, y_test)

                e1 = neuron_entropy(layer1.forward(X_train[:1000]))
                e2 = neuron_entropy(layer2.forward(layer1.forward(X_train[:1000])))
                print(f"  Epoch {epoch+1}: {acc:.2f}% | Entropy L1={e1.mean():.3f} L2={e2.mean():.3f}")

        h1 = layer1.forward(X_train)
        h2 = layer2.forward(h1)
        h1t = layer1.forward(X_test)
        h2t = layer2.forward(h1t)
        lam = 0.3
        W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                h2.T @ one_hot(y_train))
        preds = np.argmax(h2t @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("Entropy-Gated Local Learning", final_acc, t.elapsed,
           "Entropy as learning gate. Goldilocks zone for plasticity. NOVEL.")

if __name__ == "__main__":
    main()
