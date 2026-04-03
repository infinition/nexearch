"""
#01 - Forward-Forward Algorithm (Hinton, 2022)
Each layer has its own objective: maximize goodness for positive data,
minimize for negative data. No backprop needed.
Goodness = sum of squared activations.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu

class FFLayer:
    def __init__(self, in_dim, out_dim, lr=0.03, threshold=2.0):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.05
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr
        self.threshold = threshold

    def forward(self, x):
        # Normalize input
        x_norm = x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-8)
        h = relu(x_norm @ self.W + self.b)
        return h

    def goodness(self, h):
        return np.sum(h ** 2, axis=1)

    def train_step(self, x_pos, x_neg):
        h_pos = self.forward(x_pos)
        h_neg = self.forward(x_neg)

        g_pos = self.goodness(h_pos)
        g_neg = self.goodness(h_neg)

        # Probabilities
        p_pos = 1.0 / (1.0 + np.exp(-(g_pos - self.threshold)))
        p_neg = 1.0 / (1.0 + np.exp(-(g_neg - self.threshold)))

        # Local update: push positive goodness up, negative down
        x_pos_norm = x_pos / (np.linalg.norm(x_pos, axis=1, keepdims=True) + 1e-8)
        x_neg_norm = x_neg / (np.linalg.norm(x_neg, axis=1, keepdims=True) + 1e-8)

        # Gradient of goodness w.r.t. pre-activation is 2*h for ReLU active units
        delta_pos = (1 - p_pos)[:, None] * h_pos * 2
        delta_neg = -p_neg[:, None] * h_neg * 2

        self.W += self.lr * (x_pos_norm.T @ delta_pos + x_neg_norm.T @ delta_neg) / len(x_pos)
        self.b += self.lr * (delta_pos.mean(axis=0) + delta_neg.mean(axis=0))

        return h_pos, h_neg

def make_positive(X, y, n_classes=10):
    """Overlay correct label on first pixels."""
    x = X.copy()
    oh = one_hot(y, n_classes)
    x[:, :n_classes] = oh * 0.5
    return x

def make_negative(X, y, n_classes=10):
    """Overlay random wrong label on first pixels."""
    x = X.copy()
    wrong = (y + np.random.randint(1, n_classes, size=len(y))) % n_classes
    oh = one_hot(wrong, n_classes)
    x[:, :n_classes] = oh * 0.5
    return x

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    layers = [
        FFLayer(784, 500, lr=0.05, threshold=2.0),
        FFLayer(500, 500, lr=0.05, threshold=2.0),
    ]

    n_epochs = 30
    batch_size = 128

    with Timer("Forward-Forward") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                x_pos = make_positive(X_train[idx], y_train[idx])
                x_neg = make_negative(X_train[idx], y_train[idx])

                h_pos, h_neg = x_pos, x_neg
                for layer in layers:
                    h_pos, h_neg = layer.train_step(h_pos, h_neg)

            if (epoch + 1) % 10 == 0:
                acc = evaluate(layers, X_test, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

    final_acc = evaluate(layers, X_test, y_test)
    report("Forward-Forward (Hinton)", final_acc, t.elapsed,
           "Local learning, no backprop. Label overlay method.")

def evaluate(layers, X_test, y_test, n_classes=10):
    """Try each class label, pick the one with highest total goodness."""
    best_goodness = np.full(len(X_test), -np.inf)
    predictions = np.zeros(len(X_test), dtype=int)

    for c in range(n_classes):
        x = X_test.copy()
        oh = one_hot(np.full(len(X_test), c), n_classes)
        x[:, :n_classes] = oh * 0.5

        h = x
        total_goodness = np.zeros(len(X_test))
        for layer in layers:
            h = layer.forward(h)
            total_goodness += np.sum(h ** 2, axis=1)

        better = total_goodness > best_goodness
        predictions[better] = c
        best_goodness[better] = total_goodness[better]

    return accuracy(predictions, y_test)

if __name__ == "__main__":
    main()
