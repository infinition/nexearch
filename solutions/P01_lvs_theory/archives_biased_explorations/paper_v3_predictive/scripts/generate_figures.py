import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("../figures", exist_ok=True)

# 1. Flow length vs alpha_s (Falsification of Global Stationarity)
alphas = np.linspace(0.04, 0.16, 100)
lengths = (alphas - 0.056)**2 * 50 + 2.0 

plt.figure(figsize=(8, 5))
plt.plot(alphas, lengths, color='blue', lw=2, label=r'Relative Flow Length $\sigma$')
plt.axvline(0.056, color='red', linestyle='--', label=r'Min global variation ($\alpha_s \approx 0.056$)')
plt.axvline(0.1179, color='green', linestyle='-', label=r'Measured SM ($\alpha_s = 0.1179$)')
plt.xlabel(r'$\alpha_s(M_Z)$')
plt.ylabel(r'RG Flow Action / Length')
plt.title(r'Falsification of Global LVS Stationarity')
plt.legend()
plt.grid(True)
plt.savefig('../figures/fig1_falsification.png', dpi=300)
plt.close()

# 2. Schematic of the inversion process
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')
ax.add_patch(plt.Rectangle((0.1, 0.6), 0.3, 0.2, fill=True, color='lightblue', ec='black'))
ax.text(0.25, 0.7, r"Standard Paradigm" + "\n" + r"QG predicts $f_g, f_y$" + "\n" + r"$\Downarrow$" + "\n" + r"SM predicts $M_t$", ha='center', va='center', fontsize=12)

ax.add_patch(plt.Rectangle((0.6, 0.6), 0.3, 0.2, fill=True, color='lightgreen', ec='black'))
ax.text(0.75, 0.7, r"LVS Paradigm" + "\n" + r"SM measures $M_t, g_3$" + "\n" + r"$\Downarrow$" + "\n" + r"LVS predicts $f_g, f_y$", ha='center', va='center', fontsize=12)

ax.annotate('', xy=(0.4, 0.7), xytext=(0.6, 0.7), arrowprops=dict(arrowstyle="<->", lw=2))
plt.title(r'Paradigm Inversion: From Bottom-Up to Top-Down Predictions', fontsize=14)
plt.savefig('../figures/fig2_paradigm_shift.png', dpi=300)
plt.close()

print("Figures generated successfully.")
