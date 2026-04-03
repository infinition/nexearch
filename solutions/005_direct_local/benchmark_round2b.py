"""Round 2b: Run only HESP and DirectLocal (others already tested)."""
import sys
sys.path.insert(0, '.')
from benchmark_round2 import *

if __name__ == '__main__':
    train_loader, test_loader = get_mnist(256)
    dims = [784, 500, 300, 10]
    N = 10

    results = {}
    results['HESP'] = train_and_eval('HESP (Hybrid Eq-Signal Prop)', HESPNet(dims, beta=0.5, n_relax=10, relax_lr=0.3, lr=0.02, eq_weight=0.3), train_loader, test_loader, N)
    results['DirectLocal'] = train_and_eval('Direct Local Probes', DirectLocalNet(dims, lr=0.001), train_loader, test_loader, N)

    print("\n" + "="*60)
    print("  ROUND 2b RESULTS")
    print("="*60)
    # Include round 1 results for context
    print("  (From Round 2a: Backprop=98.23%, EqProp-Mom=87.49%)")
    print("-"*55)
    for k in results:
        a = results[k]['acc'][-1] * 100
        t = sum(results[k]['time'])
        print(f"  {k:<30} {a:>9.2f}% {t:>9.1f}s")
