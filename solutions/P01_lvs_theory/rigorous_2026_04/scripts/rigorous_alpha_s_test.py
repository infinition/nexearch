import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

print("--- Calcul Rigoureux : Test de Minimisation Globale (Action du Flot) ---")

# Coefficients beta à 1-boucle (sans Higgs pour le moment, jauge + top)
b1 = 41.0/10.0
b2 = -19.0/6.0
b3 = -7.0

# Valeurs aux limites (échelle du Top ~ 172.76 GeV)
t_start = 0.0
t_Pl = np.log(1.22e19 / 172.76)

g1_0 = 0.3583
g2_0 = 0.64779
yt_0 = 0.9369

def beta_functions(t, y):
    g1, g2, g3, yt = y
    pref = 1.0 / (16 * np.pi**2)
    dg1 = g1**3 * pref * b1
    dg2 = g2**3 * pref * b2
    dg3 = g3**3 * pref * b3
    dyt = yt * pref * ((9.0/2.0)*yt**2 - 8.0*g3**2 - 9.0/4.0*g2**2 - 17.0/20.0*g1**2)
    return [dg1, dg2, dg3, dyt]

alpha_s_scans = np.linspace(0.01, 0.16, 100)
actions = []
lengths = []

for alpha_s in alpha_s_scans:
    g3_0 = np.sqrt(4 * np.pi * alpha_s)
    y0 = [g1_0, g2_0, g3_0, yt_0]
    
    sol = solve_ivp(beta_functions, [t_start, t_Pl], y0, dense_output=True, rtol=1e-8, atol=1e-10)
    t_vals = np.linspace(t_start, t_Pl, 2000)
    y_vals = sol.sol(t_vals)
    
    betas = np.array(beta_functions(t_vals, y_vals))
    
    # Action = int sum(beta^2) dt
    action = np.trapezoid(np.sum(betas**2, axis=0), t_vals)
    actions.append(action)
    
    # Longueur Euclidienne = int sqrt(sum(beta^2)) dt
    length = np.trapezoid(np.sqrt(np.sum(betas**2, axis=0)), t_vals)
    lengths.append(length)

min_action_idx = np.argmin(actions)
min_length_idx = np.argmin(lengths)

print(f"Action minimisée pour alpha_s = {alpha_s_scans[min_action_idx]:.5f}")
print(f"Longueur Euclidienne minimisée pour alpha_s = {alpha_s_scans[min_length_idx]:.5f}")

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(alpha_s_scans, actions, 'b-')
plt.axvline(0.1179, color='r', linestyle='--', label='Mesure SM (0.1179)')
plt.axvline(alpha_s_scans[min_action_idx], color='g', linestyle='--', label=f'Min ({alpha_s_scans[min_action_idx]:.4f})')
plt.title("Action globale $\int \sum \\beta^2 dt$")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(alpha_s_scans, lengths, 'b-')
plt.axvline(0.1179, color='r', linestyle='--', label='Mesure SM')
plt.axvline(alpha_s_scans[min_length_idx], color='g', linestyle='--', label=f'Min ({alpha_s_scans[min_length_idx]:.4f})')
plt.title("Longueur globale $\int \sqrt{\sum \\beta^2} dt$")
plt.legend()

plt.tight_layout()
plt.savefig('rigorous_alpha_s_test.png')
print("Graphique sauvegardé : rigorous_alpha_s_test.png")
