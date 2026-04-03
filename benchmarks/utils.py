"""
Nexearch — Shared benchmark utilities
=============================================
Standardized dataloaders, metrics, and timing for all solutions.
"""

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import time
import os

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasets')
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def get_dataset(name, batch_size_train=256, batch_size_test=2000):
    """Load a dataset from the shared datasets/ folder."""
    if name == 'mnist':
        t = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        train = datasets.MNIST(DATASET_DIR, train=True, download=True, transform=t)
        test = datasets.MNIST(DATASET_DIR, train=False, transform=t)
        return (DataLoader(train, batch_size=batch_size_train, shuffle=True, num_workers=0, pin_memory=True),
                DataLoader(test, batch_size=batch_size_test, shuffle=False, num_workers=0, pin_memory=True),
                {'input_dim': 784, 'num_classes': 10, 'input_shape': (1, 28, 28)})

    elif name == 'cifar10':
        train_t = transforms.Compose([
            transforms.RandomCrop(32, padding=4), transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
        ])
        test_t = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
        ])
        train = datasets.CIFAR10(DATASET_DIR, train=True, download=True, transform=train_t)
        test = datasets.CIFAR10(DATASET_DIR, train=False, transform=test_t)
        return (DataLoader(train, batch_size=batch_size_train, shuffle=True, num_workers=0, pin_memory=True),
                DataLoader(test, batch_size=batch_size_test, shuffle=False, num_workers=0, pin_memory=True),
                {'input_dim': 3072, 'num_classes': 10, 'input_shape': (3, 32, 32)})

    else:
        raise ValueError(f"Unknown dataset: {name}. Available: mnist, cifar10")


def evaluate(model, loader, device=DEVICE):
    """Standard evaluation: returns accuracy."""
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            if hasattr(model, 'extract_features'):
                h = model.extract_features(x)
                preds = model.probe(h).argmax(1)
            else:
                preds = model(x).argmax(1)
            correct += (preds == y).sum().item()
            total += y.size(0)
    return correct / total


def count_params(model):
    """Count total, trainable, and probe parameters."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    probe = sum(p.numel() for p in model.probe.parameters()) if hasattr(model, 'probe') else 0
    return {'total': total, 'trainable': trainable, 'probe': probe, 'local': total - probe}


class Timer:
    """Context manager for timing."""
    def __enter__(self):
        self.t0 = time.time()
        return self
    def __exit__(self, *args):
        self.elapsed = time.time() - self.t0
