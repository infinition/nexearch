import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

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

B_SM = np.array([41.0/10.0, -19.0/6.0, -7.0])

def beta_SM_1loop(t, y):
    pref = 1.0 / (16.0 * np.pi**2)
    g1, g2, g3, yt = y
    dg1 = B_SM[0] * g1**3 * pref
    dg2 = B_SM[1] * g2**3 * pref
    dg3 = B_SM[2] * g3**3 * pref
    dyt = yt * pref * ((9.0/2.0)*yt**2 - (17.0/20.0)*g1**2 - (9.0/4.0)*g2**2 - 8.0*g3**2)
    return [dg1, dg2, dg3, dyt]

def compute_length(alpha_s_mz):
    g3_MZ = np.sqrt(4.0 * np.pi * alpha_s_mz)
    y0 = [g1_MZ, g2_MZ, g3_MZ, yt_MZ]
    t_span = (np.log(M_Z), np.log(M_Pl))
    
    sol = solve_ivp(beta_SM_1loop, t_span, y0, dense_output=True, rtol=1e-8, atol=1e-10)
    t = np.linspace(t_span[0], t_span[1], 1000)
    y = sol.sol(t)
    
    g1, g2, g3, yt = y
    pref = 1.0 / (16.0 * np.pi**2)
    dg1 = B_SM[0] * g1**3 * pref
    dg2 = B_SM[1] * g2**3 * pref
    dg3 = B_SM[2] * g3**3 * pref
    dyt = yt * pref * ((9.0/2.0)*yt**2 - (17.0/20.0)*g1**2 - (9.0/4.0)*g2**2 - 8.0*g3**2)
    
    # Simple Euclidean length in coupling space
    ds = np.sqrt(dg1**2 + dg2**2 + dg3**2 + dyt**2)
    length_euclidean = np.trapezoid(ds, t)
    
    # Zamolodchikov-like length (relative rates, d log g)
    ds_rel = np.sqrt((dg1/g1)**2 + (dg2/g2)**2 + (dg3/g3)**2 + (dyt/yt)**2)
    length_rel = np.trapezoid(ds_rel, t)
    
    return length_euclidean, length_rel

alphas_test = np.linspace(0.05, 0.20, 100)
lengths_euclidean = []
lengths_rel = []

for a_s in alphas_test:
    l_e, l_r = compute_length(a_s)
    lengths_euclidean.append(l_e)
    lengths_rel.append(l_r)

best_e = alphas_test[np.argmin(lengths_euclidean)]
best_r = alphas_test[np.argmin(lengths_rel)]

print(f"Optimal alpha_s for Euclidean length: {best_e:.4f}")
print(f"Optimal alpha_s for relative length: {best_r:.4f}")
print(f"Measured alpha_s: 0.1179")
