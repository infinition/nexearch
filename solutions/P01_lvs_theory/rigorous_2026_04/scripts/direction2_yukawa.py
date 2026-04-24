"""
DIRECTION 2: Joint Yukawa-Gauge Stationarity Analysis

The question: does the measured top Yukawa satisfy a non-trivial 
stationarity condition involving the gauge couplings?

Classical result (Pendleton-Ross 1981, Hill 1981):
If y_t is large at high scales, it rapidly approaches a value where
its beta function vanishes. The 1-loop condition is:

    (9/2) y_t^2 = (17/20) g_1^2 + (9/4) g_2^2 + 8 g_3^2

In the pure SM, this Hill fixed point predicts m_t ~ 220-230 GeV.
Measured: m_t = 172.76 GeV. So the SM is at 172.76/220 ~ 78% of the Hill FP.

**LVS question:** is there a DIFFERENT stationarity condition, involving 
joint gauge+Yukawa structure, that the measured y_t DOES satisfy?

We'll test several candidate relations:

1. Hill FP ratio: r_Hill = y_t / y_t^FP
2. Pendleton-Ross attractor: y_t^2 ≈ (8/9) g_3^2 (from RG flow structure)
3. Top-bottom Yukawa difference (but we ignore y_b as small)
4. Higgs self-stabilization: does y_t^2 sit at a critical value for vacuum stability?
5. LVS-proposed: y_t^2 / (g_1^2 + g_2^2 + g_3^2) = constant across RG flow?
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

# Run SM to M_Pl
y0 = np.array([g1_MZ, g2_MZ, g3_MZ, yt_MZ])
t_span = (np.log(M_Z), np.log(M_Pl))
sol = solve_ivp(lambda t, y: beta_SM_1loop(y[:3], y[3]),
                t_span, y0, t_eval=np.linspace(*t_span, 2000),
                method='DOP853', rtol=1e-11, atol=1e-14)

log_mu = sol.t
mu_arr = np.exp(log_mu)
g1 = sol.y[0]
g2 = sol.y[1]
g3 = sol.y[2]
yt = sol.y[3]


# ============================================================
# Candidate stationarity relations — compute along the flow
# ============================================================

# 1. Hill FP: (9/2) y_t^2 = (17/20) g_1^2 + (9/4) g_2^2 + 8 g_3^2
#    Define R_Hill = LHS / RHS. At the fixed point, R_Hill = 1.
R_Hill = (4.5 * yt**2) / ((17/20) * g1**2 + (9/4) * g2**2 + 8 * g3**2)

# 2. Pendleton-Ross attractor y_t^2 / g_3^2 ratio
#    Pure 1-loop SM PR attractor value: y_t^2 / g_3^2 -> 2/9 at IR
#    (From Pendleton-Ross 1981, this is derived from neglecting g_1, g_2)
R_PR_g3 = yt**2 / g3**2
R_PR_target = 2.0 / 9.0  # attractor ratio

# 3. LVS candidate: joint Yukawa-gauge quadratic invariant
#    J = y_t^2 - (1/N) sum g_i^2 (could be constant along flow?)
J_LVS = yt**2 - (g1**2 + g2**2 + g3**2) / 3.0

# 4. Dimensionless "tilt" between Yukawa and dominant QCD coupling
#    Measures how much y_t deviates from being locked to g_3
tilt_y_g3 = yt / g3  # attractor at y_t/g_3 = sqrt(2/9) ~ 0.471

# 5. The full beta_yt / (y_t * PREF) — this is the bracket
#    bracket(mu) = (9/2) y_t^2 - (17/20) g_1^2 - (9/4) g_2^2 - 8 g_3^2
bracket = (4.5 * yt**2) - (17/20) * g1**2 - (9/4) * g2**2 - 8 * g3**2


# Print key values
print("=" * 70)
print("JOINT GAUGE-YUKAWA STATIONARITY ANALYSIS")
print("=" * 70)
print(f"\nAt M_Z (measured point):")
print(f"  y_t(M_Z)           = {yt[0]:.4f}")
print(f"  g_3(M_Z)           = {g3[0]:.4f}")
print(f"  y_t / g_3          = {tilt_y_g3[0]:.4f}")
print(f"  (y_t/g_3)^2        = {(tilt_y_g3[0])**2:.4f}")
print(f"  Pendleton-Ross target y_t^2/g_3^2 = 2/9 = {2/9:.4f}")
print()
print(f"  R_Hill(M_Z) = {R_Hill[0]:.4f}   [1.0 = at Hill fixed point]")
print(f"  bracket(M_Z) = {bracket[0]:+.4f}   [0 = at fixed point]")

print(f"\nAt M_Pl (UV extrapolation):")
print(f"  y_t(M_Pl)          = {yt[-1]:.4f}")
print(f"  g_3(M_Pl)          = {g3[-1]:.4f}")
print(f"  y_t / g_3          = {tilt_y_g3[-1]:.4f}")
print(f"  (y_t/g_3)^2        = {(tilt_y_g3[-1])**2:.4f}")
print()
print(f"  R_Hill(M_Pl) = {R_Hill[-1]:.4f}")
print(f"  bracket(M_Pl) = {bracket[-1]:+.4f}")


# ============================================================
# KEY TEST: what would m_t be if SM were AT the Hill fixed point?
# ============================================================

# At Hill fixed point: y_t^2 = [17/20 g_1^2 + 9/4 g_2^2 + 8 g_3^2] / (9/2)
# Using M_Z values:
yt_Hill_at_MZ = np.sqrt(
    ((17/20) * g1[0]**2 + (9/4) * g2[0]**2 + 8 * g3[0]**2) / 4.5
)
m_t_Hill = yt_Hill_at_MZ * v_EW / np.sqrt(2)

print(f"\n" + "=" * 70)
print("HILL QUASI-FIXED POINT PREDICTION vs REALITY")
print("=" * 70)
print(f"  y_t at Hill FP (evaluated at M_Z): {yt_Hill_at_MZ:.4f}")
print(f"  Measured y_t(M_Z):                 {yt[0]:.4f}")
print(f"  Ratio y_t/y_t^Hill:                {yt[0]/yt_Hill_at_MZ:.4f}")
print(f"  Implied m_t at Hill FP:            {m_t_Hill:.1f} GeV")
print(f"  Measured m_t (pole):               {M_t:.1f} GeV")
print(f"  Ratio m_t/m_t^Hill:                {M_t/m_t_Hill:.3f}")


# ============================================================
# PLOTS
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Panel 1: Couplings
ax = axes[0, 0]
ax.plot(log_mu/np.log(10), g1, 'b-', label=r'$g_1$', lw=2)
ax.plot(log_mu/np.log(10), g2, 'g-', label=r'$g_2$', lw=2)
ax.plot(log_mu/np.log(10), g3, 'r-', label=r'$g_3$', lw=2)
ax.plot(log_mu/np.log(10), yt, 'k-', label=r'$y_t$', lw=2.5)
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel('Coupling value')
ax.set_title('SM couplings 1-loop running')
ax.legend()
ax.grid(alpha=0.3)

# Panel 2: Hill fixed-point ratio R_Hill
ax = axes[0, 1]
ax.plot(log_mu/np.log(10), R_Hill, 'k-', lw=2)
ax.axhline(1.0, color='red', ls='--', alpha=0.7, label='Hill FP (R=1)')
ax.fill_between(log_mu/np.log(10), 0.9, 1.1, color='red', alpha=0.1, label=r'$\pm 10\%$')
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel(r'$R_{Hill} = \frac{(9/2) y_t^2}{(17/20)g_1^2 + (9/4)g_2^2 + 8g_3^2}$')
ax.set_title('Proximity to Hill quasi-fixed point')
ax.legend()
ax.grid(alpha=0.3)

# Panel 3: y_t/g_3 ratio
ax = axes[1, 0]
ax.plot(log_mu/np.log(10), tilt_y_g3, 'b-', lw=2, label=r'$y_t/g_3$')
ax.plot(log_mu/np.log(10), tilt_y_g3**2, 'g-', lw=2, label=r'$(y_t/g_3)^2$')
ax.axhline(np.sqrt(2/9), color='red', ls='--', alpha=0.5, label=r'PR target $\sqrt{2/9}$')
ax.axhline(2/9, color='orange', ls='--', alpha=0.5, label=r'PR target $2/9$')
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel('Ratio')
ax.set_title('Pendleton-Ross attractor test')
ax.legend()
ax.grid(alpha=0.3)

# Panel 4: Bracket (= y_t * 16 pi^2 dy_t/dt / y_t)
ax = axes[1, 1]
ax.plot(log_mu/np.log(10), bracket, 'k-', lw=2)
ax.axhline(0, color='red', ls='--', alpha=0.7, label='Stationarity (bracket = 0)')
ax.set_xlabel(r'$\log_{10}(\mu/\mathrm{GeV})$')
ax.set_ylabel(r'$\frac{1}{y_t} \cdot 16\pi^2 \frac{dy_t}{dt}$')
ax.set_title(r'Yukawa stationarity indicator (bracket $\to 0$ = fixed point)')
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('fig_direction2.png', dpi=120, bbox_inches='tight')
plt.close()

print("\nFigure saved: fig_direction2.png")
