"""
Proper Hill Quasi-Fixed Point Analysis (corrected interpretation)

The Hill quasi-fixed point is NOT defined as "bracket = 0 at some scale".
It's defined as the IR attractor: if we start with very large y_t at high
scale and flow TOWARDS low energies, y_t converges to a specific value
that depends only on g_3 (mostly) and g_1, g_2 (a little).

This is the "infrared quasi-fixed point" because the IR flow is attracted
to this trajectory regardless of the initial UV value (as long as the UV
value is sufficiently large).

Procedure:
1. Start at M_Pl with a very large y_t (say y_t = 3.0)
2. Run DOWNWARDS to M_Z
3. See what y_t(M_Z) the flow converges to
4. Try different initial values to verify convergence
5. Extract the implied m_t and compare to ~220 GeV literature value
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

from sm_rge_1loop_validated import (
    M_Z, M_Pl, M_t, v_EW,
    g1_MZ, g2_MZ, g3_MZ, yt_MZ,
    beta_SM_1loop, B_SM
)

PREF = 1.0 / (16.0 * np.pi**2)


def run_gauge_UV_to_IR():
    """First, run gauge couplings UV->IR to have them at all scales.
    
    We need to know g_1, g_2, g_3 at M_Pl first. We run from M_Z upward
    using SM RGEs, then reverse.
    """
    y0 = np.array([g1_MZ, g2_MZ, g3_MZ, yt_MZ])
    sol = solve_ivp(lambda t, y: beta_SM_1loop(y[:3], y[3]),
                    (np.log(M_Z), np.log(M_Pl)), y0,
                    t_eval=np.linspace(np.log(M_Z), np.log(M_Pl), 2000),
                    method='DOP853', rtol=1e-11, atol=1e-14)
    return sol


# Get gauge couplings at M_Pl from forward SM run
sol_fwd = run_gauge_UV_to_IR()
g1_MPl = sol_fwd.y[0, -1]
g2_MPl = sol_fwd.y[1, -1]
g3_MPl = sol_fwd.y[2, -1]
yt_MPl_SM = sol_fwd.y[3, -1]

print(f"Gauge couplings at M_Pl (from SM forward run):")
print(f"  g_1(M_Pl) = {g1_MPl:.4f}")
print(f"  g_2(M_Pl) = {g2_MPl:.4f}")
print(f"  g_3(M_Pl) = {g3_MPl:.4f}")
print(f"  y_t(M_Pl) from SM = {yt_MPl_SM:.4f}")


# ============================================================
# Now: reverse flow. Start with various large y_t at M_Pl, 
# run DOWN to M_Z. See the IR attractor.
# ============================================================

def reverse_flow(yt_MPl_init):
    """Start at M_Pl with given y_t, gauge couplings from SM forward run.
    Run down to M_Z.
    """
    y0 = np.array([g1_MPl, g2_MPl, g3_MPl, yt_MPl_init])
    # Forward in t = log mu means: t goes from log M_Pl DOWN to log M_Z
    # solve_ivp handles decreasing t_span automatically
    t_span = (np.log(M_Pl), np.log(M_Z))
    t_eval = np.linspace(*t_span, 2000)
    
    # The RGE equations are the same, but now we integrate from high to low
    sol = solve_ivp(lambda t, y: beta_SM_1loop(y[:3], y[3]),
                    t_span, y0, t_eval=t_eval,
                    method='DOP853', rtol=1e-11, atol=1e-14)
    return sol


# Test several initial values
initial_yt_values = [0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0]

print(f"\n{'y_t(M_Pl) init':<18} {'y_t(M_Z) final':<18} {'m_t implied (GeV)':<20}")
print("-" * 60)

solutions = {}
for yt_init in initial_yt_values:
    sol = reverse_flow(yt_init)
    yt_final = sol.y[3, -1]
    m_t_implied = yt_final * v_EW / np.sqrt(2)
    print(f"{yt_init:<18.3f} {yt_final:<18.4f} {m_t_implied:<20.2f}")
    solutions[yt_init] = sol


# ============================================================
# Visualize the attractor behavior
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Left: y_t(mu) for different starting values - shows convergence
ax = axes[0]
for yt_init, sol in solutions.items():
    log_mu = sol.t / np.log(10)
    ax.plot(log_mu, sol.y[3], label=f'$y_t(M_{{Pl}}) = {yt_init}$', lw=1.5, alpha=0.8)

# Also plot the SM forward run
ax.plot(sol_fwd.t / np.log(10), sol_fwd.y[3], 'k-', lw=3, 
        label=f'SM measured: $y_t(M_Z)={yt_MZ:.3f}$')

ax.axhline(yt_MZ, color='red', ls=':', alpha=0.5, label=f'measured $y_t(M_Z)$')
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel(r'$y_t(\mu)$')
ax.set_title('Infrared attractor: all trajectories converge at low $\mu$')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Right: y_t / g_3 ratio - the PR attractor
ax = axes[1]
for yt_init, sol in solutions.items():
    log_mu = sol.t / np.log(10)
    ratio = sol.y[3] / sol.y[2]  # y_t / g_3
    ax.plot(log_mu, ratio, label=f'$y_t(M_{{Pl}}) = {yt_init}$', lw=1.5, alpha=0.8)

ax.plot(sol_fwd.t / np.log(10), sol_fwd.y[3] / sol_fwd.y[2], 'k-', lw=3,
        label='SM measured')
ax.axhline(np.sqrt(2/9), color='red', ls='--', alpha=0.5,
           label=r'PR target $\sqrt{2/9}$ = 0.471')
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel(r'$y_t(\mu) / g_3(\mu)$')
ax.set_title('Pendleton-Ross attractor visualization')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('fig_hill_attractor.png', dpi=120, bbox_inches='tight')
plt.close()

print("\nFigure saved: fig_hill_attractor.png")


# ============================================================
# Extract the quasi-fixed-point value precisely
# ============================================================

# For starting values >= 2.0, trajectories should converge at IR
# Take average of yt(M_Z) for yt_init >= 2.0
asymptotic_yt_MZ = np.mean([solutions[yt_init].y[3, -1] 
                             for yt_init in initial_yt_values 
                             if yt_init >= 2.0])
asymptotic_m_t = asymptotic_yt_MZ * v_EW / np.sqrt(2)

print(f"\n" + "=" * 70)
print("QUASI-FIXED-POINT EXTRACTION")
print("=" * 70)
print(f"  Asymptotic y_t(M_Z) from large initial values: {asymptotic_yt_MZ:.4f}")
print(f"  Implied m_t (Hill quasi-FP):                    {asymptotic_m_t:.1f} GeV")
print(f"  Literature value (1-loop SM):                   ~220 GeV")
print(f"  Measured m_t:                                   {M_t:.1f} GeV")
print()
print(f"  Ratio measured/quasi-FP: {M_t/asymptotic_m_t:.3f}")
print()

# The crucial question for LVS Direction 2:
print("=" * 70)
print("LVS INTERPRETATION (Direction 2)")
print("=" * 70)
print("""
The IR quasi-fixed point is NOT where the measured y_t sits — the measured
y_t is ~78% of the quasi-FP value. This has been known since 1981.

