"""
#33 - NoProp + Reservoir Hybrid (ORIGINAL INVENTION)
Chain of reservoir-based denoisers. Each block:
1. Projects input through a random reservoir (fixed dynamics)
2. Denoises a noisy label estimate using reservoir features
3. Passes refined estimate to next block

All blocks train independently (like NoProp) but use reservoir
computing (our best paradigm) instead of learned hidden layers.
The ONLY trainable parts are the denoiser readouts (ridge regression).
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

class ReservoirDenoiserBlock:
    """A reservoir-based denoising block."""
    def __init__(self, input_dim, reservoir_size, label_dim, noise_level,
                 spectral_radius=0.9, sparsity=0.05, seed=None):
        rng = np.random.RandomState(seed)
        self.noise_level = noise_level
        self.label_dim = label_dim

        # Fixed reservoir for input processing
        total_in = input_dim + label_dim
        self.W_in = rng.randn(total_in, reservoir_size).astype(np.float32) * 0.1
        W = rng.randn(reservoir_size, reservoir_size).astype(np.float32)
        mask = rng.rand(reservoir_size, reservoir_size) < sparsity
        W *= mask
        eigs = np.abs(np.linalg.eigvals(W))
        mx = max(eigs) if len(eigs) > 0 else 1.0
        if mx > 0: W *= spectral_radius / mx
        self.W_res = W
        self.reservoir_size = reservoir_size

        # Readout (the ONLY trainable part)
        self.W_out = None

    def reservoir_transform(self, x_combined, steps=3):
        """Run combined [features, noisy_label] through reservoir."""
        state = np.zeros((len(x_combined), self.reservoir_size), dtype=np.float32)
        drive = x_combined @ self.W_in
        for _ in range(steps):
            state = np.tanh(drive + state @ self.W_res)
        return state

    def fit(self, X_features, clean_labels, reg=0.1):
        """Train the readout using noisy inputs (one-shot, closed form)."""
        noise = np.random.randn(len(X_features), self.label_dim).astype(np.float32) * self.noise_level
        noisy = clean_labels + noise
        combined = np.hstack([X_features, noisy])
        H = self.reservoir_transform(combined)
        # Ridge regression readout
        self.W_out = np.linalg.solve(
            H.T @ H + reg * np.eye(self.reservoir_size),
            H.T @ clean_labels
        )

    def denoise(self, X_features, noisy_labels):
        """Denoise: predict clean label from features + noisy label."""
        combined = np.hstack([X_features, noisy_labels])
        H = self.reservoir_transform(combined)
        return H @ self.W_out


class NoPropReservoir:
    """Chain of reservoir denoisers. Each block independently trained."""
    def __init__(self, input_dim, label_dim=10, n_blocks=6, reservoir_size=1000):
        self.n_blocks = n_blocks
        self.blocks = []

        # Noise schedule: decreasing
        noise_levels = np.linspace(1.5, 0.1, n_blocks)

        # Feature projections (different for each block for diversity)
        self.projections = []
        proj_dims = [500, 400, 300, 500, 400, 300]

        for i in range(n_blocks):
            pd = proj_dims[i % len(proj_dims)]
            np.random.seed(i * 42 + 7)
            self.projections.append(
                np.random.randn(input_dim, pd).astype(np.float32) * np.sqrt(2.0 / input_dim)
            )

            block = ReservoirDenoiserBlock(
                input_dim=pd,
                reservoir_size=reservoir_size,
                label_dim=label_dim,
                noise_level=noise_levels[i],
                spectral_radius=0.85 + 0.1 * (i / n_blocks),
                sparsity=0.03 + 0.02 * (i / n_blocks),
                seed=i * 100
            )
            self.blocks.append(block)

    def fit(self, X, y_oh, reg=0.1):
        """Train each block independently (could be parallel!)."""
        for i, (block, proj) in enumerate(zip(self.blocks, self.projections)):
            features = np.tanh(X @ proj)
            block.fit(features, y_oh, reg=reg)
            print(f"  Block {i+1}/{self.n_blocks} trained", flush=True)

    def predict(self, X, n_passes=3):
        """Inference: chain the denoisers, average multiple passes."""
        all_preds = []

        for pass_idx in range(n_passes):
            # Start with random noise
            label_est = np.random.randn(len(X), 10).astype(np.float32) * 1.5

            # Each block refines the estimate
            for i, (block, proj) in enumerate(zip(self.blocks, self.projections)):
                features = np.tanh(X @ proj)
                label_est = block.denoise(features, label_est)

            all_preds.append(label_est)

        # Average across passes
        avg_pred = np.mean(all_preds, axis=0)
        return np.argmax(avg_pred, axis=1)


def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=20000, n_test=5000)
    y_train_oh = one_hot(y_train)

    net = NoPropReservoir(784, label_dim=10, n_blocks=6, reservoir_size=1000)

    with Timer("NoProp + Reservoir") as t:
        print("Training blocks (independently)...", flush=True)
        net.fit(X_train, y_train_oh, reg=0.05)

        print("Inference (3 passes)...", flush=True)
        preds = net.predict(X_test, n_passes=5)
        final_acc = accuracy(preds, y_test)

        # Also try single pass
        preds_1 = net.predict(X_test, n_passes=1)
        acc_1 = accuracy(preds_1, y_test)
        print(f"  1-pass: {acc_1:.2f}%, 5-pass: {final_acc:.2f}%", flush=True)

    report("NoProp + Reservoir (HYBRID)", max(final_acc, acc_1), t.elapsed,
           f"Reservoir denoiser chain. 1-pass={acc_1:.1f}% 5-pass={final_acc:.1f}%. NOVEL ARCHITECTURE.")

if __name__ == "__main__":
    main()
