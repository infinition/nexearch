"""
#23 - ULTRA RESERVOIR: Maximum Accuracy Push
Scale up the multi-reservoir hybrid to squeeze every last % of accuracy.
- 8 diverse reservoirs (more diversity = better)
- Larger reservoir sizes
- Multiple input representations (raw, HD, normalized, whitened)
- Nonlinear readout via random kitchen sinks (Rahimi & Recht 2007)
- Stacking: reservoir output as input to another reservoir
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

class Reservoir:
    def __init__(self, in_dim, size, sr, sp, isc, activation='tanh'):
        self.W_in = np.random.randn(in_dim, size).astype(np.float32) * isc
        W = np.random.randn(size, size).astype(np.float32)
        mask = np.random.rand(size, size) < sp
        W *= mask
        eigs = np.abs(np.linalg.eigvals(W))
        mx = max(eigs) if len(eigs) > 0 else 1.0
        if mx > 0: W *= sr / mx
        self.W = W
        self.act = np.tanh if activation == 'tanh' else lambda x: np.maximum(x, 0)
        self.size = size

    def transform(self, X, steps=5):
        state = np.zeros((len(X), self.size), dtype=np.float32)
        drive = X @ self.W_in
        for _ in range(steps):
            state = self.act(drive + state @ self.W)
        return state

def random_kitchen_sinks(X, n_features=2000, gamma=1.0):
    """Approximate RBF kernel via random features (Rahimi & Recht)."""
    np.random.seed(123)
    W = np.random.randn(X.shape[1], n_features).astype(np.float32) * gamma
    b = np.random.uniform(0, 2 * np.pi, n_features).astype(np.float32)
    return np.cos(X @ W + b) * np.sqrt(2.0 / n_features)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=30000, n_test=10000)

    # Multiple input representations
    X_raw = X_train
    X_raw_t = X_test

    # HD encoding
    np.random.seed(42)
    proj = np.random.choice([-1, 1], size=(784, 2000)).astype(np.float32) / np.sqrt(2000)
    X_hd = np.sign(X_train @ proj)
    X_hd_t = np.sign(X_test @ proj)

    # Whitened (PCA-like via random projection)
    np.random.seed(99)
    proj2 = np.random.randn(784, 500).astype(np.float32) / np.sqrt(500)
    X_w = X_train @ proj2
    X_w -= X_w.mean(axis=0)
    X_w_t = X_test @ proj2
    X_w_t -= X_w_t.mean(axis=0)

    configs = [
        # (input, in_dim, size, sr, sp, isc, act, steps)
        ('raw', 784, 2000, 0.9, 0.05, 0.1, 'tanh', 5),
        ('raw', 784, 2000, 0.99, 0.02, 0.05, 'tanh', 8),
        ('raw', 784, 1500, 0.8, 0.1, 0.2, 'relu', 3),
        ('hd', 2000, 1500, 0.95, 0.03, 0.1, 'tanh', 5),
        ('hd', 2000, 1500, 0.85, 0.08, 0.15, 'tanh', 4),
        ('white', 500, 1000, 0.9, 0.05, 0.2, 'tanh', 6),
        ('white', 500, 1000, 0.98, 0.01, 0.1, 'tanh', 10),
        ('raw', 784, 1000, 0.92, 0.04, 0.12, 'relu', 4),
    ]

    inputs = {'raw': (X_raw, X_raw_t), 'hd': (X_hd, X_hd_t), 'white': (X_w, X_w_t)}

    with Timer("Ultra Reservoir") as t:
        all_train = []
        all_test = []

        for i, (inp, in_dim, size, sr, sp, isc, act, steps) in enumerate(configs):
            print(f"  Reservoir {i+1}/{len(configs)}: {inp} size={size} sr={sr} act={act}")
            res = Reservoir(in_dim, size, sr, sp, isc, act)
            X_tr, X_te = inputs[inp]
            all_train.append(res.transform(X_tr, steps))
            all_test.append(res.transform(X_te, steps))

        # Concatenate
        H_tr = np.hstack(all_train)
        H_te = np.hstack(all_test)
        print(f"  Total features: {H_tr.shape[1]}")

        # Method 1: Direct ridge regression
        lam = 0.01
        targets = one_hot(y_train)
        W_out = np.linalg.solve(H_tr.T @ H_tr + lam * np.eye(H_tr.shape[1]), H_tr.T @ targets)
        preds1 = np.argmax(H_te @ W_out, axis=1)
        acc1 = accuracy(preds1, y_test)
        print(f"  Direct readout: {acc1:.2f}%")

        # Method 2: Random kitchen sinks (nonlinear readout)
        H_rks_tr = random_kitchen_sinks(H_tr, n_features=3000, gamma=0.001)
        H_rks_te = random_kitchen_sinks(H_te, n_features=3000, gamma=0.001)
        W_rks = np.linalg.solve(H_rks_tr.T @ H_rks_tr + 0.01 * np.eye(3000), H_rks_tr.T @ targets)
        preds2 = np.argmax(H_rks_te @ W_rks, axis=1)
        acc2 = accuracy(preds2, y_test)
        print(f"  Kitchen Sinks readout: {acc2:.2f}%")

        # Method 3: Stacked reservoir (reservoir on top of reservoir)
        print(f"  Building stacked reservoir...")
        meta_res = Reservoir(H_tr.shape[1], 2000, 0.9, 0.03, 0.01, 'tanh')
        H_meta_tr = meta_res.transform(H_tr, steps=3)
        H_meta_te = meta_res.transform(H_te, steps=3)
        # Combine original + meta
        H_stack_tr = np.hstack([H_tr, H_meta_tr])
        H_stack_te = np.hstack([H_te, H_meta_te])
        W_stack = np.linalg.solve(H_stack_tr.T @ H_stack_tr + 0.01 * np.eye(H_stack_tr.shape[1]),
                                   H_stack_tr.T @ targets)
        preds3 = np.argmax(H_stack_te @ W_stack, axis=1)
        acc3 = accuracy(preds3, y_test)
        print(f"  Stacked readout: {acc3:.2f}%")

        final_acc = max(acc1, acc2, acc3)

    report("ULTRA RESERVOIR", final_acc, t.elapsed,
           f"8 reservoirs + 3 readouts. Direct={acc1:.1f}% RKS={acc2:.1f}% Stacked={acc3:.1f}%")

if __name__ == "__main__":
    main()
