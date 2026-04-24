"""
DEEP DIVE: The 10^12 GeV stationarity of y_t/g_3

We found that in the measured SM, d(y_t/g_3)/d(log μ) = 0 at μ ≈ 9×10^11 GeV.
This deserves serious investigation:

1. Is it robust to initial condition uncertainties?
2. What's the ratio value there?  
3. Does it match any known scale (Higgs stability? MSSM unification?)
4. Is there a deeper relation involving all couplings?

We'll also test ratios like:
  - y_t / sqrt(g_1^2 + g_2^2 + g_3^2)
  - y_t^2 / (sum g_i^2)
  - y_t^2 / (α_1 + α_2 + α_3)
  
to see if ANY of these is stationary at a physically meaningful scale.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import json

from sm_rge_1loop_validated import (
    M_Z, M_Pl, M_t, v_EW,
    g1_MZ, g2_MZ, g3_MZ, yt_MZ,
    beta_SM_1loop
)


def run_SM_high_res():
    """Run the SM with very high resolution for derivative computation."""
    y0 = np.array([g1_MZ, g2_MZ, g3_MZ, yt_MZ])
    t_span = (np.log(M_Z), np.log(M_Pl))
    t_eval = np.linspace(*t_span, 20000)  # very fine
    sol = solve_ivp(lambda t, y: beta_SM_1loop(y[:3], y[3]),
                    t_span, y0, t_eval=t_eval,
                    method='DOP853', rtol=1e-12, atol=1e-15)
    return sol


sol = run_SM_high_res()
log_mu = sol.t
mu_arr = np.exp(log_mu)
g1, g2, g3, yt = sol.y[0], sol.y[1], sol.y[2], sol.y[3]


# ============================================================
# Test various ratios for stationarity
# ============================================================

# We test ratios of the form y_t^n / f(g_1, g_2, g_3)^m

ratios_to_test = {
    'y_t / g_3': yt / g3,
    'y_t^2 / g_3^2': yt**2 / g3**2,
    'y_t / sqrt(g_1^2+g_2^2+g_3^2)': yt / np.sqrt(g1**2 + g2**2 + g3**2),
    'y_t^2 / (g_1^2+g_2^2+g_3^2)': yt**2 / (g1**2 + g2**2 + g3**2),
    'y_t / (g_1 g_2 g_3)^(1/3)': yt / (g1 * g2 * g3)**(1/3),
    'y_t^2 / (5/3 g_1^2 + 3 g_2^2 + 8 g_3^2)': yt**2 / ((5/3)*g1**2 + 3*g2**2 + 8*g3**2),
    'y_t^2 / (17/20 g_1^2 + 9/4 g_2^2 + 8 g_3^2)': yt**2 / ((17/20)*g1**2 + (9/4)*g2**2 + 8*g3**2),
}

print("=" * 75)
print("STATIONARITY TEST: multiple ratios scanned for plateau")
print("=" * 75)

# For each ratio, find the scale where d(ratio)/d(log mu) is closest to zero
# AND the relative stationarity there: |(d ratio)/(ratio)|

results = {}

for name, ratio in ratios_to_test.items():
    d_ratio = np.gradient(ratio, log_mu)
    rel_d = np.abs(d_ratio / ratio)
    idx_min = np.argmin(rel_d)
    mu_stat = mu_arr[idx_min]
    
    # Also: the value of the ratio there
    val_at_stat = ratio[idx_min]
    # And the value at M_Z and M_Pl
    val_at_MZ = ratio[0]
    val_at_MPl = ratio[-1]
    
    results[name] = {
        'mu_stationary': float(mu_stat),
        'log10_mu': float(np.log10(mu_stat)),
        'ratio_at_stat': float(val_at_stat),
        'ratio_at_MZ': float(val_at_MZ),
        'ratio_at_MPl': float(val_at_MPl),
        'variation_MZ_to_MPl_pct': float(100 * (val_at_MPl - val_at_MZ) / val_at_MZ),
        'min_rel_derivative': float(rel_d[idx_min]),
    }
    
    print(f"\n  {name}")
    print(f"    μ_stationary       = {mu_stat:.3e} GeV  (log10 = {np.log10(mu_stat):.2f})")
    print(f"    ratio(M_Z)          = {val_at_MZ:.4f}")
    print(f"    ratio(μ_stat)       = {val_at_stat:.4f}")
    print(f"    ratio(M_Pl)         = {val_at_MPl:.4f}")
    print(f"    variation M_Z→M_Pl = {100*(val_at_MPl-val_at_MZ)/val_at_MZ:+.1f}%")
    print(f"    |1/r · dr/dt|_min   = {rel_d[idx_min]:.5e}")


# ============================================================
# Visualize the most stable ratios
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Panel 1: the most stable ratio
best_names = sorted(results.keys(), key=lambda n: results[n]['min_rel_derivative'])

for k, name in enumerate(best_names[:4]):
    ax = axes[k // 2, k % 2]
    ratio = ratios_to_test[name]
    ax.plot(log_mu/np.log(10), ratio, 'k-', lw=2)
    mu_stat = results[name]['mu_stationary']
    val_stat = results[name]['ratio_at_stat']
    ax.axvline(np.log10(mu_stat), color='red', ls='--', alpha=0.7,
               label=f'μ_stat = 10^{np.log10(mu_stat):.2f} GeV')
    ax.axhline(val_stat, color='blue', ls=':', alpha=0.5,
               label=f'value = {val_stat:.3f}')
    ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
    ax.set_ylabel('Ratio')
    ax.set_title(name, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

plt.suptitle('Most stable ratios across the SM RG flow', fontsize=14)
plt.tight_layout()
plt.savefig('fig_ratios_stationarity.png', dpi=120, bbox_inches='tight')
plt.close()


# ============================================================
# The really interesting test: are the stationarity scales 
# clustered at a physical value?
# ============================================================

mu_stats = [results[name]['log10_mu'] for name in results]
print("\n" + "=" * 75)
print("CLUSTERING OF STATIONARITY SCALES")
print("=" * 75)
print(f"All stationarity scales (log₁₀ GeV): {sorted(mu_stats)}")
print(f"Mean: {np.mean(mu_stats):.2f}, Std: {np.std(mu_stats):.2f}")
print(f"Range: {min(mu_stats):.2f} to {max(mu_stats):.2f}")

# Key physics scales for comparison:
print("\nPhysics scales for comparison:")
print(f"  M_Z        : log₁₀ = {np.log10(91.2):.2f}")
print(f"  M_t        : log₁₀ = {np.log10(172.76):.2f}")
print(f"  SM vacuum metastability (Buttazzo): log₁₀ ≈ 10-11")
print(f"  Seesaw neutrino Majorana: log₁₀ ≈ 10-14")
print(f"  MSSM GUT    : log₁₀ = 16.3")
print(f"  Planck      : log₁₀ = 19.1")


# Save
with open('stationarity_ratios.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nResults saved to stationarity_ratios.json")
