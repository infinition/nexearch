"""
#17 - HYBRID: Hyperdimensional Predictive Coding (ORIGINAL INVENTION)
Combine HDC's encoding with predictive coding's error-driven learning.
Idea: Encode inputs into HD space, then use prediction errors in HD space
to drive learning. The HD encoding provides robust representations,
while predictive coding provides the learning signal.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

class HDEncoder:
    def __init__(self, input_dim, hd_dim=4000, n_levels=30):
        self.hd_dim = hd_dim
        self.basis = np.random.choice([-1, 1], size=(input_dim, hd_dim)).astype(np.float32)
        self.levels = self._make_levels(n_levels, hd_dim)
        self.n_levels = n_levels

    def _make_levels(self, n_levels, hd_dim):
        levels = np.zeros((n_levels, hd_dim), dtype=np.float32)
        levels[0] = np.random.choice([-1, 1], size=hd_dim)
        flip_per = hd_dim // (2 * n_levels)
        for i in range(1, n_levels):
            levels[i] = levels[i-1].copy()
            idx = np.random.choice(hd_dim, flip_per, replace=False)
            levels[i, idx] *= -1
        return levels

    def encode(self, x):
        level_idx = np.clip((x * (self.n_levels - 1)).astype(int), 0, self.n_levels - 1)
        encoded = np.zeros((len(x), self.hd_dim), dtype=np.float32)
        for i in range(x.shape[1]):
            encoded += self.basis[i] * self.levels[level_idx[:, i]]
        return np.sign(encoded)

class HDPredictiveLayer:
    def __init__(self, hd_dim, out_dim, lr=0.01):
        self.W = np.random.randn(hd_dim, out_dim).astype(np.float32) * 0.01
        self.lr = lr

    def predict(self, h):
        return h @ self.W

    def update(self, h, prediction_error):
        """Update based on prediction error (local learning)."""
        self.W += self.lr * (h.T @ prediction_error) / len(h)

class HDPredictiveCoding:
    def __init__(self, input_dim, hd_dim=4000, hidden_dim=500, n_classes=10):
        self.encoder = HDEncoder(input_dim, hd_dim)

        # Prediction layers in HD space
        self.layer1 = HDPredictiveLayer(hd_dim, hidden_dim, lr=0.01)
        self.layer2 = HDPredictiveLayer(hidden_dim, n_classes, lr=0.01)

        # Feedback prediction (top-down)
        self.feedback = HDPredictiveLayer(n_classes, hidden_dim, lr=0.005)

    def train_step(self, x, y_oh):
        # Encode to HD space
        hd = self.encoder.encode(x)

        # Forward predictions
        h1 = np.tanh(self.layer1.predict(hd))
        h2_pred = self.layer2.predict(h1)

        # Prediction errors
        error_output = y_oh - h2_pred
        h1_feedback = np.tanh(self.feedback.predict(y_oh))
        error_hidden = h1_feedback - h1

        # Local updates
        self.layer2.update(h1, error_output)
        self.layer1.update(hd, error_hidden)
        self.feedback.update(y_oh, error_hidden * -1)

    def predict(self, x):
        hd = self.encoder.encode(x)
        h1 = np.tanh(self.layer1.predict(hd))
        h2 = self.layer2.predict(h1)
        return np.argmax(h2, axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    net = HDPredictiveCoding(784, hd_dim=4000, hidden_dim=300, n_classes=10)
    n_epochs = 20
    batch_size = 128

    with Timer("HD Predictive Coding") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                net.train_step(X_train[idx], one_hot(y_train[idx]))

            if (epoch + 1) % 5 == 0:
                preds = net.predict(X_test)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        preds = net.predict(X_test)
        final_acc = accuracy(preds, y_test)

    report("HD Predictive Coding (HYBRID)", final_acc, t.elapsed,
           "ORIGINAL: HDC encoding + predictive coding learning. Robust + adaptive.")

if __name__ == "__main__":
    main()
