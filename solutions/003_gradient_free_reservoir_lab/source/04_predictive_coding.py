"""
#04 - Predictive Coding Network
Each layer predicts the layer below. Learning minimizes prediction error locally.
Based on Rao & Ballard (1999) + modern deep PC networks.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu, sigmoid

class PCLayer:
    def __init__(self, in_dim, out_dim, lr=0.01):
        self.W = np.random.randn(out_dim, in_dim).astype(np.float32) * 0.05  # top-down weights
        self.b = np.zeros(in_dim, dtype=np.float32)
        self.lr = lr
        self.mu = None  # value neurons

    def predict(self, mu_above):
        """Top-down prediction of layer below."""
        return relu(mu_above @ self.W + self.b)

    def update_weights(self, mu_above, error_below):
        """Local Hebbian-like weight update from prediction errors."""
        self.W += self.lr * (mu_above.T @ error_below) / len(mu_above)
        self.b += self.lr * error_below.mean(axis=0)

class PCNetwork:
    def __init__(self, layer_sizes, lr=0.01, n_iter=20):
        self.layers = []
        self.sizes = layer_sizes
        self.n_iter = n_iter
        self.lr_inference = 0.1

        for i in range(len(layer_sizes)-1):
            self.layers.append(PCLayer(layer_sizes[i], layer_sizes[i+1], lr=lr))

    def infer_and_learn(self, x, target=None):
        n_layers = len(self.layers)

        # Initialize value neurons
        mus = [x]
        h = x
        for layer in self.layers:
            h = relu(h @ layer.W.T)
            mus.append(h)

        # If supervised, clamp top layer
        if target is not None:
            mus[-1] = target

        # Iterative inference: settle prediction errors
        for _ in range(self.n_iter):
            errors = []
            for i in range(n_layers):
                pred = self.layers[i].predict(mus[i+1])
                err = mus[i] - pred
                errors.append(err)

            # Update value neurons (not input or clamped output)
            for i in range(1, n_layers):
                # Error from below (I'm predicting poorly) + error from above (I'm being predicted poorly)
                grad = -errors[i-1] @ self.layers[i-1].W.T  # gradient from prediction above
                if i < n_layers:
                    grad += errors[i]  # prediction error at this level

                if target is not None and i == n_layers:
                    continue  # don't update clamped layer
                mus[i] -= self.lr_inference * grad

        # Weight updates (local!)
        for i in range(n_layers):
            self.layers[i].update_weights(mus[i+1], errors[i])

        return mus

    def predict(self, x, n_classes=10):
        """For classification: try each label, find lowest total error."""
        best_error = np.full(len(x), np.inf)
        predictions = np.zeros(len(x), dtype=int)

        for c in range(n_classes):
            target = np.zeros((len(x), n_classes), dtype=np.float32)
            target[:, c] = 1.0

            mus = [x]
            h = x
            for layer in self.layers:
                h = relu(h @ layer.W.T)
                mus.append(h)
            mus[-1] = target

            total_error = np.zeros(len(x))
            for i in range(len(self.layers)):
                pred = self.layers[i].predict(mus[i+1])
                err = np.sum((mus[i] - pred) ** 2, axis=1)
                total_error += err

            better = total_error < best_error
            predictions[better] = c
            best_error[better] = total_error[better]

        return predictions

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=5000, n_test=1000)

    net = PCNetwork([784, 300, 10], lr=0.005, n_iter=10)
    n_epochs = 15
    batch_size = 64

    with Timer("Predictive Coding") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                target = one_hot(y_train[idx])
                net.infer_and_learn(X_train[idx], target)

            if (epoch + 1) % 5 == 0:
                preds = net.predict(X_test[:500])
                acc = accuracy(preds, y_test[:500])
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        preds = net.predict(X_test)
        final_acc = accuracy(preds, y_test)

    report("Predictive Coding Network", final_acc, t.elapsed,
           "Local prediction errors, iterative inference. Brain-like.")

if __name__ == "__main__":
    main()
