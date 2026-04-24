"""
LVS Metric Robustness Test

Question (Fabien): does the "optimal" BSM scenario depend on the metric
we use to measure "stationarity"?

We test THREE metrics:

  σ_1(μ) = Σ_i (dg_i/dlog μ)^2                    [absolute beta, squared]
  σ_2(μ) = Σ_i (β_i / g_i)^2  = Σ_i (dlog g_i/dlog μ)^2   [relative / dimensionless]
  σ_3(μ) = Σ_i |β_i / g_i|^(1/2)                  [sub-linear alternative]

If optima differ drastically between metrics → our "result" is not physical,
it's a choice of measure.
If optima agree → there's genuine structure in the RG flow.

This is a proper robustness test.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import json

from sm_rge_1loop_validated import (
    M_Z, M_Pl,
    g1_MZ, g2_MZ, g3_MZ, yt_MZ,
    beta_SM_1loop, B_SM
)

PREF = 1.0 / (16.0 * np.pi**2)


def run_partial_LVS_final(alpha, log_mu_threshold):
    """Run and return couplings + betas at M_Pl."""
    y0 = np.array([g1_MZ, g2_MZ, g3_MZ, yt_MZ], dtype=float)
    
    # Case 1: threshold >= M_Pl → pure SM
    if log_mu_threshold >= np.log(M_Pl):
        t_span = (np.log(M_Z), np.log(M_Pl))
        sol = solve_ivp(lambda t, y: beta_SM_1loop(y[:3], y[3]),
                       t_span, y0, 
                       method='DOP853', rtol=1e-10, atol=1e-13, dense_output=False)
        y_final = np.asarray(sol.y)[:, -1]
        B_eff_final = B_SM
    
    # Case 2: threshold <= M_Z → pure BSM
    elif log_mu_threshold <= np.log(M_Z):
        B_eff = (1.0 - alpha) * B_SM
        def rhs(t, y):
            g = y[:3]
            yt = y[3]
            dg = B_eff * g**3 * PREF
            dyt = yt * PREF * ((9.0/2.0) * yt**2 - (17.0/20.0) * g[0]**2
                              - (9.0/4.0) * g[1]**2 - 8.0 * g[2]**2)
            return np.concatenate([dg, [dyt]])
        t_span = (np.log(M_Z), np.log(M_Pl))
        sol = solve_ivp(rhs, t_span, y0, 
                       method='DOP853', rtol=1e-10, atol=1e-13, dense_output=False)
        y_final = np.asarray(sol.y)[:, -1]
        B_eff_final = B_eff
    
    # Case 3: two-phase
    else:
        t_span_1 = (np.log(M_Z), log_mu_threshold)
        sol_1 = solve_ivp(lambda t, y: beta_SM_1loop(y[:3], y[3]),
                         t_span_1, y0,
                         method='DOP853', rtol=1e-10, atol=1e-13, dense_output=False)
        y_thr = np.asarray(sol_1.y)[:, -1]
        
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
                         method='DOP853', rtol=1e-10, atol=1e-13, dense_output=False)
        y_final = np.asarray(sol_2.y)[:, -1]
        B_eff_final = B_eff
    
    # Compute betas at final point with effective coefficients
    g_f = y_final[:3]
    yt_f = y_final[3]
    dg = B_eff_final * g_f**3 * PREF
    dyt = yt_f * PREF * ((9.0/2.0) * yt_f**2 - (17.0/20.0) * g_f[0]**2
                        - (9.0/4.0) * g_f[1]**2 - 8.0 * g_f[2]**2)
    betas = np.concatenate([dg, [dyt]])
    
    return y_final, betas


def metric_absolute_squared(y, betas):
    """σ_1 = Σ (β_i)^2  — absolute beta values squared"""
    # Include all 4 couplings
    return np.sum(betas**2)


def metric_relative_squared(y, betas):
    """σ_2 = Σ (β_i / c_i)^2  — dimensionless logarithmic rate"""
    # c = [g1, g2, g3, yt]
    rates = betas / y
    return np.sum(rates**2)


def metric_sqrt_relative(y, betas):
    """σ_3 = Σ |β_i / c_i|^(1/2)  — sub-linear test"""
    rates = np.abs(betas / y)
    return np.sum(np.sqrt(rates))


def unification_gap(y):
    """Δ = √Σ (α_i⁻¹ - α_j⁻¹)²"""
    g = y[:3]
    alpha = g**2 / (4*np.pi)
    inv = 1.0 / alpha
    return np.sqrt((inv[0]-inv[1])**2 + (inv[0]-inv[2])**2 + (inv[1]-inv[2])**2)


# ============================================================
# 2D scan with three metrics
# ============================================================

alpha_range = np.linspace(0.0, 1.5, 31)
log_mu_range = np.linspace(3, 18, 31)

sigma1_grid = np.zeros((alpha_range.size, log_mu_range.size))
sigma2_grid = np.zeros_like(sigma1_grid)
sigma3_grid = np.zeros_like(sigma1_grid)
delta_grid = np.zeros_like(sigma1_grid)

print(f"2D scan: {alpha_range.size} × {log_mu_range.size} = {alpha_range.size*log_mu_range.size} points")

for i, a in enumerate(alpha_range):
    for j, lm in enumerate(log_mu_range):
        y, b = run_partial_LVS_final(a, lm * np.log(10))
        sigma1_grid[i, j] = metric_absolute_squared(y, b)
        sigma2_grid[i, j] = metric_relative_squared(y, b)
        sigma3_grid[i, j] = metric_sqrt_relative(y, b)
        delta_grid[i, j] = unification_gap(y)

print("Scan done.")

# ============================================================
# Find optima for each metric
# ============================================================

def report_min(grid, name):
    idx = np.unravel_index(np.argmin(grid), grid.shape)
    a_opt = alpha_range[idx[0]]
    lm_opt = log_mu_range[idx[1]]
    val = grid[idx]
    return {'name': name, 'alpha_opt': float(a_opt), 
            'log_mu_opt': float(lm_opt), 'value': float(val),
            'idx': idx}


r1 = report_min(sigma1_grid, 'σ₁ = Σ β²')
r2 = report_min(sigma2_grid, 'σ₂ = Σ (β/g)²')
r3 = report_min(sigma3_grid, 'σ₃ = Σ √|β/g|')
rD = report_min(delta_grid, 'Δ (unification gap)')

print("\n" + "=" * 70)
print("METRIC ROBUSTNESS TEST — RESULTS")
print("=" * 70)
print(f"{'Metric':<25} {'α_opt':<10} {'log₁₀Λ_opt':<15} {'value':<15}")
print("-" * 70)
for r in [r1, r2, r3, rD]:
    print(f"{r['name']:<25} {r['alpha_opt']:<10.3f} {r['log_mu_opt']:<15.2f} {r['value']:<15.5e}")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)

# Check if optima agree
alphas_opt = [r1['alpha_opt'], r2['alpha_opt'], r3['alpha_opt']]
log_mus_opt = [r1['log_mu_opt'], r2['log_mu_opt'], r3['log_mu_opt']]

print(f"\nα optima across stationarity metrics: {alphas_opt}")
print(f"log₁₀(Λ_BSM) optima across stationarity metrics: {log_mus_opt}")

if (max(alphas_opt) - min(alphas_opt)) < 0.3 and (max(log_mus_opt) - min(log_mus_opt)) < 2:
    print("\n→ OPTIMA ARE CONSISTENT across metrics: genuine structural effect")
else:
    print("\n→ OPTIMA DIFFER SIGNIFICANTLY: result depends on metric choice → ARTIFACT")
    print("  The apparent 'LVS-favorable' region is not a physical feature")
    print("  of the RG flow; it's a feature of the measure we chose.")


# ============================================================
# Save and visualize
# ============================================================

# Save results
results = {
    'sigma1_absolute': {'alpha_opt': r1['alpha_opt'], 'log_mu_opt': r1['log_mu_opt'], 'min_value': r1['value']},
    'sigma2_relative': {'alpha_opt': r2['alpha_opt'], 'log_mu_opt': r2['log_mu_opt'], 'min_value': r2['value']},
    'sigma3_sqrt': {'alpha_opt': r3['alpha_opt'], 'log_mu_opt': r3['log_mu_opt'], 'min_value': r3['value']},
    'delta': {'alpha_opt': rD['alpha_opt'], 'log_mu_opt': rD['log_mu_opt'], 'min_value': rD['value']}
}

with open('metric_comparison.json', 'w') as f:
    json.dump(results, f, indent=2)

np.savez('metric_grids.npz',
         alpha_range=alpha_range, log_mu_range=log_mu_range,
         sigma1_grid=sigma1_grid, sigma2_grid=sigma2_grid,
         sigma3_grid=sigma3_grid, delta_grid=delta_grid)

# Visualization: 4 panels
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

titles = [
    r'$\sigma_1 = \sum_i \beta_i^2$ (absolu, métrique dimensionnée)',
    r'$\sigma_2 = \sum_i (\beta_i/g_i)^2$ (relatif, sans dimension)',
    r'$\sigma_3 = \sum_i \sqrt{|\beta_i/g_i|}$ (sous-linéaire)',
    r'$\Delta$ (écart d\'unification)'
]
grids = [sigma1_grid, sigma2_grid, sigma3_grid, delta_grid]
optima = [r1, r2, r3, rD]

for k, (title, grid, r) in enumerate(zip(titles, grids, optima)):
    ax = axes[k // 2, k % 2]
    # Use log scale with tiny offset for readability
    log_grid = np.log10(grid + 1e-30)
    im = ax.contourf(log_mu_range, alpha_range, log_grid, levels=25, cmap='viridis')
    ax.set_xlabel(r'$\log_{10}(\Lambda_{BSM}/\mathrm{GeV})$', fontsize=11)
    ax.set_ylabel(r'$\alpha$ (fraction d\'annulation $b_{SM}$)', fontsize=11)
    ax.set_title(title, fontsize=11)
    plt.colorbar(im, ax=ax, label=r'$\log_{10}$ valeur')
    
    # Mark optimum
    ax.plot(r['log_mu_opt'], r['alpha_opt'], 'w*', 
            markersize=18, markeredgecolor='red', markeredgewidth=2.5,
            label=f"min: α={r['alpha_opt']:.2f}, log₁₀Λ={r['log_mu_opt']:.1f}")
    ax.legend(fontsize=9, loc='lower right')

plt.suptitle('Test de robustesse LVS — sensibilité au choix de métrique',
             fontsize=14, y=1.00)
plt.tight_layout()
plt.savefig('fig6_metric_robustness.png', dpi=120, bbox_inches='tight')
plt.close()
print("\nFigure 6 (metric robustness) saved")
