"""Quick round 4: 5 epochs, fewer configs, unbuffered output."""
import sys
sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, '.')
from benchmark_round4_gradfree import *

if __name__ == '__main__':
    train_loader, test_loader = get_mnist(256)
    dims = [784, 500, 300, 10]
    N = 10  # Reduced

    results = {}
    results['Backprop'] = train_and_eval('Backprop', BackpropNet(dims), train_loader, test_loader, N, True)
    results['DirectLocal'] = train_and_eval('DirectLocal (grad)', DirectLocalNet(dims), train_loader, test_loader, N, True)
    results['ProtoLocal'] = train_and_eval('ProtoLocal (0-grad)', ProtoLocalNet(dims, lr=0.01), train_loader, test_loader, N, True)
    results['HebbFF'] = train_and_eval('HebbFF (0-grad)', HebbFFNet([784, 500, 300], lr=0.01), train_loader, test_loader, N, True)
    results['ContrastLocal'] = train_and_eval('ContrastLocal (0-grad)', ContrastLocalNet(dims, lr=0.01), train_loader, test_loader, N, True)

    # Wide variant of best
    dims_wide = [784, 1000, 500, 10]
    results['ContrastLocal-W'] = train_and_eval('ContrastLocal Wide', ContrastLocalNet(dims_wide, lr=0.01), train_loader, test_loader, N, True)
    results['ProtoLocal-W'] = train_and_eval('ProtoLocal Wide', ProtoLocalNet(dims_wide, lr=0.01), train_loader, test_loader, N, True)

    print("\n" + "="*70)
    print("  ROUND 4 RESULTS — MNIST (10 epochs)")
    print("="*70)
    print(f"  {'Algorithm':<35} {'Acc':>8} {'Time':>7} {'Grad?':>6}")
    print("-"*60)
    for k in sorted(results, key=lambda k: results[k]['acc'][-1], reverse=True):
        a = results[k]['acc'][-1]*100
        t = sum(results[k]['time'])
        g = 'YES' if k in ['Backprop','DirectLocal'] else 'ZERO'
        print(f"  {k:<35} {a:>7.2f}% {t:>6.0f}s {g:>6}")
