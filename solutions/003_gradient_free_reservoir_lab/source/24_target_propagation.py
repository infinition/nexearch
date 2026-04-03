"""
#24 - Difference Target Propagation (DTP)
Each layer learns an inverse mapping. Targets computed by inverting top-down signal.
Reported: 99.22% on MNIST! Key: each layer has an autoencoder-like inverse.
No weight transport, purely local updates per layer.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu, softmax

class DTPLayer:
    def __init__(self, in_dim, out_dim, lr_f=0.01, lr_g=0.01):
        # Forward weights
        self.W_f = np.random.randn(in_dim, out_dim).astype(np.float32) * np.sqrt(2.0 / in_dim)
        self.b_f = np.zeros(out_dim, dtype=np.float32)
        # Inverse (feedback) weights - LEARNED, not random
        self.W_g = np.random.randn(out_dim, in_dim).astype(np.float32) * np.sqrt(2.0 / out_dim)
        self.b_g = np.zeros(in_dim, dtype=np.float32)
        self.lr_f = lr_f
        self.lr_g = lr_g

    def forward(self, x):
        return relu(x @ self.W_f + self.b_f)

    def inverse(self, h):
        return relu(h @ self.W_g + self.b_g)

    def update_inverse(self, x, h):
        """Train inverse to reconstruct input from output (autoencoder objective)."""
        x_recon = self.inverse(h)
        error = x - x_recon
        # Local gradient for inverse weights
        mask = (x_recon > 0).astype(np.float32)  # ReLU derivative
        delta = error * mask
        self.W_g += self.lr_g * (h.T @ delta) / len(x)
        self.b_g += self.lr_g * delta.mean(axis=0)

    def update_forward(self, x, target):
        """Update forward weights to move output toward target."""
        h = self.forward(x)
        error = target - h
        mask = (h > 0).astype(np.float32)
        delta = error * mask
        self.W_f += self.lr_f * (x.T @ delta) / len(x)
        self.b_f += self.lr_f * delta.mean(axis=0)

class DTPNetwork:
    def __init__(self, layer_sizes, lr_f=0.005, lr_g=0.005):
        self.layers = []
        for i in range(len(layer_sizes) - 1):
            self.layers.append(DTPLayer(layer_sizes[i], layer_sizes[i+1], lr_f, lr_g))

    def forward(self, x):
        activations = [x]
        h = x
        for layer in self.layers:
            h = layer.forward(h)
            activations.append(h)
        return activations

    def compute_targets(self, activations, y_oh):
        """Compute local targets via difference target propagation."""
        n = len(self.layers)
        targets = [None] * (n + 1)

        # Top layer target is the label
        targets[n] = y_oh

        # Propagate targets backward through inverse mappings
        for i in range(n - 1, 0, -1):
            # DTP: target_i = activation_i + g_i(target_{i+1}) - g_i(activation_{i+1})
            # This is the "difference" correction that makes DTP work
            h_inv_target = self.layers[i].inverse(targets[i + 1])
            h_inv_actual = self.layers[i].inverse(activations[i + 1])
            targets[i] = activations[i] + h_inv_target - h_inv_actual

        return targets

    def train_step(self, x, y_oh):
        # Forward pass
        activations = self.forward(x)

        # Compute local targets
        targets = self.compute_targets(activations, y_oh)

        # Update each layer locally (no backprop!)
        for i in range(len(self.layers)):
            # Update forward weights toward local target
            self.layers[i].update_forward(activations[i], targets[i + 1])
            # Update inverse weights (reconstruction objective)
            self.layers[i].update_inverse(activations[i], activations[i + 1])

    def predict(self, x):
        h = x
        for layer in self.layers:
            h = layer.forward(h)
        return np.argmax(h, axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=5000, n_test=1000)

    net = DTPNetwork([784, 200, 10], lr_f=0.03, lr_g=0.01)
    n_epochs = 15
    batch_size = 256

    with Timer("Difference Target Propagation") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i + batch_size]
                net.train_step(X_train[idx], one_hot(y_train[idx]))

            if (epoch + 1) % 5 == 0:
                preds = net.predict(X_test)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        preds = net.predict(X_test)
        final_acc = accuracy(preds, y_test)

    report("Difference Target Propagation", final_acc, t.elapsed,
           "Learned inverse mappings, DTP correction. Purely local. Literature: 99.22%")

if __name__ == "__main__":
    main()
