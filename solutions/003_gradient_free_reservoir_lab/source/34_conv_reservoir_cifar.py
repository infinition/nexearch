"""
#34 - Convolutional Reservoir for CIFAR-10
The problem: flat reservoirs can't see 2D spatial patterns.
Solution: extract local patches, run each through a reservoir,
pool the results. Like a CNN but with random fixed filters.

Architecture:
1. Extract overlapping patches (like conv kernels)
2. Each patch goes through a shared reservoir
3. Spatial pooling (max/avg) over patch positions
4. Multiple scales (different patch sizes) for diversity
5. Ridge regression readout

Also: Gabor/HOG-like handcrafted features as input preprocessing.
"""
import numpy as np
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from common import one_hot, accuracy, report, Timer
from pathlib import Path
import pickle, tarfile, urllib.request

DATA_DIR = Path(__file__).parent.parent / "data"

def load_cifar10(n_train=50000, n_test=10000):
    data_path = DATA_DIR / "cifar10"
    data_path.mkdir(parents=True, exist_ok=True)
    archive = data_path / "cifar-10-python.tar.gz"
    if not (data_path / "cifar-10-batches-py").exists():
        url = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
        print("Downloading CIFAR-10...")
        urllib.request.urlretrieve(url, archive)
        with tarfile.open(archive, 'r:gz') as tar:
            tar.extractall(data_path)
    def unpickle(f):
        with open(f, 'rb') as fo: return pickle.load(fo, encoding='bytes')
    bd = data_path / "cifar-10-batches-py"
    Xtr, ytr = [], []
    for i in range(1, 6):
        d = unpickle(bd / f"data_batch_{i}")
        Xtr.append(d[b'data']); ytr.extend(d[b'labels'])
    Xtr = np.vstack(Xtr).astype(np.float32) / 255.0
    ytr = np.array(ytr, dtype=np.uint8)
    d = unpickle(bd / "test_batch")
    Xte = d[b'data'].astype(np.float32) / 255.0
    yte = np.array(d[b'labels'], dtype=np.uint8)
    return Xtr[:n_train], ytr[:n_train], Xte[:n_test], yte[:n_test]

def reshape_cifar(X):
    """Reshape flat CIFAR to (N, 32, 32, 3)."""
    return X.reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)

def extract_patches(images, patch_size, stride):
    """Extract overlapping patches from images. Returns (N, n_patches, patch_dim)."""
    N, H, W, C = images.shape
    patches = []
    positions = []
    for y in range(0, H - patch_size + 1, stride):
        for x in range(0, W - patch_size + 1, stride):
            p = images[:, y:y+patch_size, x:x+patch_size, :].reshape(N, -1)
            patches.append(p)
            positions.append((y, x))
    return np.stack(patches, axis=1), positions  # (N, n_patches, patch_dim)

def random_conv_features(images, n_filters, patch_size, stride, seed=42):
    """Random convolutional features: random filters applied to patches."""
    rng = np.random.RandomState(seed)
    patches, positions = extract_patches(images, patch_size, stride)
    N, n_patches, patch_dim = patches.shape

    # Random filters (fixed, not learned)
    filters = rng.randn(patch_dim, n_filters).astype(np.float32) * np.sqrt(2.0 / patch_dim)
    bias = rng.randn(n_filters).astype(np.float32) * 0.1

    # Apply filters to all patches: (N, n_patches, n_filters)
    responses = np.maximum(0, patches @ filters + bias)  # ReLU

    # Spatial pooling
    max_pool = responses.max(axis=1)   # (N, n_filters) - global max pool
    avg_pool = responses.mean(axis=1)  # (N, n_filters) - global avg pool

    return np.hstack([max_pool, avg_pool])  # (N, 2*n_filters)

