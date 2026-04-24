import os

base_dir = r"C:\DEV\Workspace\active\coding\recherche_LVS\simulations_FPS"
os.makedirs(base_dir, exist_ok=True)

sim1 = """import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.sparse import csgraph

print("Simulation 1: Émergence des Dimensions via le Flot de Stationnarité")

# On commence avec un graphe aléatoire de N noeuds (dimension non définie / infinie)
N = 100
G = nx.erdos_renyi_graph(N, 0.2)

# Calcul de la dimension spectrale (Spectral Dimension) via les marches aléatoires
def spectral_dimension(G, steps=20):
    L = nx.normalized_laplacian_matrix(G).toarray()
    eigenvalues = np.linalg.eigvalsh(L)
    
    # La probabilité de retour P(t) ~ t^(-d_s / 2)
    t_vals = np.arange(1, steps + 1)
    P_t = np.array([np.sum(np.exp(-eigenvalues * t)) / N for t in t_vals])
    
    # Estimation de ds : -2 * d(log P(t)) / d(log t)
    log_t = np.log(t_vals)
    log_P = np.log(P_t)
    
    # Régression linéaire sur la partie asymptotique
    slope, _ = np.polyfit(log_t[5:], log_P[5:], 1)
    ds = -2 * slope
    return ds, t_vals, P_t

ds_initial, t_vals, P_initial = spectral_dimension(G)
print(f"Dimension spectrale initiale du graphe aléatoire : {ds_initial:.2f}")

# TODO: Implémenter le flot de LVS (Ricci flow discret ou minimisation d'énergie locale)
# pour voir si ds converge naturellement vers 3 ou 4.
"""

sim2 = """import numpy as np
import matplotlib.pyplot as plt

print("Simulation 2: Cristallisation Algébrique (Émergence des Groupes de Jauge)")

# Modèle matriciel abstrait (ex: BFSS model simplifié)
# X_i sont des matrices hermitiennes (i = 1, 2, 3 pour 3D spatiale)
N = 10 # Taille de la matrice (U(N) symétrie initiale)
np.random.seed(42)

X = [np.random.randn(N, N) + 1j * np.random.randn(N, N) for _ in range(3)]
X = [x + x.conj().T for x in X] # Rendre Hermitien

# Flot de stationnarité : dX_i / dt = sum_j [X_j, [X_j, X_i]]
# Ce flot minimise l'action Yang-Mills S = -Tr([X_i, X_j]^2)
dt = 0.01
steps = 500

eigenvalues_history = []

for step in range(steps):
    # Enregistrement des valeurs propres de X[0]
    eigenvalues_history.append(np.linalg.eigvalsh(X[0]))
    
    dX = [np.zeros((N, N), dtype=complex) for _ in range(3)]
    for i in range(3):
        for j in range(3):
            if i != j:
                commutator_1 = np.dot(X[j], X[i]) - np.dot(X[i], X[j])
                commutator_2 = np.dot(X[j], commutator_1) - np.dot(commutator_1, X[j])
                dX[i] += commutator_2
                
    for i in range(3):
        X[i] += dt * dX[i]

eigenvalues_history = np.array(eigenvalues_history)

plt.figure(figsize=(8, 5))
for i in range(N):
    plt.plot(eigenvalues_history[:, i])
plt.title("Évolution des valeurs propres (Cristallisation)")
plt.xlabel("Temps (flot de stationnarité)")
plt.ylabel("Valeurs propres")
plt.savefig('sim2_cristallisation_matrices.png')
print("Simulation terminée, graphique généré. Observer si les valeurs propres se groupent (symétrie brisée SU(3)x...).")
"""

sim3 = """import numpy as np
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
"""

with open(os.path.join(base_dir, "sim1_dimensions.py"), "w", encoding="utf-8") as f:
    f.write(sim1)
with open(os.path.join(base_dir, "sim2_gauge_groups.py"), "w", encoding="utf-8") as f:
    f.write(sim2)
with open(os.path.join(base_dir, "sim3_cosmology.py"), "w", encoding="utf-8") as f:
    f.write(sim3)

print("Fichiers de simulation créés dans le dossier simulations_FPS.")
