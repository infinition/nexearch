"""Common utilities for all gradient-free experiments."""
import numpy as np
import time
import struct
import os
import gzip
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_mnist(n_train=5000, n_test=1000):
    """Load MNIST - download if needed, fast subset for validation."""
    data_path = DATA_DIR / "mnist"
    data_path.mkdir(parents=True, exist_ok=True)

    files = {
        'train_images': 'train-images-idx3-ubyte.gz',
        'train_labels': 'train-labels-idx1-ubyte.gz',
        'test_images': 't10k-images-idx3-ubyte.gz',
        'test_labels': 't10k-labels-idx1-ubyte.gz',
    }

    # Try to download if not present
    base_url = "https://storage.googleapis.com/cvdf-datasets/mnist/"
    for key, fname in files.items():
        fpath = data_path / fname
        if not fpath.exists():
            import urllib.request
            print(f"Downloading {fname}...")
            urllib.request.urlretrieve(base_url + fname, fpath)

    def read_images(path):
        with gzip.open(path, 'rb') as f:
            magic, num, rows, cols = struct.unpack('>IIII', f.read(16))
            data = np.frombuffer(f.read(), dtype=np.uint8)
            return data.reshape(num, rows * cols).astype(np.float32) / 255.0

    def read_labels(path):
        with gzip.open(path, 'rb') as f:
            magic, num = struct.unpack('>II', f.read(8))
            return np.frombuffer(f.read(), dtype=np.uint8)

    X_train = read_images(data_path / files['train_images'])[:n_train]
    y_train = read_labels(data_path / files['train_labels'])[:n_train]
    X_test = read_images(data_path / files['test_images'])[:n_test]
    y_test = read_labels(data_path / files['test_labels'])[:n_test]

    return X_train, y_train, X_test, y_test

def one_hot(y, n_classes=10):
    oh = np.zeros((len(y), n_classes), dtype=np.float32)
    oh[np.arange(len(y)), y] = 1.0
    return oh

def accuracy(predictions, labels):
    return np.mean(predictions == labels) * 100

def relu(x):
    return np.maximum(0, x)

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def normalize_rows(x):
    norms = np.linalg.norm(x, axis=1, keepdims=True) + 1e-8
    return x / norms

class Timer:
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, *args):
        self.elapsed = time.time() - self.start
        print(f"[{self.name}] {self.elapsed:.2f}s")

def report(method_name, acc, elapsed, notes=""):
    print(f"\n{'='*60}")
    print(f"Method: {method_name}")
    print(f"MNIST Accuracy: {acc:.2f}%")
    print(f"Time: {elapsed:.2f}s")
    if notes:
        print(f"Notes: {notes}")
    print(f"{'='*60}\n")
    return {"method": method_name, "accuracy": acc, "time": elapsed, "notes": notes}
