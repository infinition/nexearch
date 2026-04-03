"""
#30 - Prospective Configuration (Nature Neuroscience 2024)
First INFER what activity pattern should result from learning,
then modify weights to consolidate that pattern.
Phase 1: Find target activities x* by minimizing free energy
Phase 2: dW = eta * (x* - x_current) @ input.T (local Hebbian)
More data-efficient than backprop, no catastrophic forgetting.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu

class ProspectiveLayer:
    def __init__(self, in_dim, out_dim, lr=0.01):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * np.sqrt(2.0 / in_dim)
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr

    def forward(self, x):
        return relu(x @ self.W + self.b)

class ProspectiveNetwork:
    def __init__(self, sizes, lr=0.01, n_infer=10, lr_infer=0.1):
        self.layers = [ProspectiveLayer(sizes[i], sizes[i+1], lr) for i in range(len(sizes)-1)]
        self.n_infer = n_infer
        self.lr_infer = lr_infer
        self.lr = lr

    def forward(self, x):
        acts = [x]
        h = x
        for layer in self.layers:
            h = layer.forward(h)
            acts.append(h)
        return acts

    def infer_targets(self, x, y_oh):
        """Phase 1: Prospective inference. Find target activities."""
        acts = self.forward(x)
        # Initialize targets as current activations
        targets = [a.copy() for a in acts]
        targets[-1] = y_oh  # Clamp output to desired label

        for _ in range(self.n_infer):
            # For each hidden layer, adjust target to reduce free energy
            for i in range(1, len(self.layers)):
                # Prediction from below: what layer i predicts from layer i-1
                pred_from_below = self.layers[i-1].forward(targets[i-1])
                # Prediction from above: what layer i+1 expects (via pseudo-inverse)
                if i < len(self.layers):
                    # Use transpose as approximate inverse
                    pred_from_above = relu(targets[i+1] @ self.layers[i].W.T)

                    # Target is a blend of bottom-up and top-down
                    targets[i] = (1 - self.lr_infer) * targets[i] + \
                                 self.lr_infer * 0.5 * (pred_from_below + pred_from_above)
                else:
                    targets[i] = pred_from_below

        return targets

    def train_step(self, x, y_oh):
        """Phase 1: Infer targets. Phase 2: Local Hebbian consolidation."""
        targets = self.infer_targets(x, y_oh)
        acts = self.forward(x)

        # Phase 2: Update weights locally
        for i, layer in enumerate(self.layers):
            # dW = eta * (target - actual) @ input.T
            error = targets[i+1] - acts[i+1]
            mask = (acts[i+1] > 0).astype(np.float32)
            delta = error * mask
            layer.W += layer.lr * (acts[i].T @ delta) / len(x)
            layer.b += layer.lr * delta.mean(axis=0)

    def predict(self, x):
        return np.argmax(self.forward(x)[-1], axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    net = ProspectiveNetwork([784, 300, 10], lr=0.02, n_infer=5, lr_infer=0.2)
    n_epochs = 20
    batch_size = 128

    with Timer("Prospective Configuration") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                net.train_step(X_train[idx], one_hot(y_train[idx]))

            if (epoch+1) % 5 == 0:
                acc = accuracy(net.predict(X_test), y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        final_acc = accuracy(net.predict(X_test), y_test)

    report("Prospective Configuration", final_acc, t.elapsed,
           "Infer targets first, then Hebbian consolidation. Nature Neuroscience 2024.")

if __name__ == "__main__":
    main()
