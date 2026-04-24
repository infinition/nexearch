import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

print("--- EXPÉRIENCE 1: Ajustement Cosmologique DESI 2024 ---")
# Fisher-KPP
N_x, L, dt, steps = 1000, 100, 0.005, 3000
dx = L / N_x
u = np.zeros(N_x)
u[N_x//2-5:N_x//2+5] = 1.0

D, r = 0.5, 0.8
volumes = []

for step in range(steps):
    d2u = (np.roll(u, -1) - 2*u + np.roll(u, 1)) / dx**2
    d2u[0] = d2u[-1] = 0
    u += dt * (D * d2u + r * u * (1 - u))
    volumes.append(np.sum(u) * dx)

v = np.array(volumes)
t = np.arange(steps) * dt
a = v**(1/3)
a = a / a[-1] # Normalise a(today) = 1

da = np.gradient(a, dt)
H = da / a
dH = np.gradient(H, dt)

# Isoler la zone post-inflation / expansion tardive
mask = (a > 0.2) & (a < 0.99)
a_fit = a[mask]
w_fit = -1 - (2/3) * (dH[mask] / H[mask]**2)

# Modèle CPL utilisé par DESI : w(a) = w0 + wa(1 - a)
def cpl_model(a, w0, wa):
    return w0 + wa * (1 - a)

popt, _ = curve_fit(cpl_model, a_fit, w_fit)
w0_pred, wa_pred = popt

print(f"Prédictions LVS : w0 = {w0_pred:.3f}, wa = {wa_pred:.3f}")
print("Valeurs DESI 2024 (approx) : w0 ~ -0.827, wa ~ -0.75")

plt.figure(figsize=(8,5))
plt.plot(a_fit, w_fit, label='LVS Dynamique')
plt.plot(a_fit, cpl_model(a_fit, w0_pred, wa_pred), '--', label=f'Fit CPL (w0={w0_pred:.2f}, wa={wa_pred:.2f})')
plt.xlabel('Facteur d\'échelle a(t)')
plt.ylabel('Paramètre d\'énergie noire w(a)')
plt.title('Ajustement LVS vs Paramétrisation DESI')
plt.legend()
plt.savefig('exp1_desi_fit.png')
print("Graphique généré : exp1_desi_fit.png")
