import numpy as np
import matplotlib.pyplot as plt

print("\n--- SIMULATION 3: ÉNERGIE NOIRE DYNAMIQUE (FISHER-KPP) ---")

L = 100
N_x = 500
dx = L / N_x
x = np.linspace(0, L, N_x)

u = np.zeros(N_x)
u[N_x//2 - 2 : N_x//2 + 2] = 1.0 # Seed of actualization

dt = 0.05
steps = 1500
D = 0.5
r = 1.0

volumes = []
for step in range(steps):
    d2u = (np.roll(u, -1) - 2*u + np.roll(u, 1)) / dx**2
    d2u[0] = d2u[-1] = 0
    u += dt * (D * d2u + r * u * (1 - u))
    volumes.append(np.sum(u) * dx)

volumes = np.array(volumes)
t = np.arange(steps) * dt

# Scale factor a(t) ~ V^(1/3)
a = volumes**(1/3)

# Hubble parameter H = a_dot / a
da_dt = np.gradient(a, dt)
H = da_dt / a

# Equation of state parameter w = -1 - (2/3) * (H_dot / H^2)
dH_dt = np.gradient(H, dt)
# Avoid division by zero
valid = H > 1e-5
w = np.zeros_like(H)
w[valid] = -1 - (2.0/3.0) * (dH_dt[valid] / H[valid]**2)

print(f"w(t) final calculé : {w[-1]:.3f} (Rappel: Modèle Standard Lambda-CDM w = -1.0 exact)")

plt.figure(figsize=(12, 4))
plt.subplot(1, 3, 1)
plt.plot(t, a)
plt.title('Facteur Echelle a(t)')

plt.subplot(1, 3, 2)
plt.plot(t[50:], H[50:])
plt.title('Paramètre de Hubble H(t)')

plt.subplot(1, 3, 3)
plt.plot(t[50:], w[50:])
plt.axhline(-1, color='red', linestyle='--', label='Lambda-CDM (w=-1)')
plt.title('Paramètre Énergie Noire w(t)')
plt.legend()
plt.tight_layout()
plt.savefig('sim3_dark_energy.png')
print("Graphique généré : sim3_dark_energy.png")
