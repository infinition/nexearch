"""
#12 - Kanerva Sparse Distributed Memory
Binary address space, distributed storage/retrieval.
Classic cognitive architecture, gradient-free by design.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer

class SparseDistributedMemory:
    def __init__(self, address_dim, data_dim, n_locations=5000, access_radius=None):
        self.n_locations = n_locations
        self.data_dim = data_dim

        # Hard addresses (random binary)
        self.addresses = np.random.choice([-1, 1], size=(n_locations, address_dim)).astype(np.float32)
        # Data counters
        self.data = np.zeros((n_locations, data_dim), dtype=np.float32)

        if access_radius is None:
            # Auto-set radius to activate ~1% of locations
            self.radius = int(address_dim * 0.47)
        else:
            self.radius = access_radius

    def _get_activated(self, address):
        """Find locations within Hamming radius."""
        # Hamming distance via dot product (for bipolar: d_H = (n - dot) / 2)
        dots = address @ self.addresses.T
        distances = (address.shape[-1] - dots) / 2
        activated = distances <= self.radius
        return activated

    def write(self, address, data):
        """Write data to all activated locations."""
        activated = self._get_activated(address)  # (batch, n_locations)
        for i in range(len(address)):
            locs = np.where(activated[i])[0]
            if len(locs) > 0:
                self.data[locs] += data[i]

    def read(self, address):
        """Read by summing data from activated locations."""
        activated = self._get_activated(address)  # (batch, n_locations)
        result = np.zeros((len(address), self.data_dim), dtype=np.float32)
        for i in range(len(address)):
            locs = np.where(activated[i])[0]
            if len(locs) > 0:
                result[i] = self.data[locs].sum(axis=0)
        return result

def binarize(X, threshold=0.3):
    """Convert to bipolar."""
    return np.where(X > threshold, 1, -1).astype(np.float32)

def main():
    print("Loading MNIST...")
    X_train, y_train, X_test, y_test = load_mnist(n_train=10000, n_test=2000)

    # Binarize inputs
    X_train_bin = binarize(X_train)
    X_test_bin = binarize(X_test)

    sdm = SparseDistributedMemory(
        address_dim=784, data_dim=10,
        n_locations=8000, access_radius=370
    )

    with Timer("Kanerva SDM") as t:
        # Write: store label at address
        labels_oh = one_hot(y_train) * 2 - 1  # bipolar labels
        sdm.write(X_train_bin, labels_oh)

        # Read: retrieve label for test addresses
        retrieved = sdm.read(X_test_bin)
        preds = np.argmax(retrieved, axis=1)
        final_acc = accuracy(preds, y_test)

    report("Kanerva Sparse Distributed Memory", final_acc, t.elapsed,
           "Binary address space, no training loop. One-shot associative memory.")

if __name__ == "__main__":
    main()
