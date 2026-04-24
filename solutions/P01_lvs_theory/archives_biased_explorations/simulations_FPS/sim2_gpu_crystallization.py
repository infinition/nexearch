import torch
import matplotlib.pyplot as plt
import numpy as np
import time
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

print("Initialisation du moteur CUDA pour l'Univers Matriciel...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Matériel détecté : {device}")
if device.type == 'cuda':
    print(f"GPU : {torch.cuda.get_device_name(0)}")

# Paramètres de l'Univers
N = 200  # Taille des matrices (Symétrie U(200) initiale)
D = 3    # Nombre de matrices (dimensions spatiales encodées)
steps = 3000
lr = 0.05
c_potential = 0.5  # Force de la stationnarité (potentiel LVS)

# 1. Création du Chaos Quantique Initial
print(f"\nGénération du chaos initial (Matrices {N}x{N})...")
X = []
for _ in range(D):
    # Matrices complexes aléatoires
    real = torch.randn(N, N, device=device, dtype=torch.float32)
    imag = torch.randn(N, N, device=device, dtype=torch.float32)
    M = torch.complex(real, imag)
    # Rendre strictement Hermitien
    H = 0.5 * (M + M.adjoint())
    H.requires_grad_(True)
    X.append(H)

optimizer = torch.optim.Adam(X, lr=lr)
history = []

I = torch.eye(N, dtype=torch.complex64, device=device)

print("\nDémarrage du Flot de Stationnarité (Descente vers LVS)...")
start_time = time.time()

for step in range(steps):
    optimizer.zero_grad()
    
    loss_comm = 0
    # Terme de Yang-Mills : Minimise la non-commutativité Tr([Xi, Xj]^2)
    for i in range(D):
        for j in range(i+1, D):
            comm = torch.matmul(X[i], X[j]) - torch.matmul(X[j], X[i])
            # comm est anti-hermitien, comm^2 est défini négatif, trace est négative.
            loss_comm -= torch.real(torch.trace(torch.matmul(comm, comm)))
            
    loss_pot = 0
    # Potentiel LVS : Force les matrices dans des puits de stationnarité (ex: +/- 1)
    # V(X) = (X^2 - I)^2
    for i in range(D):
        X2 = torch.matmul(X[i], X[i])
        diff = X2 - I
        loss_pot += torch.real(torch.trace(torch.matmul(diff, diff)))
        
    # Action Totale LVS
    loss = (loss_comm / N) + c_potential * (loss_pot / N)
    
    loss.backward()
    optimizer.step()
    
    # Projection pour s'assurer que les matrices restent parfaitement hermitiennes
    with torch.no_grad():
        for i in range(D):
            X[i].copy_(0.5 * (X[i] + X[i].adjoint()))
            
    # Enregistrement pour la visualisation
    if step % 20 == 0:
        with torch.no_grad():
            eigvals = torch.linalg.eigvalsh(X[0]).cpu().numpy()
            history.append(eigvals)

        if step % 300 == 0:
            print(f"Étape {step:04d}/{steps} | Action de Stationnarité : {loss.item():.4f}")

end_time = time.time()
print(f"\nSimulation terminée en {end_time - start_time:.2f} secondes.")

# ---------------------------------------------------------
# VISUALISATION MAGNIFIQUE DE LA BRISURE DE SYMÉTRIE
# ---------------------------------------------------------
print("Génération du graphique haute résolution...")
history = np.array(history)
x_axis = np.arange(history.shape[0]) * 20

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_facecolor('#0f0f0f')  # Fond sombre pour contraster
fig.patch.set_facecolor('#0f0f0f')

for k in range(N):
    ax.plot(x_axis, history[:, k], color='#00ffff', alpha=0.15, linewidth=1)

ax.set_title(f'Cristallisation Spontanée du Vide (Symétrie U({N}) brisée)', color='white', fontsize=16)
ax.set_xlabel('Temps du Flot LVS (Itérations)', color='white', fontsize=12)
ax.set_ylabel('Spectre des Valeurs Propres', color='white', fontsize=12)
ax.tick_params(colors='white')
ax.grid(color='#333333', linestyle='--', alpha=0.5)

# Text annotations
ax.text(x_axis[-1]*0.8, 1.2, "Bande positive", color='#00ffff', fontsize=12, fontweight='bold')
ax.text(x_axis[-1]*0.8, -1.2, "Bande négative", color='#00ffff', fontsize=12, fontweight='bold')
ax.text(x_axis[10], 0, "Chaos Quantique", color='#ff00ff', fontsize=14, fontweight='bold')

plt.tight_layout()
output_path = os.path.join(os.getcwd(), 'sim2_gpu_crystallization.png')
plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor())
plt.close()

print(f"✅ Graphique final sauvegardé sous : {output_path}")
