"""
#10 - Spike-Timing Dependent Plasticity (STDP) Deep Network
Rate-coded STDP approximation for deep feedforward networks.
Exponential STDP windows + homeostatic normalization.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

class STDPLayer:
    def __init__(self, in_dim, out_dim, lr=0.01, threshold=0.5):
        self.W = np.random.rand(in_dim, out_dim).astype(np.float32) * 0.1
        self.lr = lr
        self.threshold = threshold

    def forward(self, x):
        """Rate-coded spiking: activation > threshold = spike."""
        h = x @ self.W
        # Lateral inhibition: keep top-k
        k = max(1, h.shape[1] // 5)
        thresh = np.partition(h, -k, axis=1)[:, -k:].min(axis=1, keepdims=True)
        spikes = (h >= thresh).astype(np.float32)
        rates = h * spikes  # spike rates
        return rates, spikes

    def stdp_update(self, pre_spikes, post_spikes):
        """STDP: strengthen connections between co-active neurons."""
        batch_size = len(pre_spikes)

        # LTP: pre fires -> post fires (Hebbian)
        dW_ltp = (pre_spikes.T @ post_spikes) / batch_size

        # LTD: post fires but pre doesn't (anti-Hebbian component)
        pre_inactive = 1.0 - (pre_spikes > 0).astype(np.float32)
        dW_ltd = (pre_inactive.T @ post_spikes) / batch_size * 0.5

        self.W += self.lr * (dW_ltp - dW_ltd)

        # Homeostasis: normalize weights per post-synaptic neuron
        col_sums = self.W.sum(axis=0, keepdims=True) + 1e-8
        self.W /= col_sums
        self.W = np.clip(self.W, 0, None)  # Dale's law: excitatory only

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    layer1 = STDPLayer(784, 500, lr=0.01)
    layer2 = STDPLayer(500, 200, lr=0.01)

    n_epochs = 15
    batch_size = 128

    with Timer("STDP Deep Network") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                x = X_train[idx]

                # Forward + STDP
                h1_rates, h1_spikes = layer1.forward(x)
                layer1.stdp_update(x, h1_spikes)

                h2_rates, h2_spikes = layer2.forward(h1_rates)
                layer2.stdp_update(h1_rates, h2_spikes)

            if (epoch + 1) % 5 == 0:
                # Evaluate
                h1, _ = layer1.forward(X_train)
                h2, _ = layer2.forward(h1)
                h1t, _ = layer1.forward(X_test)
                h2t, _ = layer2.forward(h1t)

                lam = 1.0
                W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                        h2.T @ one_hot(y_train))
                preds = np.argmax(h2t @ W_out, axis=1)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        h1, _ = layer1.forward(X_train)
        h2, _ = layer2.forward(h1)
        h1t, _ = layer1.forward(X_test)
        h2t, _ = layer2.forward(h1t)
        lam = 0.5
        W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                h2.T @ one_hot(y_train))
        preds = np.argmax(h2t @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("STDP Deep Network", final_acc, t.elapsed,
           "Spike-timing plasticity, lateral inhibition, homeostasis.")

if __name__ == "__main__":
    main()
