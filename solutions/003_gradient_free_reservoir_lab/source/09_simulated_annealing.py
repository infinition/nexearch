"""
#09 - Simulated Annealing for Neural Weights
Global optimization via random perturbation + temperature schedule.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, accuracy, report, Timer, relu

def forward(x, params):
    h = x
    for i in range(0, len(params)-2, 2):
        h = relu(h @ params[i] + params[i+1])
    return h @ params[-2] + params[-1]

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=3000, n_test=1000)

    # Small network
    sizes = [784, 64, 10]
    params = []
    for i in range(len(sizes)-1):
        params.append(np.random.randn(sizes[i], sizes[i+1]).astype(np.float32) * 0.05)
        params.append(np.zeros(sizes[i+1], dtype=np.float32))

    def loss_fn(params, X, y):
        logits = forward(X, params)
        preds = np.argmax(logits, axis=1)
        return -np.mean(preds == y)  # negative accuracy as loss

    n_iters = 500
    T_start = 0.1
    T_end = 0.001
    batch_size = 500

    with Timer("Simulated Annealing") as t:
        best_loss = loss_fn(params, X_train[:batch_size], y_train[:batch_size])
        best_params = [p.copy() for p in params]

        for it in range(n_iters):
            T = T_start * (T_end / T_start) ** (it / n_iters)

            # Perturb
            new_params = [p + np.random.randn(*p.shape).astype(np.float32) * T * 0.5 for p in params]

            idx = np.random.choice(len(X_train), batch_size, replace=False)
            new_loss = loss_fn(new_params, X_train[idx], y_train[idx])

            # Accept or reject
            delta = new_loss - best_loss
            if delta < 0 or np.random.rand() < np.exp(-delta / (T + 1e-8)):
                params = new_params
                if new_loss < best_loss:
                    best_loss = new_loss
                    best_params = [p.copy() for p in params]

            if (it + 1) % 100 == 0:
                preds = np.argmax(forward(X_test, best_params), axis=1)
                acc = accuracy(preds, y_test)
                print(f"  Iter {it+1}, T={T:.4f}: {acc:.2f}%")

        preds = np.argmax(forward(X_test, best_params), axis=1)
        final_acc = accuracy(preds, y_test)

    report("Simulated Annealing", final_acc, t.elapsed,
           "Global optimization. Simple but very slow to converge.")

if __name__ == "__main__":
    main()
