"""
SM RGEs at 1-loop including top Yukawa coupling.

Validated against Luo-Xiao 2003 (hep-ph/0207271) equation (3) for the top Yukawa
and against standard Arason et al. 1992 for the gauge sector.

WHY ONLY 1-LOOP:
    Full 2-loop implementation requires dozens of cross-terms with precise signs
    and factors that are error-prone to hand-code. Industry-standard tools (SARAH,
    RGBeta, FlexibleSUSY) are the correct approach for 2-loop+. We restrict to
    1-loop and document the ~5-15% theoretical uncertainty this introduces.

CONVENTIONS:
    - g_1 in GUT normalization: g_1^2 = (5/3) g_Y^2 where g_Y is U(1)_Y hypercharge
    - alpha_i = g_i^2 / (4*pi)
    - t = log(mu), so dg/dt = beta(g)
    - MS-bar scheme
"""

import numpy as np


# ============================================================
# Physical constants (PDG 2024)
# ============================================================

M_Z = 91.1876
M_Pl = 1.22e19
M_t = 172.76
M_H = 125.25
v_EW = 246.22

alpha_em_MZ_inv = 127.951
sin2_theta_W = 0.23122
alpha_s_MZ = 0.1179

alpha_em_MZ = 1.0 / alpha_em_MZ_inv
alpha_1_MZ = (5.0/3.0) * alpha_em_MZ / (1.0 - sin2_theta_W)
alpha_2_MZ = alpha_em_MZ / sin2_theta_W
alpha_3_MZ = alpha_s_MZ

g1_MZ = np.sqrt(4.0 * np.pi * alpha_1_MZ)
g2_MZ = np.sqrt(4.0 * np.pi * alpha_2_MZ)
g3_MZ = np.sqrt(4.0 * np.pi * alpha_3_MZ)

yt_MZ = np.sqrt(2.0) * M_t / v_EW


# ============================================================
# 1-loop beta functions
# ============================================================

# Gauge: dg_i/dt = b_i g_i^3 / (16*pi^2)
B_SM = np.array([41.0/10.0, -19.0/6.0, -7.0])
B_MSSM = np.array([33.0/5.0, 1.0, -3.0])


def beta_SM_1loop(g, yt):
    """
    1-loop SM beta functions for [g_1, g_2, g_3, y_t].
    
    Gauge:  dg_i/dt = b_i g_i^3 / (16 pi^2)
    
    Top Yukawa (Luo-Xiao 2003, eq. 3, top-only approximation):
        dy_t/dt = y_t / (16 pi^2) * [
            (9/2) y_t^2 - (17/20) g_1^2 - (9/4) g_2^2 - 8 g_3^2
        ]
    
    where y_t^2 appears from Y_2(S) ~ 3 y_t^2 + (3/2) y_t^2 = (9/2) y_t^2
    in top-only limit.
    """
    pref = 1.0 / (16.0 * np.pi**2)
    g1, g2, g3 = g
    
    dg1 = B_SM[0] * g1**3 * pref
    dg2 = B_SM[1] * g2**3 * pref
    dg3 = B_SM[2] * g3**3 * pref
    
    dyt = yt * pref * (
        (9.0/2.0) * yt**2
        - (17.0/20.0) * g1**2
        - (9.0/4.0) * g2**2
        - 8.0 * g3**2
    )
    
    return np.array([dg1, dg2, dg3, dyt])


def beta_MSSM_1loop(g):
    """1-loop MSSM gauge beta functions (top Yukawa contribution omitted)."""
    pref = 1.0 / (16.0 * np.pi**2)
    return B_MSSM * g**3 * pref


# ============================================================
# LVS stationarity condition
# ============================================================

def stationarity_measure(g, yt):
    """
    LVS stationarity measure:
        sigma(mu) = sqrt( sum_i (dg_i/dt / g_i)^2 + (dy_t/dt / y_t)^2 )
    
    This is dimensionless and measures how close the theory is to
    a true fixed point (where all couplings stop running).
    
    Returns sigma(mu). A genuine fixed point has sigma = 0.
    """
    betas = beta_SM_1loop(g, yt)
    g1, g2, g3 = g
    
    rel_rates = np.array([
        betas[0] / g1,
        betas[1] / g2,
        betas[2] / g3,
        betas[3] / yt
    ])
    
    return np.sqrt(np.sum(rel_rates**2))


def unification_gap(g):
    """Δ(μ) = √Σ(α_i⁻¹ − α_j⁻¹)² — proximity of gauge couplings."""
    alpha = g**2 / (4*np.pi)
    inv_a = 1.0 / alpha
    d12 = inv_a[0] - inv_a[1]
    d13 = inv_a[0] - inv_a[2]
    d23 = inv_a[1] - inv_a[2]
    return np.sqrt(d12**2 + d13**2 + d23**2)


if __name__ == '__main__':
    print("INITIAL CONDITIONS AT M_Z")
    print("=" * 60)
    print(f"  1/α_1 = {1/alpha_1_MZ:.3f}  (expected ~59.0)")
    print(f"  1/α_2 = {1/alpha_2_MZ:.3f}  (expected ~29.6)")
    print(f"  1/α_3 = {1/alpha_3_MZ:.3f}  (expected ~8.48)")
    print(f"  yt    = {yt_MZ:.4f}  (expected ~0.99)")
    print()
    
    # Sanity check at M_Z
    g0 = np.array([g1_MZ, g2_MZ, g3_MZ])
    betas = beta_SM_1loop(g0, yt_MZ)
    sigma = stationarity_measure(g0, yt_MZ)
    delta = unification_gap(g0)
    
    print(f"1-LOOP RATES AT M_Z")
    print(f"  dg_1/dt = {betas[0]:+.5f}  (g_1 growing ↑)")
    print(f"  dg_2/dt = {betas[1]:+.5f}  (g_2 decreasing ↓)")
    print(f"  dg_3/dt = {betas[2]:+.5f}  (g_3 decreasing ↓, asymptotic freedom)")
    print(f"  dy_t/dt = {betas[3]:+.5f}  (y_t decreasing ↓, due to g_3)")
    print()
    print(f"  Stationarity σ(M_Z) = {sigma:.4f}")
    print(f"  Unification Δ(M_Z) = {delta:.3f}")
