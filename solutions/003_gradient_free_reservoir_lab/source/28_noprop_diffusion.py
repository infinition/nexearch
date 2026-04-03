"""
#28 - NoProp: Diffusion-Inspired Block-Independent Training (CoLLAs 2025)
Treat each network block as a denoiser in a diffusion chain.
Each block independently learns to denoise a noisy version of the target.
NO forward or backward propagation between blocks.
All blocks can train in PARALLEL.
Reference: arXiv:2503.24322
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu

class NoPropBlock:
    """A single denoising block. Learns to predict clean label from noisy label + input."""
    def __init__(self, input_dim, label_dim, hidden_dim=256, lr=0.01, noise_level=0.5):
        # Takes concatenation of [input_features, noisy_label]
        total_in = input_dim + label_dim
        self.W1 = np.random.randn(total_in, hidden_dim).astype(np.float32) * np.sqrt(2.0 / total_in)
        self.b1 = np.zeros(hidden_dim, dtype=np.float32)
        self.W2 = np.random.randn(hidden_dim, label_dim).astype(np.float32) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(label_dim, dtype=np.float32)
        self.lr = lr
        self.noise_level = noise_level

    def forward(self, x, noisy_label):
        """Predict clean label from input + noisy label."""
        combined = np.hstack([x, noisy_label])
        h = relu(combined @ self.W1 + self.b1)
        pred = h @ self.W2 + self.b2
        return pred, h, combined

    def train_step(self, x, clean_label):
        """Generate noisy label, predict clean, update."""
        batch_size = len(x)
        noise = np.random.randn(*clean_label.shape).astype(np.float32) * self.noise_level
        noisy_label = clean_label + noise

        pred, h, combined = self.forward(x, noisy_label)

        # Loss: ||pred - clean_label||^2
        error = pred - clean_label

        # Backprop WITHIN this block only (not across blocks)
        dW2 = (h.T @ error) / batch_size
        db2 = error.mean(axis=0)

        # Hidden layer gradient
        dh = error @ self.W2.T
        dh *= (h > 0).astype(np.float32)  # ReLU derivative
        dW1 = (combined.T @ dh) / batch_size
        db1 = dh.mean(axis=0)

        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1

    def denoise(self, x, noisy_label):
        pred, _, _ = self.forward(x, noisy_label)
        return pred

class NoPropNetwork:
    """Chain of denoising blocks. Each block reduces noise independently."""
    def __init__(self, input_dim, label_dim=10, n_blocks=5, hidden_dim=256, lr=0.01):
        self.n_blocks = n_blocks
        self.blocks = []

        # Noise schedule: decreasing noise levels
        noise_levels = np.linspace(1.0, 0.1, n_blocks)

        # Feature extractor (fixed random projection for efficiency)
        self.proj = np.random.randn(input_dim, hidden_dim).astype(np.float32) * np.sqrt(2.0 / input_dim)

        for i in range(n_blocks):
            self.blocks.append(NoPropBlock(hidden_dim, label_dim, hidden_dim,
                                          lr=lr, noise_level=noise_levels[i]))

    def extract_features(self, x):
        return relu(x @ self.proj)

    def train_epoch(self, X, y_oh, batch_size=128):
        """Train all blocks. Each block trains independently."""
        features = self.extract_features(X)
        perm = np.random.permutation(len(X))

        for i in range(0, len(X), batch_size):
            idx = perm[i:i+batch_size]
            x_batch = features[idx]
            y_batch = y_oh[idx]

            # Each block trains independently (could be parallel!)
            for block in self.blocks:
                block.train_step(x_batch, y_batch)

    def predict(self, X):
        """Inference: chain the denoisers. Start from pure noise, denoise step by step."""
        features = self.extract_features(X)
        batch_size = len(X)

        # Start with random noise as initial "label guess"
        label_estimate = np.random.randn(batch_size, 10).astype(np.float32) * 1.0

        # Each block refines the estimate
        for block in self.blocks:
            label_estimate = block.denoise(features, label_estimate)

        return np.argmax(label_estimate, axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)
    y_train_oh = one_hot(y_train)

    net = NoPropNetwork(784, label_dim=10, n_blocks=6, hidden_dim=300, lr=0.01)
    n_epochs = 25
    batch_size = 128

    with Timer("NoProp (Diffusion)") as t:
        for epoch in range(n_epochs):
            net.train_epoch(X_train, y_train_oh, batch_size)

            if (epoch + 1) % 5 == 0:
                preds = net.predict(X_test)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        preds = net.predict(X_test)
        final_acc = accuracy(preds, y_test)

    report("NoProp (Diffusion-Inspired)", final_acc, t.elapsed,
           "Block-independent denoising chain. CoLLAs 2025. All blocks train in parallel.")

if __name__ == "__main__":
    main()
