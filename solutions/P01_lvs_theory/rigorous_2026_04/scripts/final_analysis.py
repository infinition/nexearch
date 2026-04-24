"""
Fine analysis: does dλ/d(log μ) reach a minimum (inflection point of λ)
near the y_t/g_3 stationarity scale?

If YES — there's a genuine structural link between the Higgs sector's
running and the Yukawa-gauge balance.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

from final_corrected import beta_SM_halved, g1_MZ, g2_MZ, g3_MZ, yt_MZ, lambda_MZ
from final_corrected import M_Z, M_Pl

y0 = np.array([g1_MZ, g2_MZ, g3_MZ, yt_MZ, lambda_MZ])
t_span = (np.log(M_Z), np.log(M_Pl))
sol = solve_ivp(beta_SM_halved, t_span, y0,
                t_eval=np.linspace(*t_span, 30000),
                method='DOP853', rtol=1e-13, atol=1e-16)

log_mu = sol.t
mu_arr = np.exp(log_mu)
g1, g2, g3, yt, lam = sol.y

# Compute dλ/d(log μ) along the trajectory
PREF = 1.0 / (16.0 * np.pi**2)
dlam_dt = []
for i in range(len(log_mu)):
    _, _, _, _, dl = beta_SM_halved(log_mu[i], [g1[i], g2[i], g3[i], yt[i], lam[i]])
    dlam_dt.append(dl)
dlam_dt = np.array(dlam_dt)

# And the y_t/g_3 ratio
ratio_yt_g3 = yt / g3
d_ratio_dt = np.gradient(ratio_yt_g3, log_mu)

# Key scales
idx_dlam_min = np.argmin(np.abs(dlam_dt))  # where dλ/dt closest to 0
mu_dlam_min = mu_arr[idx_dlam_min]

idx_ratio_stat = np.argmin(np.abs(d_ratio_dt))  # where d(y_t/g_3)/dt = 0
mu_ratio_stat = mu_arr[idx_ratio_stat]

# Where is dλ/dt most negative (fastest descent of λ)?
idx_dlam_most_neg = np.argmin(dlam_dt)
mu_dlam_most_neg = mu_arr[idx_dlam_most_neg]

# Where is λ minimum?
idx_lam_min = np.argmin(lam)
mu_lam_min = mu_arr[idx_lam_min]

print("=" * 70)
print("KEY SCALES IN THE HIGGS-YUKAWA COUPLING FLOW")
print("=" * 70)
print()
print(f"1. y_t/g_3 stationarity (d(y_t/g_3)/dt = 0):")
print(f"     μ = {mu_ratio_stat:.3e} GeV = 10^{np.log10(mu_ratio_stat):.2f}")
print()
print(f"2. λ minimum (dλ/dt = 0, closest to zero):")
print(f"     μ = {mu_dlam_min:.3e} GeV = 10^{np.log10(mu_dlam_min):.2f}")
print()
print(f"3. λ steepest descent (min of dλ/dt):")
print(f"     μ = {mu_dlam_most_neg:.3e} GeV = 10^{np.log10(mu_dlam_most_neg):.2f}")
print()
print(f"4. λ absolute minimum:")
print(f"     μ = {mu_lam_min:.3e} GeV = 10^{np.log10(mu_lam_min):.2f}")
print(f"     λ(min) = {lam[idx_lam_min]:.4f}")
print()
print("=" * 70)
print("RELATIVE POSITIONS")  
print("=" * 70)

log10_diff_12 = np.log10(mu_dlam_min) - np.log10(mu_ratio_stat)
print(f"\nLog₁₀ distance  λ-stationarity ↔ y_t/g_3-stationarity: {log10_diff_12:+.2f}")
print(f"(positive = λ-stationary scale is HIGHER)")

if abs(log10_diff_12) < 1.0:
    print("  → The two stationarity scales are WITHIN factor 10.")
    print("  → This is a striking proximity worth investigating.")
elif abs(log10_diff_12) < 2.0:
    print("  → Within factor 100, suggestive but not conclusive.")
else:
    print("  → Separated, no coincidence.")


# ============================================================
# KEY PLOT: put all key quantities together
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# λ(μ)
ax = axes[0, 0]
ax.plot(log_mu/np.log(10), lam, 'm-', lw=2.5, label=r'$\lambda(\mu)$')
ax.axhline(0, color='red', ls='--', alpha=0.5, label='λ=0')
ax.axvline(np.log10(mu_ratio_stat), color='green', ls=':', alpha=0.8,
           label=f'$y_t/g_3$ stat at 10^{np.log10(mu_ratio_stat):.2f}')
ax.axvline(np.log10(mu_dlam_min), color='orange', ls=':', alpha=0.8,
           label=f'$d\\lambda/dt\\to 0$ at 10^{np.log10(mu_dlam_min):.2f}')
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel(r'$\lambda(\mu)$')
ax.set_title(r'Higgs quartic running')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# dλ/dt
ax = axes[0, 1]
ax.plot(log_mu/np.log(10), dlam_dt, 'm-', lw=2, label=r'$d\lambda/d(\log\mu)$')
ax.axhline(0, color='red', ls='--', alpha=0.5)
ax.axvline(np.log10(mu_ratio_stat), color='green', ls=':', alpha=0.8,
           label=f'$y_t/g_3$ stat')
ax.axvline(np.log10(mu_dlam_min), color='orange', ls=':', alpha=0.8,
           label=f'$d\\lambda/dt\\to 0$')
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel(r'$d\lambda/d(\log\mu)$')
ax.set_title(r'Derivative of Higgs quartic: where does it vanish?')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# y_t/g_3
ax = axes[1, 0]
ax.plot(log_mu/np.log(10), ratio_yt_g3, 'b-', lw=2, label=r'$y_t/g_3$')
ax.axvline(np.log10(mu_ratio_stat), color='green', ls=':', alpha=0.8)
ax.axvline(np.log10(mu_dlam_min), color='orange', ls=':', alpha=0.8)
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel(r'$y_t/g_3$')
ax.set_title('Yukawa-QCD ratio')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Both dλ/dt and d(y_t/g_3)/dt on same axis
ax = axes[1, 1]
# Normalize both to same scale for comparison
dlam_normalized = dlam_dt / np.max(np.abs(dlam_dt))
dratio_normalized = d_ratio_dt / np.max(np.abs(d_ratio_dt))
ax.plot(log_mu/np.log(10), dlam_normalized, 'm-', lw=2,
        label=r'$d\lambda/dt$ (normalized)')
ax.plot(log_mu/np.log(10), dratio_normalized, 'b-', lw=2,
        label=r'$d(y_t/g_3)/dt$ (normalized)')
ax.axhline(0, color='red', ls='--', alpha=0.5)
ax.axvline(np.log10(mu_ratio_stat), color='green', ls=':', alpha=0.8,
           label=f'$y_t/g_3$ stat: 10^{np.log10(mu_ratio_stat):.2f}')
ax.axvline(np.log10(mu_dlam_min), color='orange', ls=':', alpha=0.8,
           label=f'$\\lambda$ stat: 10^{np.log10(mu_dlam_min):.2f}')
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel('Normalized rate')
ax.set_title('Do the two stationarity scales coincide?')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('fig_higgs_yukawa_final.png', dpi=120, bbox_inches='tight')
plt.close()
print("\nFigure saved: fig_higgs_yukawa_final.png")
