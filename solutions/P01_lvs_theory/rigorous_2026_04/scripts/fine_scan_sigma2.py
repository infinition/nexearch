"""
Finer resolution around the σ₂ optimum to see if α < 1 is real.

The σ₂ metric (relative rates) showed optimum at α=0.95 rather than 1.0.
Is this numerical noise or a genuine sub-unit preference?

We zoom in with finer α resolution.
"""

import numpy as np
from scipy.integrate import solve_ivp

from sm_rge_1loop_validated import (
    M_Z, M_Pl,
    g1_MZ, g2_MZ, g3_MZ, yt_MZ,
    beta_SM_1loop, B_SM
)

PREF = 1.0 / (16.0 * np.pi**2)


def run_and_return_final(alpha, log_mu_threshold):
    y0 = np.array([g1_MZ, g2_MZ, g3_MZ, yt_MZ], dtype=float)
    
    # Phase 1: SM
    t_span_1 = (np.log(M_Z), log_mu_threshold)
    sol_1 = solve_ivp(lambda t, y: beta_SM_1loop(y[:3], y[3]),
                     t_span_1, y0,
                     method='DOP853', rtol=1e-12, atol=1e-15)
    y_thr = np.asarray(sol_1.y)[:, -1]
    
    # Phase 2: BSM
    B_eff = (1.0 - alpha) * B_SM
    def rhs(t, y):
        g = y[:3]
        yt = y[3]
        dg = B_eff * g**3 * PREF
        dyt = yt * PREF * ((9.0/2.0) * yt**2 - (17.0/20.0) * g[0]**2
                          - (9.0/4.0) * g[1]**2 - 8.0 * g[2]**2)
        return np.concatenate([dg, [dyt]])
    
    t_span_2 = (log_mu_threshold, np.log(M_Pl))
    sol_2 = solve_ivp(rhs, t_span_2, y_thr,
                     method='DOP853', rtol=1e-12, atol=1e-15)
    y_final = np.asarray(sol_2.y)[:, -1]
    
    # Betas at final point
    g_f = y_final[:3]
    yt_f = y_final[3]
    dg = B_eff * g_f**3 * PREF
    dyt = yt_f * PREF * ((9.0/2.0) * yt_f**2 - (17.0/20.0) * g_f[0]**2
                        - (9.0/4.0) * g_f[1]**2 - 8.0 * g_f[2]**2)
    betas = np.concatenate([dg, [dyt]])
    
    return y_final, betas


# Fine scan at log_mu = 18 (the reported optimum region)
log_mu = 18.0 * np.log(10)  # fixed at 10^18 GeV
alpha_fine = np.linspace(0.85, 1.05, 41)

sigma2_vals = []
contrib_gauge = []
contrib_yukawa = []

for a in alpha_fine:
    y, b = run_and_return_final(a, log_mu)
    rates = b / y
    sigma2 = np.sum(rates**2)
    sigma2_vals.append(sigma2)
    # Split contribution
    contrib_gauge.append(np.sum(rates[:3]**2))
    contrib_yukawa.append(rates[3]**2)

sigma2_vals = np.array(sigma2_vals)
contrib_gauge = np.array(contrib_gauge)
contrib_yukawa = np.array(contrib_yukawa)

idx_min = np.argmin(sigma2_vals)
print(f"Fine scan at Λ_BSM = 10^18 GeV:")
print(f"  α range: [{alpha_fine[0]:.3f}, {alpha_fine[-1]:.3f}], step = {alpha_fine[1]-alpha_fine[0]:.4f}")
print(f"  Minimum σ₂ at α = {alpha_fine[idx_min]:.4f}")
print(f"  σ₂ at minimum = {sigma2_vals[idx_min]:.5e}")
print(f"  σ₂ at α=1.00  = {sigma2_vals[np.argmin(np.abs(alpha_fine-1.0))]:.5e}")
print(f"  Gauge contribution at minimum: {contrib_gauge[idx_min]:.5e}")
print(f"  Yukawa contribution at minimum: {contrib_yukawa[idx_min]:.5e}")
print()

# At α=1, gauge betas are exactly zero by construction. Only Yukawa remains.
# At α<1, gauge betas are nonzero but Yukawa can be partially compensated.

print("PHYSICAL INTERPRETATION:")
print(f"  At α = 1.00: B_eff = 0, so gauge β_i = 0 EXACTLY.")
print(f"  Only Yukawa β_yt remains, driven by residual g_i^2.")
print(f"  At α < 1: gauge β_i nonzero, but Yukawa might balance them in total σ₂.")
print()

# Save for inclusion in notebook
import json
result = {
    'alpha_range': alpha_fine.tolist(),
    'sigma2_values': sigma2_vals.tolist(),
    'gauge_contribution': contrib_gauge.tolist(),
    'yukawa_contribution': contrib_yukawa.tolist(),
    'optimum': {
        'alpha': float(alpha_fine[idx_min]),
        'sigma2': float(sigma2_vals[idx_min])
    }
}
with open('fine_scan_sigma2.json', 'w') as f:
    json.dump(result, f, indent=2)

# Plot
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(alpha_fine, sigma2_vals, 'k-', lw=2, label=r'$\sigma_2$ total')
ax.plot(alpha_fine, contrib_gauge, 'b--', lw=1.5, label='gauge contribution')
ax.plot(alpha_fine, contrib_yukawa, 'r--', lw=1.5, label='Yukawa contribution')
ax.axvline(alpha_fine[idx_min], color='green', ls=':', alpha=0.7, 
           label=f'minimum à α={alpha_fine[idx_min]:.3f}')
ax.axvline(1.0, color='orange', ls=':', alpha=0.7, label='α=1 (cancellation stricte)')
ax.set_xlabel(r'$\alpha$', fontsize=12)
ax.set_ylabel(r'$\sigma_2 = \sum_i (\beta_i/c_i)^2$', fontsize=12)
ax.set_title(r'Décomposition de $\sigma_2$ à $\Lambda_{BSM} = 10^{18}$ GeV', fontsize=12)
ax.set_yscale('log')
ax.legend(fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('fig7_sigma2_fine.png', dpi=120, bbox_inches='tight')
plt.close()
print("Figure 7 saved")