LVS candidate interpretation: does the measured y_t satisfy a DIFFERENT
stationarity condition, or occupy a specific position on the attractor flow?

Testing: compute d(yt/g3)/d(log mu) — if this ratio is stationary at M_Z,
that IS a joint stationarity condition.
""")

# Compute d(yt/g3)/dt along the SM flow
log_mu_fwd = sol_fwd.t
yt_fwd = sol_fwd.y[3]
g3_fwd = sol_fwd.y[2]
ratio_fwd = yt_fwd / g3_fwd

# Numerical derivative
d_ratio_dt = np.gradient(ratio_fwd, log_mu_fwd)

idx_MZ = 0
idx_Mt = np.argmin(np.abs(np.exp(log_mu_fwd) - M_t))
idx_MPl = -1

print(f"d(y_t/g_3)/d(log μ) at various scales:")
print(f"  at M_Z (mu={M_Z} GeV):     {d_ratio_dt[idx_MZ]:+.5e}")
print(f"  at M_t (mu={M_t} GeV):     {d_ratio_dt[idx_Mt]:+.5e}")
print(f"  at M_Pl (mu={M_Pl:.2e} GeV): {d_ratio_dt[idx_MPl]:+.5e}")
print()

# Find scale where derivative is closest to zero
idx_min_deriv = np.argmin(np.abs(d_ratio_dt))
mu_stationary = np.exp(log_mu_fwd[idx_min_deriv])
print(f"Scale where d(y_t/g_3)/dt is minimum: μ = {mu_stationary:.3e} GeV = 10^{np.log10(mu_stationary):.2f}")
print(f"Ratio (y_t/g_3) at that scale: {ratio_fwd[idx_min_deriv]:.4f}")
print(f"Derivative value: {d_ratio_dt[idx_min_deriv]:.5e}")
