"""
#27 - Three-Factor Neuromodulated Learning
dw = eta * M * eligibility_trace
- Pre-post Hebbian trace (local)
- Global reward/error signal M (dopamine-like)
Reported: ~95% on MNIST with single-layer SNNs.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu

class NeuromodulatedLayer:
    def __init__(self, in_dim, out_dim, lr=0.01, trace_decay=0.9):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * np.sqrt(2.0 / in_dim)
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr
        self.trace_decay = trace_decay
        # Eligibility traces
        self.trace_W = np.zeros_like(self.W)
        self.trace_b = np.zeros_like(self.b)

    def forward(self, x):
        return relu(x @ self.W + self.b)

    def compute_trace(self, x, h):
        """Hebbian eligibility trace: pre * post (local computation)."""
        # Decay old trace
        self.trace_W *= self.trace_decay
        self.trace_b *= self.trace_decay
        # Add new Hebbian trace
        mask = (h > 0).astype(np.float32)
        self.trace_W += (x.T @ (h * mask)) / len(x)
        self.trace_b += (h * mask).mean(axis=0)

    def modulated_update(self, modulator):
        """Apply modulator (reward signal) to eligibility traces."""
        # Three-factor rule: dw = eta * M * trace
        self.W += self.lr * modulator * self.trace_W
        self.b += self.lr * modulator * self.trace_b

class ThreeFactorNetwork:
    def __init__(self, layer_sizes, lr=0.005):
        self.layers = []
        for i in range(len(layer_sizes) - 1):
            self.layers.append(NeuromodulatedLayer(layer_sizes[i], layer_sizes[i+1], lr))

    def forward(self, x):
        activations = [x]
        h = x
        for layer in self.layers:
            h = layer.forward(h)
            activations.append(h)
        return activations

    def train_step(self, x, y):
        activations = self.forward(x)
        output = activations[-1]

        # Compute prediction and reward
        preds = np.argmax(output, axis=1)
        correct = (preds == y).astype(np.float32)

        # Reward signal: +1 for correct, -1 for wrong (per-sample)
        # But we use a scalar modulator for simplicity
        reward = correct.mean() * 2 - 1  # range [-1, 1]

        # Also compute a per-class modulator (more informative)
        y_oh = one_hot(y)
        # Output goodness per sample
        target_activation = np.sum(output * y_oh, axis=1)
        baseline = target_activation.mean()
        per_sample_reward = (target_activation - baseline)

        # Compute eligibility traces (local Hebbian)
        for i, layer in enumerate(self.layers):
            layer.compute_trace(activations[i], activations[i+1])

        # Apply modulated update
        # Use average reward for hidden layers, per-sample for output
        for i, layer in enumerate(self.layers):
            if i < len(self.layers) - 1:
                layer.modulated_update(reward)
            else:
                # Output layer gets more specific signal
                # Push correct class up, incorrect down
                error = y_oh - (output > 0).astype(np.float32) * 0.1
                layer.W += layer.lr * (activations[i].T @ error) / len(x)
                layer.b += layer.lr * error.mean(axis=0)

    def predict(self, x):
        h = x
        for layer in self.layers:
            h = layer.forward(h)
        return np.argmax(h, axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    net = ThreeFactorNetwork([784, 300, 10], lr=0.02)
    n_epochs = 20
    batch_size = 128

    with Timer("Three-Factor Neuromodulated") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i + batch_size]
                net.train_step(X_train[idx], y_train[idx])

            if (epoch + 1) % 5 == 0:
                preds = net.predict(X_test)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        preds = net.predict(X_test)
        final_acc = accuracy(preds, y_test)

    report("Three-Factor Neuromodulated Learning", final_acc, t.elapsed,
           "Eligibility trace + global reward signal. Dopamine-like.")

if __name__ == "__main__":
    main()
