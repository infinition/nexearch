import torch
import numpy as np
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

print("\n--- EXPÉRIENCE 3: Cristallisation SU(3)xSU(2)xU(1) ---")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 100
D = 3
lr = 0.05
steps = 2000

print(f"Simulation Tensor GPU sur matrice {N}x{N}...")
X = []
for _ in range(D):
    real = torch.randn(N, N, device=device)
    imag = torch.randn(N, N, device=device)
    H = 0.5 * ((real + 1j*imag) + (real + 1j*imag).adjoint())
    H.requires_grad_(True)
    X.append(H)

optimizer = torch.optim.Adam(X, lr=lr)
I = torch.eye(N, dtype=torch.complex64, device=device)

# Un potentiel asymétrique pour encourager une brisure inégale (type 3, 2, 1)
# P(X) = (X - 3I)^2 (X - 2I)^2 (X - 1I)^2
for step in range(steps):
    optimizer.zero_grad()
    loss_comm = 0
    for i in range(D):
        for j in range(i+1, D):
            comm = torch.matmul(X[i], X[j]) - torch.matmul(X[j], X[i])
            loss_comm -= torch.real(torch.trace(torch.matmul(comm, comm)))
            
    loss_pot = 0
    for i in range(D):
        # V = (X - I)^2 * (X + 0.5 I)^2 * (X - 0.5 I)^2 (puits multiples asymétriques)
        M1 = X[i] - I
        M2 = X[i] + 0.5*I
        M3 = X[i] - 0.5*I
        term = torch.matmul(torch.matmul(M1, M2), M3)
        loss_pot += torch.real(torch.trace(torch.matmul(term, term.adjoint())))
        
    loss = loss_comm + 0.1 * loss_pot
    loss.backward()
    optimizer.step()
    with torch.no_grad():
        for i in range(D):
            X[i].copy_(0.5 * (X[i] + X[i].adjoint()))

eigvals = torch.linalg.eigvalsh(X[0]).detach().cpu().numpy()
import matplotlib.pyplot as plt
plt.figure(figsize=(8,4))
plt.hist(eigvals, bins=50, color='purple')
plt.title('Spectre final: Recherche de Blocs SU(3)xSU(2)xU(1)')
plt.savefig('exp3_matrix_spectrum.png')
print("Histogramme généré : exp3_matrix_spectrum.png")
print("Observer si le spectre se divise en puits de populations asymétriques (ex: proportions 3:2:1).")