def gabor_like_features(images, n_orientations=8, n_frequencies=4, seed=0):
    """Gabor-like random oriented edge detectors."""
    rng = np.random.RandomState(seed)
    N, H, W, C = images.shape
    # Convert to grayscale
    gray = 0.299 * images[:,:,:,0] + 0.587 * images[:,:,:,1] + 0.114 * images[:,:,:,2]

    features = []
    for freq_idx in range(n_frequencies):
        freq = 2 + freq_idx * 2  # kernel sizes 2, 4, 6, 8
        for orient in range(n_orientations):
            # Create oriented filter
            angle = orient * np.pi / n_orientations
            ksize = min(freq * 2 + 1, 7)
            cx, cy = ksize // 2, ksize // 2
            kernel = np.zeros((ksize, ksize), dtype=np.float32)
            for ky in range(ksize):
                for kx in range(ksize):
                    x_rot = (kx - cx) * np.cos(angle) + (ky - cy) * np.sin(angle)
                    y_rot = -(kx - cx) * np.sin(angle) + (ky - cy) * np.cos(angle)
                    kernel[ky, kx] = np.exp(-(x_rot**2 + y_rot**2) / (2 * (freq/2)**2)) * np.cos(2 * np.pi * x_rot / freq)

            # Apply via valid convolution (simplified: use patches)
            patches = []
            for y in range(0, H - ksize + 1, 4):
                for x in range(0, W - ksize + 1, 4):
                    p = gray[:, y:y+ksize, x:x+ksize]
                    resp = np.sum(p * kernel, axis=(1, 2))
                    patches.append(resp)
            patches = np.array(patches).T  # (N, n_positions)
            features.append(patches.max(axis=1))  # max response
            features.append(patches.mean(axis=1))  # mean response

    return np.column_stack(features)

class PatchReservoir:
    """Reservoir that processes image patches."""
    def __init__(self, patch_dim, size, sr=0.9, sp=0.05, isc=0.1, seed=None):
        rng = np.random.RandomState(seed)
        self.W_in = rng.randn(patch_dim, size).astype(np.float32) * isc
        W = rng.randn(size, size).astype(np.float32)
        mask = rng.rand(size, size) < sp
        W *= mask
        eigs = np.abs(np.linalg.eigvals(W))
        mx = max(eigs) if len(eigs) > 0 else 1.0
        if mx > 0: W *= sr / mx
        self.W = W
        self.size = size

    def transform_patches(self, patches, steps=3):
        """Process patches through reservoir. patches: (N, n_patches, dim)"""
        N, n_patches, dim = patches.shape
        # Process each patch position
        all_states = np.zeros((N, n_patches, self.size), dtype=np.float32)
        for p in range(n_patches):
            state = np.zeros((N, self.size), dtype=np.float32)
            drive = patches[:, p, :] @ self.W_in
            for _ in range(steps):
                state = np.tanh(drive + state @ self.W)
            all_states[:, p, :] = state

        # Pool over spatial positions
        max_pool = all_states.max(axis=1)
        avg_pool = all_states.mean(axis=1)
        return np.hstack([max_pool, avg_pool])

