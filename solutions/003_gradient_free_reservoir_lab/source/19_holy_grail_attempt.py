"""
#19 - HOLY GRAIL ATTEMPT: Entropic Competitive Tropical Predictive Network
Combines the BEST ideas from all experiments:
1. Tropical (max-plus) algebra for natural competition (no softmax needed)
2. Entropy gating for optimal plasticity regime
3. Predictive coding for local error signals
4. Hyperdimensional encoding for robust input representation
5. Adaptive temperature from thermodynamics

The key insight: Each mechanism addresses a different aspect of learning:
- HD encoding: noise-robust feature representation
- Tropical ops: natural winner-take-all without explicit competition
- Predictive coding: provides TARGET signal without backprop
- Entropy gate: prevents dead neurons and runaway activations
- Temperature: automatic annealing schedule

This is a NOVEL ARCHITECTURE that has never been tried.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

def neuron_entropy(h, eps=1e-8):
    h_pos = np.abs(h) + eps
    p = h_pos / h_pos.sum(axis=0, keepdims=True)
    entropy = -np.sum(p * np.log(p + eps), axis=0)
    return entropy / (np.log(max(2, len(h))) + eps)

class HDProjection:
    """Random HD projection for robust encoding."""
    def __init__(self, input_dim, hd_dim):
        self.proj = np.random.choice([-1, 1], size=(input_dim, hd_dim)).astype(np.float32) / np.sqrt(hd_dim)

    def encode(self, x):
        return np.sign(x @ self.proj)

class HolyGrailLayer:
    def __init__(self, in_dim, out_dim, lr=0.01, T_init=1.5):
        self.W = np.random.randn(in_dim, out_dim).astype(np.float32) * 0.1
        self.b = np.zeros(out_dim, dtype=np.float32)
        self.lr = lr
        self.T = np.ones(out_dim, dtype=np.float32) * T_init

        # Prediction weights (top-down)
        self.W_pred = np.random.randn(out_dim, in_dim).astype(np.float32) * 0.01

    def tropical_forward(self, x):
        """Max-plus forward pass."""
        extended = x[:, :, None] + self.W[None, :, :]
        h = np.max(extended, axis=1) + self.b
        winners = np.argmax(extended, axis=1)
        # Apply temperature scaling
        h = h / self.T
        return np.maximum(h, 0), winners  # tropical ReLU

    def predict_input(self, h):
        """Top-down prediction of input."""
        return h @ self.W_pred

    def update(self, x, h, winners, target_signal=None):
        """Multi-mechanism update."""
        batch_size = len(x)

        # 1. Entropy gate
        ent = neuron_entropy(h)
        gate = np.exp(-8 * (ent - 0.55)**2)  # Gaussian centered at sweet spot

        # 2. Predictive coding error
        x_pred = self.predict_input(h)
        pred_error = x - x_pred

        # 3. Update prediction weights (local)
        self.W_pred += self.lr * 0.5 * (h.T @ pred_error) / batch_size

        # 4. Tropical weight update: use prediction error as learning signal
        # Project error through winners
        dW = np.zeros_like(self.W)
        for j in range(self.W.shape[1]):
            if gate[j] < 0.01:
                continue
            for b in range(batch_size):
                w = winners[b, j]
                # Error-driven: strengthen if prediction error is large for this feature
                signal = np.abs(pred_error[b, w]) * gate[j]
                if target_signal is not None:
                    signal *= target_signal[b, j]
                dW[w, j] += signal

        self.W += self.lr * gate[None, :] * dW / batch_size

        # 5. Adaptive temperature
        target_ent = 0.55
        self.T *= np.exp(0.02 * (ent - target_ent))
        self.T = np.clip(self.T, 0.2, 5.0)

        # Normalize
        norms = np.linalg.norm(self.W, axis=0, keepdims=True) + 1e-8
        self.W /= norms

        return ent

class HolyGrailNetwork:
    def __init__(self, input_dim, hd_dim, hidden_dims, n_classes):
        self.hd = HDProjection(input_dim, hd_dim)
        self.layers = []
        dims = [hd_dim] + hidden_dims
        for i in range(len(dims)-1):
            self.layers.append(HolyGrailLayer(dims[i], dims[i+1], lr=0.015))

        # Final readout (not part of the novel mechanism, just for evaluation)
        self.readout_dim = hidden_dims[-1]
        self.n_classes = n_classes

    def extract_features(self, X):
        """Full forward pass to get features."""
        h = self.hd.encode(X)
        for layer in self.layers:
            h, _ = layer.tropical_forward(h)
        return h

    def train_epoch(self, X, y, batch_size=128):
        perm = np.random.permutation(len(X))
        for i in range(0, len(X), batch_size):
            idx = perm[i:i+batch_size]
            x = self.hd.encode(X[idx])

            # Forward through all layers
            activations = [x]
            winners_list = []
            h = x
            for layer in self.layers:
                h, w = layer.tropical_forward(h)
                activations.append(h)
                winners_list.append(w)

            # Update each layer (local signals only)
            for l, layer in enumerate(self.layers):
                # Create target signal from class information
                # Simple: each class should activate a different subset
                target = np.zeros_like(activations[l+1])
                n_per_class = activations[l+1].shape[1] // self.n_classes
                for c in range(self.n_classes):
                    mask = y[idx] == c
                    if mask.any():
                        start = c * n_per_class
                        end = min((c+1) * n_per_class, activations[l+1].shape[1])
                        target[mask, start:end] = 1.0
                        # Suppress other classes
                        target[mask, :start] = -0.5
                        target[mask, end:] = -0.5

                layer.update(activations[l], activations[l+1], winners_list[l],
                           target_signal=target)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    net = HolyGrailNetwork(
        input_dim=784,
        hd_dim=2000,
        hidden_dims=[800, 400],
        n_classes=10
    )

    n_epochs = 30
    batch_size = 256

    with Timer("Holy Grail Attempt") as t:
        for epoch in range(n_epochs):
            net.train_epoch(X_train, y_train, batch_size=batch_size)

            if (epoch + 1) % 5 == 0:
                h_train = net.extract_features(X_train)
                h_test = net.extract_features(X_test)

                # Ridge readout
                lam = 0.5
                W_out = np.linalg.solve(h_train.T @ h_train + lam * np.eye(h_train.shape[1]),
                                        h_train.T @ one_hot(y_train))
                preds = np.argmax(h_test @ W_out, axis=1)
                acc = accuracy(preds, y_test)

                # Entropy stats
                ents = []
                h = net.hd.encode(X_train[:1000])
                for layer in net.layers:
                    h, _ = layer.tropical_forward(h)
                    ents.append(neuron_entropy(h).mean())
                ent_str = " | ".join([f"L{i}={e:.3f}" for i, e in enumerate(ents)])
                print(f"  Epoch {epoch+1}: {acc:.2f}% | {ent_str}")

        # Final
        h_train = net.extract_features(X_train)
        h_test = net.extract_features(X_test)
        lam = 0.3
        W_out = np.linalg.solve(h_train.T @ h_train + lam * np.eye(h_train.shape[1]),
                                h_train.T @ one_hot(y_train))
        preds = np.argmax(h_test @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("HOLY GRAIL: Entropic Competitive Tropical Predictive", final_acc, t.elapsed,
           "NOVEL ARCHITECTURE: HD + Tropical + PredCoding + Entropy + AdaptiveTemp")

if __name__ == "__main__":
    main()
