import numpy as np
import matplotlib.pyplot as plt

print("Simulation 3: L'Énergie Noire comme Actualisation (Fisher-KPP)")

# Grille spatiale 1D
L = 100
N_x = 500
dx = L / N_x
x = np.linspace(0, L, N_x)

# u(x,t) : Probabilité que le nœud du vide soit "actualisé" (stationnaire)
u = np.zeros(N_x)
u[N_x//2 - 5 : N_x//2 + 5] = 1.0 # Big Bang local (graine de stationnarité)

dt = 0.01
steps = 2000
D = 1.0   # Diffusion (intrication quantique)
r = 1.0   # Taux de conversion (taux de stationnarisation)

volumes = []

for step in range(steps):
    # Fisher-KPP equation: du/dt = D * d^2u/dx^2 + r * u * (1 - u)
    d2u_dx2 = (np.roll(u, -1) - 2*u + np.roll(u, 1)) / dx**2
    d2u_dx2[0] = d2u_dx2[-1] = 0 # Boundaries
    
    u += dt * (D * d2u_dx2 + r * u * (1 - u))
    
    # Volume de l'univers observable (intégrale de u)
    volumes.append(np.sum(u) * dx)

volumes = np.array(volumes)
t = np.arange(steps) * dt

# Facteur d'échelle a(t) ~ Volume^(1/3)
a_t = volumes**(1/3)

# Paramètre de Hubble H = (da/dt) / a
da_dt = np.gradient(a_t, dt)
H_t = da_dt / a_t

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(t, volumes)
plt.title("Volume de l'Univers vs Temps")
plt.xlabel("Temps")

plt.subplot(1, 2, 2)
plt.plot(t[10:], H_t[10:])
plt.title("Paramètre de Hubble H(t)")
plt.xlabel("Temps")
plt.savefig('sim3_fisher_kpp_expansion.png')
print("Simulation terminée, graphique généré. Observer la dynamique de l'expansion.")
