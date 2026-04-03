"""
#15 - Fractal/Chaos Attractor Learning
Use iterated function systems to create fractal attractors for each class.
Learning = tuning attractor parameters so inputs converge to class basins.
HIGHLY ORIGINAL - combining dynamical systems theory with classification.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, accuracy, report, Timer

class FractalClassifier:
    def __init__(self, input_dim, hidden_dim=100, n_classes=10, n_iters=10):
        self.n_classes = n_classes
        self.n_iters = n_iters
        self.hidden_dim = hidden_dim

        # Projection to hidden space
        self.P = np.random.randn(input_dim, hidden_dim).astype(np.float32) * 0.01

        # Per-class attractor parameters: contraction maps
        self.A = []  # Linear part
        self.c = []  # Translation
        for _ in range(n_classes):
            # Contractive map: spectral radius < 1
            a = np.random.randn(hidden_dim, hidden_dim).astype(np.float32) * 0.1
            # Ensure contraction
            u, s, vt = np.linalg.svd(a, full_matrices=False)
            s = np.clip(s, 0, 0.8)  # Spectral radius < 1
            a = u @ np.diag(s) @ vt
            self.A.append(a)
            self.c.append(np.random.randn(hidden_dim).astype(np.float32) * 0.1)

    def iterate(self, x, class_idx):
        """Iterate the class attractor from initial point x."""
        h = x @ self.P
        trajectory_energy = np.zeros(len(x))

        for _ in range(self.n_iters):
            h_new = np.tanh(h @ self.A[class_idx] + self.c[class_idx])
            trajectory_energy += np.sum((h_new - h) ** 2, axis=1)
            h = h_new

        # Lower energy = better convergence = more likely this class
        return -trajectory_energy, h

    def predict(self, x):
        best_score = np.full(len(x), -np.inf)
        predictions = np.zeros(len(x), dtype=int)

        for c in range(self.n_classes):
            score, _ = self.iterate(x, c)
            better = score > best_score
            predictions[better] = c
            best_score[better] = score[better]

        return predictions

    def train(self, X, y, n_epochs=20, lr=0.01, batch_size=128):
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X))
            for i in range(0, len(X), batch_size):
                idx = perm[i:i+batch_size]
                x_batch, y_batch = X[idx], y[idx]

                # For each class present in batch
                for c in range(self.n_classes):
                    mask_pos = y_batch == c
                    mask_neg = y_batch != c

                    if not mask_pos.any() or not mask_neg.any():
                        continue

                    # Perturbation-based update
                    n_perturb = 5
                    for _ in range(n_perturb):
                        # Perturb attractor parameters
                        dA = np.random.randn(*self.A[c].shape).astype(np.float32) * 0.01
                        dc = np.random.randn(*self.c[c].shape).astype(np.float32) * 0.01

                        # Original scores
                        score_pos, _ = self.iterate(x_batch[mask_pos], c)
                        score_neg, _ = self.iterate(x_batch[mask_neg], c)

                        # Perturbed scores
                        old_A, old_c = self.A[c].copy(), self.c[c].copy()
                        self.A[c] += dA
                        self.c[c] += dc

                        new_score_pos, _ = self.iterate(x_batch[mask_pos], c)
                        new_score_neg, _ = self.iterate(x_batch[mask_neg], c)

                        # We want: higher score for positive, lower for negative
                        improvement = (new_score_pos.mean() - score_pos.mean()) - \
                                     (new_score_neg.mean() - score_neg.mean())

                        self.A[c] = old_A
                        self.c[c] = old_c

                        if improvement > 0:
                            self.A[c] += lr * dA
                            self.c[c] += lr * dc

                    # Keep contractive
                    u, s, vt = np.linalg.svd(self.A[c], full_matrices=False)
                    s = np.clip(s, 0, 0.9)
                    self.A[c] = u @ np.diag(s) @ vt

            # Also update projection
            dP = np.random.randn(*self.P.shape).astype(np.float32) * 0.001
            old_P = self.P.copy()
            self.P += dP
            new_preds = self.predict(X[:500])
            new_acc = np.mean(new_preds == y[:500])
            self.P = old_P
            old_preds = self.predict(X[:500])
            old_acc = np.mean(old_preds == y[:500])
            if new_acc > old_acc:
                self.P += lr * dP

            if (epoch + 1) % 5 == 0:
                preds = self.predict(X[:1000])
                acc = np.mean(preds == y[:1000]) * 100
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=5000, n_test=1000)

    clf = FractalClassifier(784, hidden_dim=50, n_classes=10, n_iters=8)

    with Timer("Fractal/Chaos Attractor") as t:
        clf.train(X_train, y_train, n_epochs=20, lr=0.02, batch_size=256)
        preds = clf.predict(X_test)
        final_acc = accuracy(preds, y_test)

    report("Fractal/Chaos Attractor Learning", final_acc, t.elapsed,
           "Iterated function systems as classifiers. HIGHLY ORIGINAL.")

if __name__ == "__main__":
    main()
