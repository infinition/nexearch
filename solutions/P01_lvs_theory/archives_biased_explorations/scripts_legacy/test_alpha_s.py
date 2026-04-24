import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

# ============================================================
# Physical constants (PDG 2024)
# ============================================================

M_Z = 91.1876
M_Pl = 1.22e19
M_t = 172.76
v_EW = 246.22

alpha_em_MZ_inv = 127.951
sin2_theta_W = 0.23122
alpha_em_MZ = 1.0 / alpha_em_MZ_inv
alpha_1_MZ = (5.0/3.0) * alpha_em_MZ / (1.0 - sin2_theta_W)
alpha_2_MZ = alpha_em_MZ / sin2_theta_W

g1_MZ = np.sqrt(4.0 * np.pi * alpha_1_MZ)
g2_MZ = np.sqrt(4.0 * np.pi * alpha_2_MZ)
yt_MZ = np.sqrt(2.0) * M_t / v_EW

# Beta functions (1-loop)
B_SM = np.array([41.0/10.0, -19.0/6.0, -7.0])

def beta_SM_1loop(t, y):
    """
    y = [g1, g2, g3, yt]
    """
    pref = 1.0 / (16.0 * np.pi**2)
    g1, g2, g3, yt = y
    
    dg1 = B_SM[0] * g1**3 * pref
    dg2 = B_SM[1] * g2**3 * pref
    dg3 = B_SM[2] * g3**3 * pref
    
    dyt = yt * pref * (
        (9.0/2.0) * yt**2
        - (17.0/20.0) * g1**2
        - (9.0/4.0) * g2**2
        - 8.0 * g3**2
    )
    
    return [dg1, dg2, dg3, dyt]

def run_rge(alpha_s_mz):
    g3_MZ = np.sqrt(4.0 * np.pi * alpha_s_mz)
    y0 = [g1_MZ, g2_MZ, g3_MZ, yt_MZ]
    
    t_span = (np.log(M_Z), np.log(M_Pl))
    sol = solve_ivp(beta_SM_1loop, t_span, y0, dense_output=True, rtol=1e-8, atol=1e-10)
    return sol

def compute_stationarity_metrics(alpha_s_mz):
    sol = run_rge(alpha_s_mz)
    t = np.linspace(np.log(M_Z), np.log(M_Pl), 500)
    y = sol.sol(t)
    
    g1, g2, g3, yt = y
    pref = 1.0 / (16.0 * np.pi**2)
    dg1 = B_SM[0] * g1**3 * pref
    dg2 = B_SM[1] * g2**3 * pref
    dg3 = B_SM[2] * g3**3 * pref
    dyt = yt * pref * (
        (9.0/2.0) * yt**2
        - (17.0/20.0) * g1**2
        - (9.0/4.0) * g2**2
        - 8.0 * g3**2
    )
    
    rel_rates_sq = (dg1/g1)**2 + (dg2/g2)**2 + (dg3/g3)**2 + (dyt/yt)**2
    sigma = np.sqrt(rel_rates_sq)
    
    min_sigma = np.min(sigma)
    int_sigma = np.trapezoid(sigma, t)
    sigma_mpl = sigma[-1]
    
    # Let's also compute the point where d(y_t/g_3)/dt = 0
    # d(y_t/g_3)/dt = (dyt * g3 - yt * dg3) / g3^2 = 0  => dyt/yt = dg3/g3
    ratio_rate = (dyt/yt) - (dg3/g3)
    
    # Find zero crossing of ratio_rate
    crossings = np.where(np.diff(np.sign(ratio_rate)))[0]
    has_crossing = len(crossings) > 0
    
    return min_sigma, int_sigma, sigma_mpl, has_crossing

alphas_test = np.linspace(0.05, 0.20, 100)
min_sigmas = []
int_sigmas = []
sigma_mpls = []

for a_s in alphas_test:
    ms, isig, smpl, hc = compute_stationarity_metrics(a_s)
    min_sigmas.append(ms)
    int_sigmas.append(isig)
    sigma_mpls.append(smpl)

best_as_min = alphas_test[np.argmin(min_sigmas)]
best_as_int = alphas_test[np.argmin(int_sigmas)]
best_as_mpl = alphas_test[np.argmin(sigma_mpls)]

print(f"Optimal alpha_s(M_Z) for Minimum Sigma: {best_as_min:.4f}")
print(f"Optimal alpha_s(M_Z) for Integral Sigma: {best_as_int:.4f}")
print(f"Optimal alpha_s(M_Z) for Sigma at M_Pl: {best_as_mpl:.4f}")
print(f"Measured alpha_s(M_Z): 0.1179")

# What about the quasi fixed point metric?
# Let's see if there is an alpha_s that exactly makes the stationarity of yt/g3 occur at M_Pl or M_Z
