"""Fast sequential runner with 120s timeout per script."""
import subprocess, sys, re, time
from pathlib import Path

SDIR = Path(__file__).parent
PY = sys.executable

scripts = sorted(SDIR.glob("[0-9][0-9]_*.py"))
results = {}

for s in scripts:
    num = s.name[:2]
    print(f"\n[{num}] {s.name}...", flush=True)
    try:
        r = subprocess.run([PY, str(s)], capture_output=True, text=True,
                          timeout=120, cwd=str(SDIR))
        out = r.stdout + r.stderr
        m = re.search(r'MNIST Accuracy:\s*([\d.]+)%', out)
        t = re.search(r'Time:\s*([\d.]+)s', out)
        if m:
            acc = float(m.group(1))
            tm = float(t.group(1)) if t else 0
            results[num] = (acc, tm)
            print(f"  -> {acc:.1f}% ({tm:.1f}s)", flush=True)
        else:
            # Check for error
            errs = [l for l in out.split('\n') if 'Error' in l]
            if errs:
                print(f"  -> ERROR: {errs[-1][:80]}", flush=True)
            else:
                print(f"  -> No result (running too slow?)", flush=True)
            results[num] = (None, 120)
    except subprocess.TimeoutExpired:
        print(f"  -> TIMEOUT", flush=True)
        results[num] = (None, 120)

print(f"\n{'='*60}")
print(f"{'#':<4} {'Accuracy':<12} {'Time':<10}")
print(f"{'-'*30}")
for n in sorted(results):
    a, t = results[n]
    print(f"{n:<4} {f'{a:.1f}%' if a else 'FAIL':<12} {t:.0f}s")
print(f"{'='*60}")
