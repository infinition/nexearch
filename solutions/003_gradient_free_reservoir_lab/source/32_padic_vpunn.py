"""
#32 - v-PuNN: van der Put Neural Networks with VAPO Optimizer
p-Adic neural networks operating in ultrametric space.
Neurons are characteristic functions of p-adic balls.
VAPO = Valuation-Adaptive Perturbation Optimization (gradient-free).

Key properties:
- Totally disconnected space -> NO gradients exist
- Natural hierarchy: p-adic balls nest like a tree
- VAPO perturbs at different p-adic scales (valuations)

Reference: arXiv:2508.01010 (2025)
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

class PAdicEncoder:
    """Encode real-valued inputs into p-adic representations."""
    def __init__(self, input_dim, p=2, depth=8):
        self.p = p
        self.depth = depth
        self.input_dim = input_dim
        # Total encoded dimension: input_dim * depth (multi-scale)
        self.encoded_dim = input_dim * depth

    def encode(self, X):
        """Convert to p-adic digits at multiple scales (valuations)."""
        batch_size = len(X)
        encoded = np.zeros((batch_size, self.encoded_dim), dtype=np.float32)

        for d in range(self.depth):
            # Extract the d-th "p-adic digit" by quantizing at scale p^d
            scale = self.p ** d
            # Quantize to p levels at this scale
            quantized = np.floor(X * scale * self.p) % self.p
            encoded[:, d * self.input_dim:(d + 1) * self.input_dim] = quantized / (self.p - 1)

        return encoded

class PAdicBallNeuron:
    """A neuron that is the characteristic function of a p-adic ball.
    Activates when input is 'close' in the p-adic ultrametric."""
    def __init__(self, input_dim, center=None, radius_valuation=3, p=2):
        self.p = p
        if center is None:
            self.center = np.random.randn(input_dim).astype(np.float32) * 0.5
        else:
            self.center = center.copy()
        self.radius_val = radius_valuation  # p-adic radius = p^(-valuation)
        self.radius = p ** (-radius_valuation)

    def activate(self, x):
        """Ultrametric activation: max of component-wise differences."""
        # In p-adic space, distance = max(|x_i - c_i|_p)
        # We approximate with max of absolute differences at the relevant scale
        diff = np.abs(x - self.center)
        # Ultrametric: distance = max component (not L2!)
        dist = np.max(diff, axis=1)
        # Characteristic function of the ball (soft version)
        # Sharp: return (dist < self.radius).astype(np.float32)
        # Soft: smooth approximation
        return np.exp(-dist / (self.radius + 1e-8))

class VPuNNLayer:
    """Layer of p-adic ball neurons at a given valuation level."""
    def __init__(self, input_dim, n_neurons, p=2, valuation=3):
        self.neurons = []
        self.p = p
        self.valuation = valuation
        for _ in range(n_neurons):
            center = np.random.randn(input_dim).astype(np.float32) * 0.5
            self.neurons.append(PAdicBallNeuron(input_dim, center, valuation, p))
        self.n_neurons = n_neurons

    def forward(self, x):
        """Activate all neurons in this layer."""
        activations = np.zeros((len(x), self.n_neurons), dtype=np.float32)
        for i, neuron in enumerate(self.neurons):
            activations[:, i] = neuron.activate(x)
        return activations

    def get_centers(self):
        return np.array([n.center for n in self.neurons])

    def set_centers(self, centers):
        for i, n in enumerate(self.neurons):
            n.center = centers[i].copy()

class VPuNN:
    """van der Put Neural Network with multi-scale p-adic layers."""
    def __init__(self, input_dim, p=2, max_depth=5, neurons_per_level=50):
        self.p = p
        self.layers = []
        self.input_dim = input_dim
        self.encoder = PAdicEncoder(input_dim, p, depth=max_depth)

        # Create layers at different valuation levels
        # Each level has finer granularity
        for d in range(max_depth):
            n_neurons = neurons_per_level
            layer = VPuNNLayer(self.encoder.encoded_dim, n_neurons, p, valuation=d + 1)
            self.layers.append(layer)

        # Total feature dimension
        self.feature_dim = neurons_per_level * max_depth

    def extract_features(self, X):
        """Multi-scale p-adic feature extraction."""
        encoded = self.encoder.encode(X)
        features = []
        for layer in self.layers:
            features.append(layer.forward(encoded))
        return np.hstack(features)

class VAPO:
    """Valuation-Adaptive Perturbation Optimization.
    Gradient-free optimizer that perturbs at different p-adic scales."""
    def __init__(self, network, p=2, base_lr=0.1, n_perturbations=20):
        self.net = network
        self.p = p
        self.base_lr = base_lr
        self.n_perturbations = n_perturbations

    def step(self, X_batch, y_batch, W_out, loss_fn):
        """One VAPO optimization step."""
        best_improvement = 0
        best_layer_idx = -1
        best_new_centers = None

        # Try perturbations at different valuation levels
        for layer_idx, layer in enumerate(self.net.layers):
            valuation = layer.valuation
            # Step size adapts to the hierarchical level
            step_size = self.base_lr * (self.p ** (-valuation))

            centers = layer.get_centers()

            for _ in range(self.n_perturbations // len(self.net.layers)):
                # Random perturbation at this scale
                perturbation = np.random.randn(*centers.shape).astype(np.float32) * step_size

                # Try perturbation
                new_centers = centers + perturbation
                layer.set_centers(new_centers)

                # Evaluate
                features = self.net.extract_features(X_batch)
                preds = features @ W_out
                new_loss = loss_fn(preds, y_batch)

                # Restore
                layer.set_centers(centers)

                # Evaluate original
                features_orig = self.net.extract_features(X_batch)
                preds_orig = features_orig @ W_out
                orig_loss = loss_fn(preds_orig, y_batch)

                improvement = orig_loss - new_loss
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_layer_idx = layer_idx
                    best_new_centers = new_centers.copy()

        # Apply best perturbation
        if best_layer_idx >= 0 and best_new_centers is not None:
            self.net.layers[best_layer_idx].set_centers(best_new_centers)
            return best_improvement

        return 0

def mse_loss(preds, targets):
    return np.mean((preds - targets) ** 2)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)
    y_train_oh = one_hot(y_train)
    y_test_oh = one_hot(y_test)

    p = 3  # prime base
    net = VPuNN(784, p=p, max_depth=4, neurons_per_level=80)

    with Timer("v-PuNN + VAPO") as t:
        # Phase 1: Extract initial features + ridge readout
        print("  Phase 1: Initial features...", flush=True)
        H_train = net.extract_features(X_train)
        H_test = net.extract_features(X_test)
        print(f"  Feature dim: {H_train.shape[1]}", flush=True)

        lam = 0.1
        W_out = np.linalg.solve(H_train.T @ H_train + lam * np.eye(H_train.shape[1]),
                                H_train.T @ y_train_oh)
        preds = np.argmax(H_test @ W_out, axis=1)
        acc_init = accuracy(preds, y_test)
        print(f"  Initial accuracy: {acc_init:.2f}%", flush=True)

        # Phase 2: VAPO optimization of p-adic centers
        print("  Phase 2: VAPO optimization...", flush=True)
        optimizer = VAPO(net, p=p, base_lr=0.3, n_perturbations=20)

        n_vapo_steps = 30
        batch_size = 500
        for step in range(n_vapo_steps):
            idx = np.random.choice(len(X_train), batch_size, replace=False)
            improvement = optimizer.step(X_train[idx], y_train_oh[idx], W_out, mse_loss)

            # Re-fit readout periodically
            if (step + 1) % 5 == 0:
                H_train = net.extract_features(X_train)
                H_test = net.extract_features(X_test)
                W_out = np.linalg.solve(H_train.T @ H_train + lam * np.eye(H_train.shape[1]),
                                        H_train.T @ y_train_oh)
                preds = np.argmax(H_test @ W_out, axis=1)
                acc = accuracy(preds, y_test)
                print(f"  VAPO step {step+1}: {acc:.2f}% (improvement: {improvement:.6f})", flush=True)

        # Final evaluation
        H_train = net.extract_features(X_train)
        H_test = net.extract_features(X_test)
        W_out = np.linalg.solve(H_train.T @ H_train + lam * np.eye(H_train.shape[1]),
                                H_train.T @ y_train_oh)
        preds = np.argmax(H_test @ W_out, axis=1)
        final_acc = accuracy(preds, y_test)

    report("v-PuNN + VAPO (p-adic)", final_acc, t.elapsed,
           f"p={p}, 4 valuation levels, VAPO optimizer. Init={acc_init:.1f}% Final={final_acc:.1f}%")

if __name__ == "__main__":
    main()
