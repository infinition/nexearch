import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Physical constants (PDG 2024)
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

def run_rge(alpha_s_mz):
    g3_MZ = np.sqrt(4.0 * np.pi * alpha_s_mz)
    y0 = [g1_MZ, g2_MZ, g3_MZ, yt_MZ]
    t_span = (np.log(M_Z), np.log(M_Pl) + 5)
    sol = solve_ivp(beta_SM_1loop, t_span, y0, dense_output=True, rtol=1e-8, atol=1e-10)
    return sol

alphas_test = np.linspace(0.08, 0.15, 100)
stationarity_scales = []

for a_s in alphas_test:
    sol = run_rge(a_s)
    t = np.linspace(np.log(M_Z), np.log(M_Pl) + 5, 500)
    y = sol.sol(t)
    
    g1, g2, g3, yt = y
    pref = 1.0 / (16.0 * np.pi**2)
    dg3 = B_SM[2] * g3**3 * pref
    dyt = yt * pref * ((9.0/2.0)*yt**2 - (17.0/20.0)*g1**2 - (9.0/4.0)*g2**2 - 8.0*g3**2)
    
    ratio_rate = (dyt/yt) - (dg3/g3)
    
    crossings = np.where(np.diff(np.sign(ratio_rate)))[0]
    if len(crossings) > 0:
        idx = crossings[0]
        # Linear interpolation for better precision
        t_cross = t[idx] - ratio_rate[idx] * (t[idx+1] - t[idx]) / (ratio_rate[idx+1] - ratio_rate[idx])
        scale = np.exp(t_cross)
        stationarity_scales.append(scale)
    else:
        stationarity_scales.append(0)

# Find alpha_s that gives stationarity at M_Pl
closest_idx = np.argmin(np.abs(np.array(stationarity_scales) - M_Pl))
print(f"Alpha_s giving stationarity at M_Pl: {alphas_test[closest_idx]:.5f}")

# Print stationarity scale for measured alpha_s
sol_meas = run_rge(0.1179)
t = np.linspace(np.log(M_Z), np.log(M_Pl) + 5, 1000)
y = sol_meas.sol(t)
g1, g2, g3, yt = y
pref = 1.0 / (16.0 * np.pi**2)
dg3 = B_SM[2] * g3**3 * pref
dyt = yt * pref * ((9.0/2.0)*yt**2 - (17.0/20.0)*g1**2 - (9.0/4.0)*g2**2 - 8.0*g3**2)
ratio_rate = (dyt/yt) - (dg3/g3)
cross = np.where(np.diff(np.sign(ratio_rate)))[0]
if len(cross)>0:
    t_c = t[cross[0]] - ratio_rate[cross[0]]*(t[cross[0]+1]-t[cross[0]])/(ratio_rate[cross[0]+1]-ratio_rate[cross[0]])
    print(f"Stationarity scale for alpha_s=0.1179: 10^{np.log10(np.exp(t_c)):.2f} GeV")
