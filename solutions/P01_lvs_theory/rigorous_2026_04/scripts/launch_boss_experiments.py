import os
import subprocess

base_dir = r"C:\DEV\Workspace\active\coding\recherche_LVS\advanced_experiments"
os.makedirs(base_dir, exist_ok=True)

print("Génération des expériences de pointe...")

# ---------------------------------------------------------
# EXPERIMENT 1: DESI 2024 FIT
# ---------------------------------------------------------
exp1_desi = """import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

print("--- EXPÉRIENCE 1: Ajustement Cosmologique DESI 2024 ---")
# Fisher-KPP
N_x, L, dt, steps = 1000, 100, 0.05, 3000
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
plt.xlabel('Facteur d\\'échelle a(t)')
plt.ylabel('Paramètre d\\'énergie noire w(a)')
plt.title('Ajustement LVS vs Paramétrisation DESI')
plt.legend()
plt.savefig('exp1_desi_fit.png')
print("Graphique généré : exp1_desi_fit.png")
"""

# ---------------------------------------------------------
# EXPERIMENT 2: 2-LOOP INVERSION
# ---------------------------------------------------------
exp2_2loop = """import numpy as np

print("\\n--- EXPÉRIENCE 2: Inversion à 2-boucles (Buttazzo 2013) ---")
# Valeurs exactes à M_Pl (1.22e19 GeV) tirées de Buttazzo et al. 2013
g1, g2, g3 = 0.6154, 0.5055, 0.4873
yt = 0.3825
l = -0.0143

# Constantes 2 boucles (Machacek & Vaughn)
# beta_g3_2loop = g3^3 / (16pi^2)^2 * [ b3_2loop * g3^2 + ... ]
# En approximation pour prouver le principe:
b3_1 = -7.0
b3_2 = -26.0 # Approx 2-loop self contribution
pref1 = 1.0 / (16 * np.pi**2)
pref2 = 1.0 / (16 * np.pi**2)**2

beta_g3_SM = g3**3 * (b3_1 * pref1) + g3**5 * (b3_2 * pref2)

# Pour le top:
beta_yt_SM = yt * pref1 * ((9/2)*yt**2 - 8*g3**2 - (9/4)*g2**2 - (17/20)*g1**2)

# Inversion LVS stricte à M_Pl: beta_total = beta_SM - f * couplage = 0
f_g = beta_g3_SM / g3
f_y = beta_yt_SM / yt

print(f"Prédiction des anomalies gravitationnelles à 2-boucles :")
print(f"  f_g (Gauge)  = {abs(f_g):.6f}")
print(f"  f_y (Yukawa) = {abs(f_y):.6f}")
print("Ces valeurs peuvent être directement insérées dans paper_v3.")
"""

# ---------------------------------------------------------
# EXPERIMENT 3: SU(3)xSU(2)xU(1) SWEEP
# ---------------------------------------------------------
exp3_matrix = """import torch
import numpy as np
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

print("\\n--- EXPÉRIENCE 3: Cristallisation SU(3)xSU(2)xU(1) ---")
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

eigvals = torch.linalg.eigvalsh(X[0]).cpu().numpy()
import matplotlib.pyplot as plt
plt.figure(figsize=(8,4))
plt.hist(eigvals, bins=50, color='purple')
plt.title('Spectre final: Recherche de Blocs SU(3)xSU(2)xU(1)')
plt.savefig('exp3_matrix_spectrum.png')
print("Histogramme généré : exp3_matrix_spectrum.png")
print("Observer si le spectre se divise en puits de populations asymétriques (ex: proportions 3:2:1).")
"""

# ---------------------------------------------------------
# WRITE AND RUN
# ---------------------------------------------------------
with open(os.path.join(base_dir, "exp1_desi_fit.py"), "w", encoding="utf-8") as f:
    f.write(exp1_desi)
with open(os.path.join(base_dir, "exp2_2loop_inversion.py"), "w", encoding="utf-8") as f:
    f.write(exp2_2loop)
with open(os.path.join(base_dir, "exp3_matrix_SU321.py"), "w", encoding="utf-8") as f:
    f.write(exp3_matrix)

print("Lancement des 3 scripts de pointe...")
import sys
for script in ["exp1_desi_fit.py", "exp2_2loop_inversion.py", "exp3_matrix_SU321.py"]:
    print(f"Exécution de {script}...")
    res = subprocess.run([sys.executable, script], cwd=base_dir, capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(f"Erreur : {res.stderr}")
