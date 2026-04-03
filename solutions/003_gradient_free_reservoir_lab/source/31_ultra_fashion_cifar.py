"""
#31 - Ultra Reservoir on Fashion-MNIST and CIFAR-10
The real test: does the multi-reservoir paradigm hold on harder data?
Fashion-MNIST: same shape as MNIST but clothing items (harder)
CIFAR-10: 32x32x3 color images (much harder)
"""
import numpy as np
import sys
import struct
import gzip
import urllib.request
import os
import pickle
import tarfile
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import one_hot, accuracy, report, Timer
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_fashion_mnist(n_train=60000, n_test=10000):
    """Load Fashion-MNIST."""
    data_path = DATA_DIR / "fashion"
    data_path.mkdir(parents=True, exist_ok=True)
    base_url = "http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/"
    files = {
        'train_images': 'train-images-idx3-ubyte.gz',
        'train_labels': 'train-labels-idx1-ubyte.gz',
        'test_images': 't10k-images-idx3-ubyte.gz',
        'test_labels': 't10k-labels-idx1-ubyte.gz',
    }
    for key, fname in files.items():
        fpath = data_path / fname
        if not fpath.exists():
            print(f"Downloading {fname}...")
            urllib.request.urlretrieve(base_url + fname, fpath)

    def read_images(path):
        with gzip.open(path, 'rb') as f:
            magic, num, rows, cols = struct.unpack('>IIII', f.read(16))
            return np.frombuffer(f.read(), dtype=np.uint8).reshape(num, rows*cols).astype(np.float32) / 255.0

    def read_labels(path):
        with gzip.open(path, 'rb') as f:
            magic, num = struct.unpack('>II', f.read(8))
            return np.frombuffer(f.read(), dtype=np.uint8)

    X_train = read_images(data_path / files['train_images'])[:n_train]
    y_train = read_labels(data_path / files['train_labels'])[:n_train]
    X_test = read_images(data_path / files['test_images'])[:n_test]
    y_test = read_labels(data_path / files['test_labels'])[:n_test]
    return X_train, y_train, X_test, y_test

def load_cifar10(n_train=50000, n_test=10000):
    """Load CIFAR-10."""
    data_path = DATA_DIR / "cifar10"
    data_path.mkdir(parents=True, exist_ok=True)
    archive = data_path / "cifar-10-python.tar.gz"

    if not (data_path / "cifar-10-batches-py").exists():
        url = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
        print("Downloading CIFAR-10 (~170MB)...")
        urllib.request.urlretrieve(url, archive)
        print("Extracting...")
        with tarfile.open(archive, 'r:gz') as tar:
            tar.extractall(data_path)

    def unpickle(file):
        with open(file, 'rb') as fo:
            return pickle.load(fo, encoding='bytes')

    batches_dir = data_path / "cifar-10-batches-py"
    X_train, y_train = [], []
    for i in range(1, 6):
        d = unpickle(batches_dir / f"data_batch_{i}")
        X_train.append(d[b'data'])
        y_train.extend(d[b'labels'])
    X_train = np.vstack(X_train).astype(np.float32) / 255.0
    y_train = np.array(y_train, dtype=np.uint8)

    d = unpickle(batches_dir / "test_batch")
    X_test = d[b'data'].astype(np.float32) / 255.0
    y_test = np.array(d[b'labels'], dtype=np.uint8)

    return X_train[:n_train], y_train[:n_train], X_test[:n_test], y_test[:n_test]


class Reservoir:
    def __init__(self, in_dim, size, sr, sp, isc, activation='tanh', seed=None):
        rng = np.random.RandomState(seed)
        self.W_in = rng.randn(in_dim, size).astype(np.float32) * isc
        W = rng.randn(size, size).astype(np.float32)
        mask = rng.rand(size, size) < sp
        W *= mask
        eigs = np.abs(np.linalg.eigvals(W))
        mx = max(eigs) if len(eigs) > 0 else 1.0
        if mx > 0: W *= sr / mx
        self.W = W
        self.act = np.tanh if activation == 'tanh' else lambda x: np.maximum(x, 0)
        self.size = size

    def transform(self, X, steps=5):
        state = np.zeros((len(X), self.size), dtype=np.float32)
        drive = X @ self.W_in
        for _ in range(steps):
            state = self.act(drive + state @ self.W)
        return state


