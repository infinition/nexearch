"""
#21 - Direct Feedback Alignment (DFA)
Use random FIXED feedback weights instead of transposed forward weights.
This breaks the weight transport problem while still using error signals.
Technically uses loss gradient at output but NOT backpropagation.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer, relu, softmax

class DFANetwork:
    def __init__(self, layer_sizes, lr=0.01):
        self.n_layers = len(layer_sizes) - 1
        self.W = []
        self.b = []
        self.B = []  # Fixed random feedback matrices

        for i in range(self.n_layers):
            self.W.append(np.random.randn(layer_sizes[i], layer_sizes[i+1]).astype(np.float32) * 0.05)
            self.b.append(np.zeros(layer_sizes[i+1], dtype=np.float32))

            # Random feedback from output directly to this layer
            if i < self.n_layers - 1:
                self.B.append(np.random.randn(layer_sizes[-1], layer_sizes[i+1]).astype(np.float32) * 0.05)

        self.lr = lr

    def forward(self, x):
        activations = [x]
        pre_activations = []
        h = x
        for i in range(self.n_layers - 1):
            z = h @ self.W[i] + self.b[i]
            pre_activations.append(z)
            h = relu(z)
            activations.append(h)

        # Output (no activation for softmax later)
        z = h @ self.W[-1] + self.b[-1]
        pre_activations.append(z)
        h = z  # linear output
        activations.append(h)

        return activations, pre_activations

    def train_step(self, x, y_oh):
        activations, pre_activations = self.forward(x)
        batch_size = len(x)

        # Output error (this is the only "gradient" - just output error)
        output = softmax(activations[-1])
        error = output - y_oh  # (batch, n_classes)

        # Update output layer (normal gradient)
        self.W[-1] -= self.lr * (activations[-2].T @ error) / batch_size
        self.b[-1] -= self.lr * error.mean(axis=0)

        # Update hidden layers using DIRECT random feedback
        for i in range(self.n_layers - 1):
            # Project error directly to hidden layer via random B
            hidden_error = error @ self.B[i]  # (batch, hidden_dim)
            # Mask by ReLU derivative
            mask = (pre_activations[i] > 0).astype(np.float32)
            hidden_error *= mask

            self.W[i] -= self.lr * (activations[i].T @ hidden_error) / batch_size
            self.b[i] -= self.lr * hidden_error.mean(axis=0)

    def predict(self, x):
        h = x
        for i in range(self.n_layers - 1):
            h = relu(h @ self.W[i] + self.b[i])
        h = h @ self.W[-1] + self.b[-1]
        return np.argmax(h, axis=1)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    net = DFANetwork([784, 500, 300, 10], lr=0.05)
    n_epochs = 20
    batch_size = 128

    with Timer("Direct Feedback Alignment") as t:
        for epoch in range(n_epochs):
            perm = np.random.permutation(len(X_train))
            for i in range(0, len(X_train), batch_size):
                idx = perm[i:i+batch_size]
                net.train_step(X_train[idx], one_hot(y_train[idx]))

            if (epoch + 1) % 5 == 0:
                preds = net.predict(X_test)
                acc = accuracy(preds, y_test)
                print(f"  Epoch {epoch+1}: {acc:.2f}%")

        preds = net.predict(X_test)
        final_acc = accuracy(preds, y_test)

    report("Direct Feedback Alignment", final_acc, t.elapsed,
           "Random feedback weights, no weight transport. Partially gradient-free.")

if __name__ == "__main__":
    main()
