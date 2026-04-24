import numpy as np
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
