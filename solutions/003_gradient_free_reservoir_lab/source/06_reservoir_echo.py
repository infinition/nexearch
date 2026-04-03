"""
#06 - Echo State Network / Reservoir Computing
Fixed random recurrent layer, only train readout (closed form).
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, accuracy, report, Timer

class EchoStateNetwork:
    def __init__(self, input_dim, reservoir_size=2000, spectral_radius=0.9, sparsity=0.1):
        self.reservoir_size = reservoir_size

        # Input weights (random, fixed)
        self.W_in = np.random.randn(input_dim, reservoir_size).astype(np.float32) * 0.1

        # Reservoir weights (sparse, random, fixed)
        W_res = np.random.randn(reservoir_size, reservoir_size).astype(np.float32)
        mask = np.random.rand(reservoir_size, reservoir_size) < sparsity
        W_res *= mask

        # Scale to desired spectral radius
        eigenvalues = np.abs(np.linalg.eigvals(W_res))
        max_eig = np.max(eigenvalues) if len(eigenvalues) > 0 else 1.0
        if max_eig > 0:
            W_res *= spectral_radius / max_eig
        self.W_res = W_res

        self.W_out = None

    def transform(self, X, steps=3):
        """Run input through reservoir for several steps."""
        batch_size = len(X)
        state = np.zeros((batch_size, self.reservoir_size), dtype=np.float32)

        # Drive reservoir with input
        drive = X @ self.W_in
        for _ in range(steps):
            state = np.tanh(drive + state @ self.W_res)

        return state

    def fit(self, X, y, n_classes=10, reg=1.0):
        states = self.transform(X)
        targets = np.eye(n_classes, dtype=np.float32)[y]
        # Ridge regression
        self.W_out = np.linalg.solve(
            states.T @ states + reg * np.eye(self.reservoir_size),
            states.T @ targets
        )

    def predict(self, X):
        states = self.transform(X)
        return np.argmax(states @ self.W_out, axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    esn = EchoStateNetwork(784, reservoir_size=2000, spectral_radius=0.95, sparsity=0.05)

    with Timer("Echo State Network") as t:
        esn.fit(X_train, y_train, reg=0.1)
        preds = esn.predict(X_test)
        final_acc = accuracy(preds, y_test)

    report("Echo State Network / Reservoir", final_acc, t.elapsed,
           "Fixed random reservoir, only readout trained (closed-form).")

if __name__ == "__main__":
    main()
