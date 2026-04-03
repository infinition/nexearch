"""
#03 - OpenAI-style Evolution Strategy
Gradient estimation via population of perturbations.
Known to scale but sample-inefficient.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, accuracy, report, Timer, relu, softmax

class ESNetwork:
    def __init__(self, layer_sizes):
        self.params = []
        for i in range(len(layer_sizes)-1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]).astype(np.float32) * 0.05
            b = np.zeros(layer_sizes[i+1], dtype=np.float32)
            self.params.extend([w, b])

    def forward(self, x, params=None):
        p = params if params is not None else self.params
        h = x
        for i in range(0, len(p)-2, 2):
            h = relu(h @ p[i] + p[i+1])
        h = h @ p[-2] + p[-1]
        return h

    def get_flat(self):
        return np.concatenate([p.ravel() for p in self.params])

    def set_flat(self, flat):
        idx = 0
        for i, p in enumerate(self.params):
            size = p.size
            self.params[i] = flat[idx:idx+size].reshape(p.shape)
            idx += size

    def count_params(self):
        return sum(p.size for p in self.params)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=5000, n_test=1000)

    net = ESNetwork([784, 128, 10])
    n_params = net.count_params()
    print(f"Parameters: {n_params}")

    pop_size = 50
    sigma = 0.02
    lr = 0.01
    n_iters = 100
    batch_size = 512

    with Timer("Evolution Strategy") as t:
        theta = net.get_flat()

        for it in range(n_iters):
            # Sample subset for fitness eval
            idx = np.random.choice(len(X_train), batch_size, replace=False)
            X_batch, y_batch = X_train[idx], y_train[idx]

            # Generate perturbations
            eps = np.random.randn(pop_size, n_params).astype(np.float32)
            rewards = np.zeros(pop_size)

            for j in range(pop_size):
                net.set_flat(theta + sigma * eps[j])
                logits = net.forward(X_batch)
                preds = np.argmax(logits, axis=1)
                rewards[j] = np.mean(preds == y_batch)

            # Normalize rewards
            rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-8)

            # Update
            grad = (eps.T @ rewards) / (pop_size * sigma)
            theta += lr * grad

            if (it + 1) % 20 == 0:
                net.set_flat(theta)
                preds = np.argmax(net.forward(X_test), axis=1)
                acc = accuracy(preds, y_test)
                print(f"  Iter {it+1}: {acc:.2f}%")

        net.set_flat(theta)
        preds = np.argmax(net.forward(X_test), axis=1)
        final_acc = accuracy(preds, y_test)

    report("Evolution Strategy", final_acc, t.elapsed,
           "Population-based, zeroth-order. Sample inefficient but parallelizable.")

if __name__ == "__main__":
    main()
