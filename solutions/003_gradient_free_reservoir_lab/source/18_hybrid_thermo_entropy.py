"""
#18 - HYBRID: Thermodynamic Entropy-Gated Network (ORIGINAL INVENTION)
Combine thermodynamic free energy with entropy gating.
Idea: Use Boltzmann-like energy minimization, but gate the learning
based on the entropy of each neuron's activation distribution.
The temperature schedule interacts with the entropy gate:
- High temperature -> high entropy -> gates open -> fast exploration
- Low temperature -> low entropy -> gates close -> exploitation
This creates an automatic exploration/exploitation schedule.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, sigmoid

def neuron_entropy(h, eps=1e-8):
    h_pos = np.abs(h) + eps
    p = h_pos / h_pos.sum(axis=0, keepdims=True)
    entropy = -np.sum(p * np.log(p + eps), axis=0)
    return entropy / (np.log(len(h)) + eps)

class ThermoEntropyLayer:
    def __init__(self, in_dim, out_dim, lr=0.01, T_init=2.0):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.05
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr
        self.T = T_init
        self.T_init = T_init
        # Per-neuron adaptive temperature
        self.T_neuron = np.ones(out_dim, dtype=np.float32) * T_init

    def forward(self, x):
        """Stochastic forward with per-neuron temperature."""
        logits = (x @ self.W + self.b) / self.T_neuron
        prob = sigmoid(logits)
        # Soft activations (not binary)
        return prob

    def energy(self, x, h):
        return -np.sum(x @ self.W * h, axis=1) - np.sum(self.b * h, axis=1)

    def update(self, x, h, y_oh=None):
        """Entropy-gated thermodynamic update."""
        ent = neuron_entropy(h)

        # Adaptive temperature: neurons with extreme entropy get heated/cooled
        # High entropy (too random) -> cool down
        # Low entropy (too fixed) -> heat up
        target_entropy = 0.6
        self.T_neuron *= np.exp(0.01 * (ent - target_entropy))
        self.T_neuron = np.clip(self.T_neuron, 0.1, 5.0)

        # Entropy gate
        gate = np.exp(-10 * (ent - 0.5)**2)  # Gaussian gate centered at 0.5

        # Contrastive divergence with gating
        # Positive phase
        pos_corr = (x.T @ h) / len(x)

        # Negative phase (one Gibbs step)
        x_recon = sigmoid(h @ self.W.T / self.T)
        h_recon = sigmoid((x_recon @ self.W + self.b) / self.T_neuron)
        neg_corr = (x_recon.T @ h_recon) / len(x)

        # Gated update
        dW = gate[None, :] * (pos_corr - neg_corr)
        self.W += self.lr * dW
        self.b += self.lr * gate * (h.mean(axis=0) - h_recon.mean(axis=0))

        # Global temperature cooling
        self.T *= 0.999
        self.T = max(0.3, self.T)

        return ent, self.T_neuron.mean()

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    layer1 = ThermoEntropyLayer(784, 500, lr=0.01, T_init=2.0)
    layer2 = ThermoEntropyLayer(500, 200, lr=0.01, T_init=2.0)

    n_epochs = 20
    batch_size = 128

    with Timer("Thermo-Entropy Network") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                x = X_train[idx]

                h1 = layer1.forward(x)
                e1, t1 = layer1.update(x, h1)

                h2 = layer2.forward(h1)
                e2, t2 = layer2.update(h1, h2)

            if (epoch + 1) % 5 == 0:
                h1 = layer1.forward(X_train)
                h2 = layer2.forward(h1)
                h1t = layer1.forward(X_test)
                h2t = layer2.forward(h1t)

                lam = 0.5
                W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                        h2.T @ one_hot(y_train))
                preds = np.argmax(h2t @ W_out, axis=1)
                acc = accuracy(preds, y_test)

                e1 = neuron_entropy(h1[:1000])
                print(f"  Epoch {epoch+1}: {acc:.2f}% | Entropy={e1.mean():.3f} T_global={layer1.T:.3f}")

        h1 = layer1.forward(X_train)
        h2 = layer2.forward(h1)
        h1t = layer1.forward(X_test)
        h2t = layer2.forward(h1t)
        lam = 0.3
        W_out = np.linalg.solve(h2.T @ h2 + lam * np.eye(h2.shape[1]),
                                h2.T @ one_hot(y_train))
        preds = np.argmax(h2t @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("Thermo-Entropy Network (HYBRID)", final_acc, t.elapsed,
           "ORIGINAL: Thermodynamic + entropy gating + adaptive temperature. Auto explore/exploit.")

if __name__ == "__main__":
    main()
