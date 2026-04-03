"""
#25 - Counter-Current Learning (CCL) - NeurIPS 2024
Two networks with anti-parallel signal flow.
Forward: input -> h1 -> h2 -> output
Backward: target -> h2' -> h1' -> recon
Local loss at each matching pair of layers.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu

class CCLNetwork:
    def __init__(self, sizes, lr=0.01):
        # sizes = [784, 256, 256, 10]
        self.n = len(sizes) - 1
        self.lr = lr

        # Forward weights
        self.Wf = [np.random.randn(sizes[i], sizes[i+1]).astype(np.float32) * np.sqrt(2.0/sizes[i]) for i in range(self.n)]
        self.bf = [np.zeros(sizes[i+1], dtype=np.float32) for i in range(self.n)]

        # Backward weights (reversed direction, same hidden sizes)
        # backward[0]: sizes[-1] -> sizes[-2], backward[1]: sizes[-2] -> sizes[-3], etc.
        self.Wb = [np.random.randn(sizes[self.n-i], sizes[self.n-i-1]).astype(np.float32) * np.sqrt(2.0/sizes[self.n-i]) for i in range(self.n)]
        self.bb = [np.zeros(sizes[self.n-i-1], dtype=np.float32) for i in range(self.n)]

    def fwd(self, x):
        acts = [x]
        h = x
        for i in range(self.n):
            h = h @ self.Wf[i] + self.bf[i]
            if i < self.n - 1: h = relu(h)
            acts.append(h)
        return acts

    def bwd(self, y):
        acts = [y]
        h = y
        for i in range(self.n):
            h = h @ self.Wb[i] + self.bb[i]
            if i < self.n - 1: h = relu(h)
            acts.append(h)
        return acts

    def train_step(self, x, y_oh):
        bs = len(x)
        fa = self.fwd(x)   # [x, h1, h2, out]
        ba = self.bwd(y_oh) # [y, h2', h1', recon]

        # Match: fa[i+1] with ba[n-i-1] (same dimension)
        for i in range(self.n):
            f_act = fa[i + 1]              # forward layer i+1
            b_act = ba[self.n - i - 1]     # backward matching layer

            if f_act.shape != b_act.shape:
                continue

            err = b_act - f_act
            if i < self.n - 1:
                err *= (f_act > 0).astype(np.float32)

            self.Wf[i] += self.lr * (fa[i].T @ err) / bs
            self.bf[i] += self.lr * err.mean(axis=0)

            # Update backward weights: backward layer maps ba[j] -> ba[j+1]
            # We need to find which backward layer produced b_act
            # ba = [y, bwd_h1, bwd_h2, recon], Wb[0]: y->bwd_h1, Wb[1]: bwd_h1->bwd_h2, etc.
            b_layer_idx = self.n - i - 2  # which Wb produced b_act
            if 0 <= b_layer_idx < self.n:
                b_input = ba[b_layer_idx]  # input to that backward layer
                err_b = f_act - b_act
                if b_layer_idx < self.n - 1:
                    err_b *= (b_act > 0).astype(np.float32)
                if b_input.shape[1] == self.Wb[b_layer_idx].shape[0]:
                    self.Wb[b_layer_idx] += self.lr * (b_input.T @ err_b) / bs
                    self.bb[b_layer_idx] += self.lr * err_b.mean(axis=0)

    def predict(self, x):
        return np.argmax(self.fwd(x)[-1], axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    net = CCLNetwork([784, 256, 256, 10], lr=0.01)
    n_epochs = 25
    batch_size = 64

    with Timer("Counter-Current Learning") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                net.train_step(X_train[idx], one_hot(y_train[idx]))

            if (epoch+1) % 5 == 0:
                acc = accuracy(net.predict(X_test), y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        final_acc = accuracy(net.predict(X_test), y_test)

    report("Counter-Current Learning (CCL)", final_acc, t.elapsed,
           "Anti-parallel dual network, local losses. NeurIPS 2024.")

if __name__ == "__main__":
    main()