def ultra_reservoir(X_train, y_train, X_test, y_test, input_dim, dataset_name):
    """Run Ultra Reservoir on any dataset."""
    n_classes = len(np.unique(y_train))

    # HD encoding
    np.random.seed(42)
    hd_dim = min(2000, input_dim * 2)
    proj_hd = np.random.choice([-1, 1], size=(input_dim, hd_dim)).astype(np.float32) / np.sqrt(hd_dim)
    X_hd = np.sign(X_train @ proj_hd)
    X_hd_t = np.sign(X_test @ proj_hd)

    # Whitened
    np.random.seed(99)
    white_dim = min(500, input_dim)
    proj_w = np.random.randn(input_dim, white_dim).astype(np.float32) / np.sqrt(white_dim)
    X_w = X_train @ proj_w; X_w -= X_w.mean(axis=0)
    X_w_t = X_test @ proj_w; X_w_t -= X_w_t.mean(axis=0)

    configs = [
        ('raw', input_dim, 2000, 0.9, 0.05, 0.1, 'tanh', 5, 10),
        ('raw', input_dim, 2000, 0.99, 0.02, 0.05, 'tanh', 8, 20),
        ('raw', input_dim, 1500, 0.8, 0.1, 0.2, 'relu', 3, 30),
        ('hd', hd_dim, 1500, 0.95, 0.03, 0.1, 'tanh', 5, 40),
        ('hd', hd_dim, 1500, 0.85, 0.08, 0.15, 'tanh', 4, 50),
        ('white', white_dim, 1000, 0.9, 0.05, 0.2, 'tanh', 6, 60),
        ('white', white_dim, 1000, 0.98, 0.01, 0.1, 'tanh', 10, 70),
        ('raw', input_dim, 1000, 0.92, 0.04, 0.12, 'relu', 4, 80),
    ]

    inputs = {
        'raw': (X_train, X_test),
        'hd': (X_hd, X_hd_t),
        'white': (X_w, X_w_t)
    }

    all_train, all_test = [], []
    for i, (inp, in_dim, size, sr, sp, isc, act, steps, seed) in enumerate(configs):
        print(f"  Reservoir {i+1}/{len(configs)}: {inp} size={size} sr={sr}", flush=True)
        res = Reservoir(in_dim, size, sr, sp, isc, act, seed)
        Xtr, Xte = inputs[inp]
        all_train.append(res.transform(Xtr, steps))
        all_test.append(res.transform(Xte, steps))

    H_tr = np.hstack(all_train)
    H_te = np.hstack(all_test)
    print(f"  Features: {H_tr.shape[1]}", flush=True)

    # Ridge regression readout
    targets = one_hot(y_train, n_classes)
    lam = 0.01
    W_out = np.linalg.solve(H_tr.T @ H_tr + lam * np.eye(H_tr.shape[1]), H_tr.T @ targets)
    preds = np.argmax(H_te @ W_out, axis=1)
    acc = accuracy(preds, y_test)
    print(f"  Direct readout: {acc:.2f}%", flush=True)

    # Stacked reservoir
    print(f"  Building stacked reservoir...", flush=True)
    meta = Reservoir(H_tr.shape[1], 2000, 0.9, 0.03, 0.01, 'tanh', seed=100)
    Hm_tr = meta.transform(H_tr, steps=3)
    Hm_te = meta.transform(H_te, steps=3)
    Hs_tr = np.hstack([H_tr, Hm_tr])
    Hs_te = np.hstack([H_te, Hm_te])
    W_s = np.linalg.solve(Hs_tr.T @ Hs_tr + 0.01 * np.eye(Hs_tr.shape[1]), Hs_tr.T @ targets)
    preds_s = np.argmax(Hs_te @ W_s, axis=1)
    acc_s = accuracy(preds_s, y_test)
    print(f"  Stacked readout: {acc_s:.2f}%", flush=True)

    return max(acc, acc_s), acc, acc_s


def main():
    # === FASHION-MNIST ===
    print("=" * 60)
    print("FASHION-MNIST")
    print("=" * 60)
    X_tr, y_tr, X_te, y_te = load_fashion_mnist(n_train=60000, n_test=10000)
    print(f"Loaded: {len(X_tr)} train, {len(X_te)} test")

    with Timer("Ultra Reservoir / Fashion-MNIST") as t:
        best, direct, stacked = ultra_reservoir(X_tr, y_tr, X_te, y_te, 784, "Fashion-MNIST")
    report("Ultra Reservoir / Fashion-MNIST", best, t.elapsed,
           f"Direct={direct:.1f}% Stacked={stacked:.1f}%. Backprop baseline ~90-92%")

    # === CIFAR-10 ===
    print("\n" + "=" * 60)
    print("CIFAR-10")
    print("=" * 60)
    X_tr, y_tr, X_te, y_te = load_cifar10(n_train=50000, n_test=10000)
    print(f"Loaded: {len(X_tr)} train, {len(X_te)} test, dim={X_tr.shape[1]}")

    with Timer("Ultra Reservoir / CIFAR-10") as t:
        best, direct, stacked = ultra_reservoir(X_tr, y_tr, X_te, y_te, 3072, "CIFAR-10")
    report("Ultra Reservoir / CIFAR-10", best, t.elapsed,
           f"Direct={direct:.1f}% Stacked={stacked:.1f}%. Backprop CNN baseline ~93-95%")

if __name__ == "__main__":
    main()
