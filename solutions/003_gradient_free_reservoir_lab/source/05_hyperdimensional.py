"""
#05 - Hyperdimensional Computing (Vector Symbolic Architecture)
Encode data into high-dimensional binary/bipolar vectors.
Classification via bundling + similarity. No weights to train.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, accuracy, report, Timer

class HDClassifier:
    def __init__(self, input_dim, hd_dim=10000, n_classes=10, n_levels=100):
        self.hd_dim = hd_dim
        self.n_classes = n_classes
        self.n_levels = n_levels

        # Random projection basis vectors (one per input feature)
        self.basis = np.random.choice([-1, 1], size=(input_dim, hd_dim)).astype(np.float32)

        # Level hypervectors for encoding continuous values
        self.levels = self._create_level_hvs(n_levels, hd_dim)

        # Class prototypes
        self.prototypes = np.zeros((n_classes, hd_dim), dtype=np.float32)

    def _create_level_hvs(self, n_levels, hd_dim):
        """Create level HVs by progressively flipping bits."""
        levels = np.zeros((n_levels, hd_dim), dtype=np.float32)
        levels[0] = np.random.choice([-1, 1], size=hd_dim)

        flip_per_step = hd_dim // (2 * n_levels)
        for i in range(1, n_levels):
            levels[i] = levels[i-1].copy()
            flip_idx = np.random.choice(hd_dim, flip_per_step, replace=False)
            levels[i, flip_idx] *= -1

        return levels

    def encode(self, x):
        """Encode a batch of samples into HD space."""
        batch_size = len(x)
        # Quantize to level indices
        level_idx = np.clip((x * (self.n_levels - 1)).astype(int), 0, self.n_levels - 1)

        # For each sample, bind basis with level and bundle
        encoded = np.zeros((batch_size, self.hd_dim), dtype=np.float32)
        for i in range(x.shape[1]):
            lvl_hvs = self.levels[level_idx[:, i]]  # (batch, hd_dim)
            encoded += self.basis[i] * lvl_hvs  # bind and accumulate

        # Bipolarize
        encoded = np.sign(encoded)
        encoded[encoded == 0] = 1
        return encoded

    def train(self, X, y, n_epochs=5):
        """Train by bundling encoded samples per class."""
        for epoch in range(n_epochs):
            self.prototypes[:] = 0
            encoded = self.encode(X)
            for c in range(self.n_classes):
                mask = y == c
                if mask.any():
                    self.prototypes[c] = encoded[mask].sum(axis=0)

            # Bipolarize prototypes
            self.prototypes = np.sign(self.prototypes)
            self.prototypes[self.prototypes == 0] = 1

            # Retraining: check mistakes and adjust
            if epoch > 0:
                preds = self.predict(X)
                wrong = preds != y
                if wrong.any():
                    wrong_enc = encoded[wrong]
                    for i, idx in enumerate(np.where(wrong)[0]):
                        # Add to correct, subtract from predicted
                        self.prototypes[y[idx]] += wrong_enc[i]
                        self.prototypes[preds[idx]] -= wrong_enc[i]

                    self.prototypes = np.sign(self.prototypes)
                    self.prototypes[self.prototypes == 0] = 1

    def predict(self, X):
        encoded = self.encode(X)
        # Cosine similarity with prototypes
        sims = encoded @ self.prototypes.T
        return np.argmax(sims, axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    clf = HDClassifier(784, hd_dim=10000, n_classes=10, n_levels=50)

    with Timer("Hyperdimensional Computing") as t:
        clf.train(X_train, y_train, n_epochs=5)
        preds = clf.predict(X_test)
        final_acc = accuracy(preds, y_test)

    report("Hyperdimensional Computing", final_acc, t.elapsed,
           "No weights, no gradients. Encode-bind-bundle paradigm.")

if __name__ == "__main__":
    main()
