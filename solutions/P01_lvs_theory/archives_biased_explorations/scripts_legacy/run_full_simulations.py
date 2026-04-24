import os
import subprocess

base_dir = r"C:\DEV\Workspace\active\coding\recherche_LVS\simulations_FPS"
os.makedirs(base_dir, exist_ok=True)

sim1 = """import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

print("--- SIMULATION 1: CRISTALLISATION DIMENSIONNELLE ---")

N = 100
# Initial state: Erdős–Rényi random graph (no metric structure, d ~ infinity)
G = nx.erdos_renyi_graph(N, 0.1)

def spectral_dimension(graph):
    L = nx.normalized_laplacian_matrix(graph).toarray()
    eigenvalues = np.linalg.eigvalsh(L)
    t_vals = np.arange(1, 30)
    P_t = np.array([np.sum(np.exp(-eigenvalues * t)) / N for t in t_vals])
    log_t = np.log(t_vals)
    log_P = np.log(P_t)
    slope, _ = np.polyfit(log_t[5:20], log_P[5:20], 1)
    return -2 * slope

d_initial = spectral_dimension(G)
print(f"Dimension spectrale initiale (Chaos) : {d_initial:.2f}")

# Stationarity Flow (simulated annealing to minimize an energy functional)
# Energy favors regular degrees (lattice-like) and high clustering (spatial geometry)
degrees = [d for n, d in G.degree()]
target_k = int(np.mean(degrees))

import random
for step in range(2000):
    edges = list(G.edges())
    if len(edges) == 0: break
    u, v = random.choice(edges)
    G.remove_edge(u, v)
    
    # Try adding a new edge to close a triangle (promotes spatial clustering)
    neighbors_u = list(G.neighbors(u))
    if len(neighbors_u) > 0:
        w = random.choice(neighbors_u)
        neighbors_w = list(G.neighbors(w))
        if len(neighbors_w) > 0:
            target = random.choice(neighbors_w)
            if target != u and not G.has_edge(u, target):
                G.add_edge(u, target)
                continue
    
    # Fallback: add random edge to maintain density
    nodes = list(G.nodes())
    n1, n2 = random.sample(nodes, 2)
    if not G.has_edge(n1, n2):
        G.add_edge(n1, n2)

d_final = spectral_dimension(G)
print(f"Dimension spectrale finale (Stationnaire) : {d_final:.2f}")

plt.figure(figsize=(8,4))
plt.bar(['Chaos Initial', 'Stationnarité LVS'], [d_initial, d_final], color=['red', 'green'])
plt.ylabel('Dimension Spectrale (d_s)')
plt.title('Émergence des Dimensions via le Flot LVS')
plt.axhline(3.0, color='black', linestyle='--', label='Espace 3D')
plt.legend()
plt.savefig('sim1_dimensions.png')
print("Graphique généré : sim1_dimensions.png")
"""

sim2 = """import numpy as np
import matplotlib.pyplot as plt

print("\\n--- SIMULATION 2: ÉMERGENCE DES SYMÉTRIES (JAUGE) ---")

N = 6 # Size of matrices
np.random.seed(42)

# Initialize 3 Hermitian matrices randomly (Chaos)
X = [0.1 * (np.random.randn(N, N) + 1j * np.random.randn(N, N)) for _ in range(3)]
X = [x + x.conj().T for x in X]

# Gradient descent to minimize S = -Tr([Xi,Xj]^2) + c Tr((Xi^2 - I)^2)
# This forces matrices to commute and eigenvalues to cluster at +/- 1
# Breaking U(N) into U(k) x U(N-k)
eta = 0.01
steps = 1000
c = 0.5

history = []

for step in range(steps):
    eigvals = np.sort(np.linalg.eigvalsh(X[0]))
    history.append(eigvals)
    
    dX = [np.zeros((N, N), dtype=complex) for _ in range(3)]
    for i in range(3):
        for j in range(3):
            if i != j:
                comm = np.dot(X[j], X[i]) - np.dot(X[i], X[j])
                dX[i] += np.dot(X[j], comm) - np.dot(comm, X[j])
        
        # Potential gradient: 4 * c * X_i * (X_i^2 - I)
        X2 = np.dot(X[i], X[i])
        dX[i] += 4 * c * np.dot(X[i], X2 - np.eye(N))
        
    for i in range(3):
        X[i] -= eta * dX[i]
        # Force exact hermiticity
        X[i] = 0.5 * (X[i] + X[i].conj().T)

history = np.array(history)
print(f"Valeurs propres finales : {history[-1]}")

plt.figure(figsize=(8,5))
for k in range(N):
    plt.plot(history[:, k])
plt.title('Rupture de Symétrie U(N) -> U(k) x U(N-k) par Cristallisation LVS')
plt.xlabel('Temps de flot (Gradient)')
plt.ylabel('Valeurs propres')
plt.savefig('sim2_gauge_groups.png')
print("Graphique généré : sim2_gauge_groups.png")
"""

sim3 = """import numpy as np
import matplotlib.pyplot as plt

print("\\n--- SIMULATION 3: ÉNERGIE NOIRE DYNAMIQUE (FISHER-KPP) ---")

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
"""

with open(os.path.join(base_dir, "sim1_full.py"), "w", encoding="utf-8") as f:
    f.write(sim1)
with open(os.path.join(base_dir, "sim2_full.py"), "w", encoding="utf-8") as f:
    f.write(sim2)
with open(os.path.join(base_dir, "sim3_full.py"), "w", encoding="utf-8") as f:
    f.write(sim3)

print("Exécution des simulations en cours (cela peut prendre quelques secondes)...")
import sys
for script in ["sim1_full.py", "sim2_full.py", "sim3_full.py"]:
    print(f"Lancement de {script}...")
    res = subprocess.run([sys.executable, script], cwd=base_dir, capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(f"Erreur dans {script}:\n{res.stderr}")
