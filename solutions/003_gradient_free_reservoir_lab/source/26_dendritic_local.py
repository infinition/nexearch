"""
#26 - Dendritic Localized Learning (DLL) - ICML 2025
Pyramidal neuron with basal (bottom-up) and apical (top-down) compartments.
Local error = apical - basal. No global backprop.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu, sigmoid

class DendriticLayer:
    def __init__(self, in_dim, out_dim, lr=0.01):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * np.sqrt(2.0 / in_dim)
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr

    def forward(self, x):
        return relu(x @ self.W + self.b)

    def update_with_target(self, x, h, target):
        """Local update: push h toward target."""
        error = target - h
        mask = (h > 0).astype(np.float32)
        delta = error * mask
        self.W += self.lr * (x.T @ delta) / len(x)
        self.b += self.lr * delta.mean(axis=0)

class DLLNetwork:
    def __init__(self, sizes, lr=0.01):
        self.hidden = []
        for i in range(len(sizes) - 2):
            self.hidden.append(DendriticLayer(sizes[i], sizes[i+1], lr))

        # Output
        self.W_out = np.random.randn(sizes[-2], sizes[-1]).astype(np.float32) * np.sqrt(2.0/sizes[-2])
        self.b_out = np.zeros(sizes[-1], dtype=np.float32)

        # Top-down projection weights (feedback, separate from forward)
        self.W_fb = []
        for i in range(len(sizes) - 2):
            # Project from label space to hidden layer i
            self.W_fb.append(np.random.randn(sizes[-1], sizes[i+1]).astype(np.float32) * 0.1)
        self.lr = lr

    def forward(self, x):
        acts = [x]
        h = x
        for layer in self.hidden:
            h = layer.forward(h)
            acts.append(h)
        out = h @ self.W_out + self.b_out
        acts.append(out)
        return acts

    def train_step(self, x, y_oh):
        bs = len(x)
        acts = self.forward(x)

        # Output update
        out = acts[-1]
        probs = np.exp(out - out.max(axis=1, keepdims=True))
        probs /= probs.sum(axis=1, keepdims=True)
        err_out = probs - y_oh
        self.W_out -= self.lr * (acts[-2].T @ err_out) / bs
        self.b_out -= self.lr * err_out.mean(axis=0)

        # Hidden layers: dendritic local learning
        for i, layer in enumerate(self.hidden):
            # Apical target: top-down projection of correct label
            apical = relu(y_oh @ self.W_fb[i])
            # Scale to match activation range
            scale = np.mean(np.abs(acts[i+1])) / (np.mean(np.abs(apical)) + 1e-8)
            apical *= scale

            layer.update_with_target(acts[i], acts[i+1], apical)

            # Update feedback weights too (slow)
            fb_err = acts[i+1] - apical
            self.W_fb[i] += self.lr * 0.1 * (y_oh.T @ fb_err) / bs

    def predict(self, x):
        return np.argmax(self.forward(x)[-1], axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=5000, n_test=1000)

    net = DLLNetwork([784, 256, 10], lr=0.03)
    n_epochs = 15
    batch_size = 128

    with Timer("Dendritic Localized Learning") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                net.train_step(X_train[idx], one_hot(y_train[idx]))

            if (epoch+1) % 5 == 0:
                acc = accuracy(net.predict(X_test), y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        final_acc = accuracy(net.predict(X_test), y_test)

    report("Dendritic Localized Learning (DLL)", final_acc, t.elapsed,
           "3-compartment pyramidal neuron. ICML 2025. Local error only.")

if __name__ == "__main__":
    main()
