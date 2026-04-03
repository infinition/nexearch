"""
#29 - Mono-Forward Algorithm (2025)
Single forward pass. Each layer has its own local classifier.
No inter-layer gradient flow. Reported to BEAT backprop on MLPs!
Up to 41% less energy, 34% faster training.
Reference: arXiv:2501.09238
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu, softmax

class MonoForwardLayer:
    """Layer with its own local classifier head."""
    def __init__(self, in_dim, out_dim, n_classes, lr=0.01):
        # Feature transform
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * np.sqrt(2.0 / in_dim)
        self.b = np.zeros(out_dim, dtype=np.float32)
        # Local classifier
        self.W_cls = np.random.randn(out_dim, n_classes).astype(np.float32) * np.sqrt(2.0 / out_dim)
        self.b_cls = np.zeros(n_classes, dtype=np.float32)
        self.lr = lr

    def forward(self, x):
        h = relu(x @ self.W + self.b)
        logits = h @ self.W_cls + self.b_cls
        return h, logits

    def train_step(self, x, y_oh):
        """Local training: optimize this layer's classifier loss only."""
        batch_size = len(x)
        h, logits = self.forward(x)
        probs = softmax(logits)
        error = probs - y_oh

        # Update classifier head
        self.W_cls -= self.lr * (h.T @ error) / batch_size
        self.b_cls -= self.lr * error.mean(axis=0)

        # Update feature transform (gradient of local loss w.r.t. this layer only)
        dh = error @ self.W_cls.T
        dh *= (h > 0).astype(np.float32)
        self.W -= self.lr * (x.T @ dh) / batch_size
        self.b -= self.lr * dh.mean(axis=0)

        return h

class MonoForwardNetwork:
    def __init__(self, layer_sizes, n_classes=10, lr=0.01):
        self.layers = []
        for i in range(len(layer_sizes) - 1):
            self.layers.append(MonoForwardLayer(layer_sizes[i], layer_sizes[i+1], n_classes, lr))

    def train_step(self, x, y_oh):
        """Train each layer independently with its own local loss."""
        h = x
        for layer in self.layers:
            h = layer.train_step(h, y_oh)
            # IMPORTANT: h is detached - no gradient flows between layers
            # In numpy this is automatic since we just pass the array

    def predict(self, x):
        """Use the last layer's classifier for prediction."""
        h = x
        for layer in self.layers:
            h, logits = layer.forward(h)
        return np.argmax(logits, axis=1)

    def predict_ensemble(self, x):
        """Ensemble all local classifiers (better accuracy)."""
        h = x
        all_logits = []
        for layer in self.layers:
            h, logits = layer.forward(h)
            all_logits.append(softmax(logits))
        # Average probabilities
        avg_probs = np.mean(all_logits, axis=0)
        return np.argmax(avg_probs, axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)
    y_train_oh = one_hot(y_train)

    net = MonoForwardNetwork([784, 300, 200], n_classes=10, lr=0.02)
    n_epochs = 20
    batch_size = 128

    with Timer("Mono-Forward") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                net.train_step(X_train[idx], y_train_oh[idx])

            if (epoch + 1) % 5 == 0:
                preds = net.predict(X_test)
                acc = accuracy(preds, y_test)
                preds_ens = net.predict_ensemble(X_test)
                acc_ens = accuracy(preds_ens, y_test)
                print(f"  Epoch {epoch+1}: last={acc:.2f}% ensemble={acc_ens:.2f}%")

        preds = net.predict(X_test)
        acc_last = accuracy(preds, y_test)
        preds_ens = net.predict_ensemble(X_test)
        acc_ens = accuracy(preds_ens, y_test)
        final_acc = max(acc_last, acc_ens)

    report("Mono-Forward Algorithm", final_acc, t.elapsed,
           f"Local classifiers per layer. 2025. Last={acc_last:.1f}% Ensemble={acc_ens:.1f}%")

if __name__ == "__main__":
    main()
