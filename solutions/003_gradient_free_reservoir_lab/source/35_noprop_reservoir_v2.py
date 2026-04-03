"""
#35 - NoProp + Reservoir V2: Scaled Up
Push the NoProp+Reservoir architecture to maximum performance.
- More blocks (10 instead of 6)
- Larger reservoirs (2000 instead of 1000)
- Multiple denoising passes with averaging
- Diversity: different spectral radii, sparsities, input projections
- Test on MNIST, Fashion-MNIST
"""
import numpy as np
import sys
import struct, gzip
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import load_mnist, one_hot, accuracy, report, Timer
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_fashion_mnist(n_train=60000, n_test=10000):
    data_path = DATA_DIR / "fashion"
    data_path.mkdir(parents=True, exist_ok=True)
    base_url = "http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/"
    files = {'train_images': 'train-images-idx3-ubyte.gz', 'train_labels': 'train-labels-idx1-ubyte.gz',
             'test_images': 't10k-images-idx3-ubyte.gz', 'test_labels': 't10k-labels-idx1-ubyte.gz'}
    for key, fname in files.items():
        fpath = data_path / fname
        if not fpath.exists():
            import urllib.request
            print(f"Downloading {fname}...")
            urllib.request.urlretrieve(base_url + fname, fpath)
    def read_images(p):
        with gzip.open(p, 'rb') as f:
            struct.unpack('>IIII', f.read(16))
            return np.frombuffer(f.read(), dtype=np.uint8).reshape(-1, 784).astype(np.float32) / 255.0
    def read_labels(p):
        with gzip.open(p, 'rb') as f:
            struct.unpack('>II', f.read(8))
            return np.frombuffer(f.read(), dtype=np.uint8)
    return (read_images(data_path / files['train_images'])[:n_train],
            read_labels(data_path / files['train_labels'])[:n_train],
            read_images(data_path / files['test_images'])[:n_test],
            read_labels(data_path / files['test_labels'])[:n_test])

class ReservoirBlock:
    def __init__(self, feat_dim, res_size, label_dim, noise_level, sr, sp, seed):
        rng = np.random.RandomState(seed)
        total = feat_dim + label_dim
        self.W_in = rng.randn(total, res_size).astype(np.float32) * 0.1
        W = rng.randn(res_size, res_size).astype(np.float32)
        W *= (rng.rand(res_size, res_size) < sp)
        eigs = np.abs(np.linalg.eigvals(W))
        mx = max(eigs) if len(eigs) > 0 else 1.0
        if mx > 0: W *= sr / mx
        self.W_res = W
        self.res_size = res_size
        self.noise_level = noise_level
        self.W_out = None

    def _transform(self, combined, steps=3):
        state = np.zeros((len(combined), self.res_size), dtype=np.float32)
        drive = combined @ self.W_in
        for _ in range(steps):
            state = np.tanh(drive + state @ self.W_res)
        return state

    def fit(self, features, labels, reg=0.05):
        noise = np.random.randn(len(features), labels.shape[1]).astype(np.float32) * self.noise_level
        H = self._transform(np.hstack([features, labels + noise]))
        self.W_out = np.linalg.solve(H.T @ H + reg * np.eye(self.res_size), H.T @ labels)

    def denoise(self, features, noisy_labels):
        H = self._transform(np.hstack([features, noisy_labels]))
        return H @ self.W_out

class NoPropReservoirV2:
    def __init__(self, input_dim, label_dim=10, n_blocks=10, res_size=1500):
        self.blocks = []
        self.projections = []
        noise_levels = np.linspace(2.0, 0.05, n_blocks)
        proj_dims = [600, 500, 400, 600, 500, 400, 600, 500, 400, 300]

        for i in range(n_blocks):
            pd = proj_dims[i % len(proj_dims)]
            rng = np.random.RandomState(i * 31 + 7)
            self.projections.append(rng.randn(input_dim, pd).astype(np.float32) * np.sqrt(2.0 / input_dim))

            sr = 0.8 + 0.15 * (i / n_blocks)
            sp = 0.02 + 0.03 * (i / n_blocks)
            self.blocks.append(ReservoirBlock(pd, res_size, label_dim, noise_levels[i], sr, sp, seed=i*100+1))

        self.n_blocks = n_blocks

    def fit(self, X, y_oh, reg=0.05):
        for i, (block, proj) in enumerate(zip(self.blocks, self.projections)):
            features = np.tanh(X @ proj)
            block.fit(features, y_oh, reg)
            print(f"  Block {i+1}/{self.n_blocks} trained", flush=True)

    def predict(self, X, n_passes=10):
        all_preds = []
        for p in range(n_passes):
            est = np.random.randn(len(X), 10).astype(np.float32) * 2.0
            for block, proj in zip(self.blocks, self.projections):
                features = np.tanh(X @ proj)
                est = block.denoise(features, est)
            all_preds.append(est)
        avg = np.mean(all_preds, axis=0)
        return np.argmax(avg, axis=1)

def main():
    # === MNIST ===
    print("=" * 60)
    print("NoProp+Reservoir V2 / MNIST")
    print("=" * 60)
    X_tr, y_tr, X_te, y_te = load_mnist(n_train=30000, n_test=10000)

    net = NoPropReservoirV2(784, n_blocks=8, res_size=1500)
    with Timer("NoProp+Reservoir V2 / MNIST") as t:
        net.fit(X_tr, one_hot(y_tr))
        for np_ in [1, 5, 10]:
            preds = net.predict(X_te, n_passes=np_)
            acc = accuracy(preds, y_te)
            print(f"  {np_}-pass: {acc:.2f}%", flush=True)
        preds = net.predict(X_te, n_passes=10)
        acc_mnist = accuracy(preds, y_te)
    report("NoProp+Reservoir V2 / MNIST", acc_mnist, t.elapsed, "Scaled up: 8 blocks, 1500-dim reservoirs, 10 passes")

    # === Fashion-MNIST ===
    print("\n" + "=" * 60)
    print("NoProp+Reservoir V2 / Fashion-MNIST")
    print("=" * 60)
    X_tr, y_tr, X_te, y_te = load_fashion_mnist(n_train=60000, n_test=10000)

    net2 = NoPropReservoirV2(784, n_blocks=8, res_size=1500)
    with Timer("NoProp+Reservoir V2 / Fashion") as t2:
        net2.fit(X_tr, one_hot(y_tr))
        preds = net2.predict(X_te, n_passes=10)
        acc_fashion = accuracy(preds, y_te)
        print(f"  Fashion-MNIST: {acc_fashion:.2f}%", flush=True)
    report("NoProp+Reservoir V2 / Fashion-MNIST", acc_fashion, t2.elapsed, "8 blocks, 1500-dim, 10 passes")

if __name__ == "__main__":
    main()
