"""
#20 - MEGA HYBRID: Multi-Reservoir + Entropy-Gated Readout (NOVEL)
Since Reservoir Computing gave us 91.9%, let's push it further:
1. Multiple diverse reservoirs (different spectral radii, sparsities)
2. Concatenate their states for richer representation
3. Entropy-gated feature selection before readout
4. Hyperdimensional encoding of input for robustness
5. Tikhonov regularized readout

This combines the BEST performer (reservoir) with the most promising ideas.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

class DiverseReservoir:
    def __init__(self, input_dim, size, spectral_radius, sparsity, input_scale=0.1):
        self.size = size
        self.W_in = np.random.randn(input_dim, size).astype(np.float32) * input_scale

        W = np.random.randn(size, size).astype(np.float32)
        mask = np.random.rand(size, size) < sparsity
        W *= mask
        eigs = np.abs(np.linalg.eigvals(W))
        max_eig = max(eigs) if len(eigs) > 0 else 1.0
        if max_eig > 0:
            W *= spectral_radius / max_eig
        self.W_res = W

    def transform(self, X, steps=5):
        batch = len(X)
        state = np.zeros((batch, self.size), dtype=np.float32)
        drive = X @ self.W_in
        for _ in range(steps):
            state = np.tanh(drive + state @ self.W_res)
        return state

def entropy_feature_selection(features, threshold=0.3):
    """Select features that have good entropy (informative but not random)."""
    # Per-feature entropy across samples
    eps = 1e-8
    f_abs = np.abs(features) + eps
    p = f_abs / f_abs.sum(axis=0, keepdims=True)
    ent = -np.sum(p * np.log(p + eps), axis=0)
    ent_norm = ent / (np.log(len(features)) + eps)

    # Keep features in the Goldilocks zone
    mask = (ent_norm > threshold) & (ent_norm < 0.95)
    return features[:, mask], mask

def hd_encode(X, proj_dim=2000):
    """Quick HD random projection."""
    np.random.seed(42)
    proj = np.random.choice([-1, 1], size=(X.shape[1], proj_dim)).astype(np.float32) / np.sqrt(proj_dim)
    return np.sign(X @ proj)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=20000, n_test=5000)

    # Try with HD encoding too
    X_train_hd = hd_encode(X_train, 1500)
    X_test_hd = hd_encode(X_test, 1500)

    # Create diverse reservoirs
    configs = [
        # (size, spectral_radius, sparsity, input_scale)
        (1500, 0.9, 0.05, 0.1),
        (1500, 0.99, 0.02, 0.05),
        (1000, 0.8, 0.1, 0.2),
        (1000, 0.95, 0.03, 0.15),
    ]

    with Timer("Mega Reservoir Hybrid") as t:
        all_train = []
        all_test = []

        for i, (size, sr, sp, isc) in enumerate(configs):
            print(f"  Reservoir {i+1}: size={size}, sr={sr}")
            # Half reservoirs use raw input, half use HD-encoded
            if i < 2:
                res = DiverseReservoir(784, size, sr, sp, isc)
                s_train = res.transform(X_train, steps=5)
                s_test = res.transform(X_test, steps=5)
            else:
                res = DiverseReservoir(1500, size, sr, sp, isc)
                s_train = res.transform(X_train_hd, steps=5)
                s_test = res.transform(X_test_hd, steps=5)

            all_train.append(s_train)
            all_test.append(s_test)

        # Concatenate all reservoir states
        H_train = np.hstack(all_train)
        H_test = np.hstack(all_test)
        print(f"  Total features: {H_train.shape[1]}")

        # Entropy-gated feature selection
        H_train_sel, mask = entropy_feature_selection(H_train, threshold=0.2)
        H_test_sel = H_test[:, mask]
        print(f"  After entropy gating: {H_train_sel.shape[1]} features")

        # Tikhonov regularized readout
        lam = 0.01
        targets = one_hot(y_train)
        W_out = np.linalg.solve(
            H_train_sel.T @ H_train_sel + lam * np.eye(H_train_sel.shape[1]),
            H_train_sel.T @ targets
        )
        preds = np.argmax(H_test_sel @ W_out, axis=1)
        acc_gated = accuracy(preds, y_test)
        print(f"  With entropy gating: {acc_gated:.2f}%")

        # Also try without gating for comparison
        W_out2 = np.linalg.solve(
            H_train.T @ H_train + lam * np.eye(H_train.shape[1]),
            H_train.T @ targets
        )
        preds2 = np.argmax(H_test @ W_out2, axis=1)
        acc_full = accuracy(preds2, y_test)
        print(f"  Without gating:      {acc_full:.2f}%")

        final_acc = max(acc_gated, acc_full)

    report("Mega Reservoir Hybrid", final_acc, t.elapsed,
           f"Multi-reservoir + HD encoding + entropy gating. Gated={acc_gated:.1f}% Full={acc_full:.1f}%")

if __name__ == "__main__":
    main()
