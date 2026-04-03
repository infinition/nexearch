"""Quick run: only NoProp + MonoForward (SCFF eliminated)."""
import sys
sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, '.')
from benchmark_round6_breakthrough import *

if __name__ == '__main__':
    train_loader, test_loader = get_mnist(256)
    N = 15
    flatten = lambda x: x.view(x.size(0), -1)
    dims = [784, 500, 300, 10]

    results = {}

    results['MonoForward'] = train_and_eval(
        'Mono-Forward (Auckland 2025)',
        MonoForwardNet(dims, n_classes=10, lr=0.01),
        train_loader, test_loader, N, flatten
    )

    dims_wide = [784, 1000, 500, 200, 10]
    results['MonoForward-W'] = train_and_eval(
        'Mono-Forward Wide',
        MonoForwardNet(dims_wide, n_classes=10, lr=0.005),
        train_loader, test_loader, N, flatten
    )

    print("\n" + "="*60)
    print("  RESULTS (add to Round 6)")
    print("="*60)
    print("  (From earlier: Backprop=98.22%, DirectLocal=97.98%, NoProp=97.89%)")
    for k in results:
        a = results[k]['acc'][-1]*100
        t = sum(results[k]['time'])
        print(f"  {k:<30} {a:>7.2f}% {t:>6.0f}s")
