import numpy as np
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
