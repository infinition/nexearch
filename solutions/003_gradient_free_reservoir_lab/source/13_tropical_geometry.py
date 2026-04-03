"""
#13 - Tropical Geometry Network
Replace standard algebra with tropical semiring: (max, +) instead of (+, *).
Neural networks become piecewise-linear maps. Learning = adjusting breakpoints.
This is an ORIGINAL COMBINATION: tropical algebra + competitive learning.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

class TropicalLayer:
    """Layer using tropical (max-plus) algebra."""
    def __init__(self, in_dim, out_dim, lr=0.01):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.1
        self.lr = lr

    def forward(self, x):
        """Tropical matrix multiplication: (max, +) instead of (+, *)."""
        # For each output j: h_j = max_i(x_i + W_ij)
        # This is equivalent to: x[:, :, None] + W[None, :, :]  -> max over axis 1
        h = np.zeros((len(x), self.W.shape[1]), dtype=np.float32)
        for j in range(self.W.shape[1]):
            h[:, j] = np.max(x + self.W[:, j], axis=1)
        return h

    def forward_with_argmax(self, x):
        """Forward with winner tracking for learning."""
        h = np.zeros((len(x), self.W.shape[1]), dtype=np.float32)
        winners = np.zeros((len(x), self.W.shape[1]), dtype=int)
        for j in range(self.W.shape[1]):
            vals = x + self.W[:, j]
            winners[:, j] = np.argmax(vals, axis=1)
            h[:, j] = np.max(vals, axis=1)
        return h, winners

    def tropical_update(self, x, h, winners, target_direction):
        """Update weights based on which input won the max competition."""
        batch_size = len(x)
        for j in range(self.W.shape[1]):
            for i in range(batch_size):
                w_idx = winners[i, j]
                # Move the winning weight in the target direction
                self.W[w_idx, j] += self.lr * target_direction[i, j]

class TropicalNet:
    def __init__(self, layer_sizes, lr=0.005):
        self.layers = []
        for i in range(len(layer_sizes)-1):
            self.layers.append(TropicalLayer(layer_sizes[i], layer_sizes[i+1], lr=lr))

    def forward(self, x):
        h = x
        for layer in self.layers:
            h = layer.forward(h)
        return h

    def train_step(self, x, y_oh):
        # Forward with tracking
        activations = [x]
        winners_list = []
        h = x
        for layer in self.layers:
            h, w = layer.forward_with_argmax(h)
            activations.append(h)
            winners_list.append(w)

        # Compute target direction at output
        output = activations[-1]
        # Simple: push correct class up, wrong classes down
        target_dir = -np.ones_like(output) * 0.1
        target_dir[np.arange(len(y_oh)), np.argmax(y_oh, axis=1)] = 1.0

        # Update last layer
        self.layers[-1].tropical_update(
            activations[-2], activations[-1], winners_list[-1], target_dir
        )

        # For hidden layers: propagate direction through argmax paths
        if len(self.layers) > 1:
            h_target = target_dir  # simplified propagation
            for l in range(len(self.layers)-2, -1, -1):
                # Project target direction backward through winner paths
                h_target_proj = np.zeros_like(activations[l+1])
                for j in range(h_target.shape[1]):
                    h_target_proj[:, j] = h_target[:, j]
                self.layers[l].tropical_update(
                    activations[l], activations[l+1], winners_list[l],
                    h_target_proj * 0.1
                )

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=5000, n_test=1000)

    net = TropicalNet([784, 200, 10], lr=0.003)
    n_epochs = 20
    batch_size = 64

    with Timer("Tropical Geometry Network") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                net.train_step(X_train[idx], one_hot(y_train[idx]))

            if (epoch + 1) % 5 == 0:
                output = net.forward(X_test)
                preds = np.argmax(output, axis=1)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        output = net.forward(X_test)
        preds = np.argmax(output, axis=1)
        final_acc = accuracy(preds, y_test)

    report("Tropical Geometry Network", final_acc, t.elapsed,
           "Max-plus algebra, piecewise-linear. NOVEL approach.")

if __name__ == "__main__":
    main()
