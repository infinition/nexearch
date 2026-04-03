"""
#22 - Local Contrastive Learning (NOVEL COMBINATION)
Combine contrastive learning (SimCLR-like) with local-only updates.
Each layer learns to bring same-class representations closer and
push different-class ones apart, using only local information.
No backprop, no global loss. Uses cosine similarity locally.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu

def cosine_sim(a, b):
    """Cosine similarity between rows of a and b."""
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-8)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)
    return np.sum(a_norm * b_norm, axis=1)

class LocalContrastiveLayer:
    def __init__(self, in_dim, out_dim, lr=0.01, temperature=0.5):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.05
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr
        self.temp = temperature

    def forward(self, x):
        return relu(x @ self.W + self.b)

    def contrastive_update(self, x, h, labels):
        """Local contrastive: attract same-class, repel different-class."""
        batch_size = len(x)
        dW = np.zeros_like(self.W)

        # Normalize representations
        h_norm = h / (np.linalg.norm(h, axis=1, keepdims=True) + 1e-8)

        # For each sample, find positive and negative pairs
        for c in np.unique(labels):
            pos_mask = labels == c
            neg_mask = labels != c

            if pos_mask.sum() < 2 or neg_mask.sum() < 1:
                continue

            pos_h = h_norm[pos_mask]
            neg_h = h_norm[neg_mask]
            pos_x = x[pos_mask]

            # Positive mean representation
            pos_mean = pos_h.mean(axis=0, keepdims=True)
            # Negative mean representation
            neg_mean = neg_h.mean(axis=0, keepdims=True)

            # Push positive toward positive mean
            attract = pos_mean - pos_h  # attract direction
            # Push positive away from negative mean
            repel = pos_h - neg_mean  # repel direction

            # Combined signal
            signal = attract + 0.5 * repel
            # Apply ReLU derivative mask
            mask = (h[pos_mask] > 0).astype(np.float32)
            signal *= mask

            dW += (pos_x.T @ signal) / batch_size

        self.W += self.lr * dW
        self.b += self.lr * 0.01

        # Normalize columns
        norms = np.linalg.norm(self.W, axis=0, keepdims=True) + 1e-8
        self.W /= norms

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    layer1 = LocalContrastiveLayer(784, 500, lr=0.02, temperature=0.5)
    layer2 = LocalContrastiveLayer(500, 300, lr=0.02, temperature=0.5)

    n_epochs = 20
    batch_size = 256

    with Timer("Local Contrastive Learning") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                x = X_train[idx]
                y = y_train[idx]

                h1 = layer1.forward(x)
                layer1.contrastive_update(x, h1, y)

                h2 = layer2.forward(h1)
                layer2.contrastive_update(h1, h2, y)

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
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        h1 = layer1.forward(X_train)
        h2 = layer2.forward(h1)
        h1t = layer1.forward(X_test)
        h2t = layer2.forward(h1t)
        lam = 0.3
        W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                h2.T @ one_hot(y_train))
        preds = np.argmax(h2t @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("Local Contrastive Learning", final_acc, t.elapsed,
           "Contrastive (SimCLR-like) with purely local updates. NOVEL combo.")

if __name__ == "__main__":
    main()