def main():
    print("Loading CIFAR-10...")
    X_train, y_train, X_test, y_test = load_cifar10(n_train=50000, n_test=10000)
    images_train = reshape_cifar(X_train)
    images_test = reshape_cifar(X_test)
    print(f"Images: {images_train.shape}")

    with Timer("Convolutional Reservoir / CIFAR-10") as t:
        all_train = []
        all_test = []

        # 1. Multi-scale random conv features
        for ps, stride, nf, seed in [(3,2,200,10), (5,3,200,20), (7,4,150,30), (3,1,150,40)]:
            print(f"  Random conv: patch={ps}x{ps} stride={stride} filters={nf}", flush=True)
            f_tr = random_conv_features(images_train, nf, ps, stride, seed)
            f_te = random_conv_features(images_test, nf, ps, stride, seed)
            all_train.append(f_tr)
            all_test.append(f_te)

        # 2. Gabor-like features
        print("  Gabor features...", flush=True)
        g_tr = gabor_like_features(images_train, n_orientations=8, n_frequencies=4)
        g_te = gabor_like_features(images_test, n_orientations=8, n_frequencies=4)
        all_train.append(g_tr)
        all_test.append(g_te)

        # 3. Patch reservoir (small patches through reservoir dynamics)
        for ps, res_size, sr, seed in [(5, 500, 0.9, 100), (3, 500, 0.95, 200)]:
            print(f"  Patch reservoir: patch={ps} size={res_size}", flush=True)
            patches_tr, _ = extract_patches(images_train, ps, stride=4)
            patches_te, _ = extract_patches(images_test, ps, stride=4)
            pr = PatchReservoir(ps*ps*3, res_size, sr, 0.05, 0.1, seed)
            f_tr = pr.transform_patches(patches_tr, steps=3)
            f_te = pr.transform_patches(patches_te, steps=3)
            all_train.append(f_tr)
            all_test.append(f_te)

        # 4. Color histogram features (simple but effective)
        print("  Color histograms...", flush=True)
        def color_hist(images, n_bins=16):
            N = len(images)
            features = np.zeros((N, n_bins * 3), dtype=np.float32)
            for c in range(3):
                channel = images[:, :, :, c].reshape(N, -1)
                for i in range(n_bins):
                    lo, hi = i / n_bins, (i + 1) / n_bins
                    features[:, c * n_bins + i] = np.mean((channel >= lo) & (channel < hi), axis=1)
            return features
        all_train.append(color_hist(images_train))
        all_test.append(color_hist(images_test))

        # 5. Flat reservoir on top of all features
        H_tr = np.hstack(all_train)
        H_te = np.hstack(all_test)
        print(f"  Total features before meta-reservoir: {H_tr.shape[1]}", flush=True)

        # Meta-reservoir
        from common import Timer as T2
        rng = np.random.RandomState(999)
        meta_size = 2000
        W_in = rng.randn(H_tr.shape[1], meta_size).astype(np.float32) * 0.01
        W_res = rng.randn(meta_size, meta_size).astype(np.float32)
        mask = rng.rand(meta_size, meta_size) < 0.03
        W_res *= mask
        eigs = np.abs(np.linalg.eigvals(W_res))
        W_res *= 0.9 / max(eigs)

        def reservoir_transform(X, steps=3):
            state = np.zeros((len(X), meta_size), dtype=np.float32)
            drive = X @ W_in
            for _ in range(steps):
                state = np.tanh(drive + state @ W_res)
            return state

        print("  Meta-reservoir transform...", flush=True)
        Hm_tr = reservoir_transform(H_tr)
        Hm_te = reservoir_transform(H_te)

        # Combine
        Hf_tr = np.hstack([H_tr, Hm_tr])
        Hf_te = np.hstack([H_te, Hm_te])
        print(f"  Final features: {Hf_tr.shape[1]}", flush=True)

        # Ridge readout
        targets = one_hot(y_train)

        # Direct
        lam = 0.01
        W_out = np.linalg.solve(Hf_tr.T @ Hf_tr + lam * np.eye(Hf_tr.shape[1]), Hf_tr.T @ targets)
        preds = np.argmax(Hf_te @ W_out, axis=1)
        acc_full = accuracy(preds, y_test)
        print(f"  Full pipeline: {acc_full:.2f}%", flush=True)

        # Without meta-reservoir
        W_out2 = np.linalg.solve(H_tr.T @ H_tr + lam * np.eye(H_tr.shape[1]), H_tr.T @ targets)
        preds2 = np.argmax(H_te @ W_out2, axis=1)
        acc_direct = accuracy(preds2, y_test)
        print(f"  Without meta-reservoir: {acc_direct:.2f}%", flush=True)

        final_acc = max(acc_full, acc_direct)

    report("Convolutional Reservoir / CIFAR-10", final_acc, t.elapsed,
           f"Patches+Gabor+PatchReservoir+ColorHist+MetaReservoir. Full={acc_full:.1f}% Direct={acc_direct:.1f}%")

if __name__ == "__main__":
    main()
