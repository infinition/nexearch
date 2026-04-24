import math

print("--- Vérification Transparente : Calcul f_g et f_y via Eichhorn & Held (2018) ---")
print("Papier de référence : 'Top mass from asymptotic safety' (arXiv:1707.01107)")

# 1. Point Fixe Gravitationnel (G_N*, Lambda*)
# Ces valeurs sont tirées du texte (Section 'Top-bottom mass difference' / Equation 9 manquante dans certaines versions HTML)
# et validées dans le code source LaTeX du papier :
G_N_star = 3.29
Lambda_star = -4.51
print(f"1. Valeurs du point fixe utilisées : G_N* = {G_N_star}, Lambda* = {Lambda_star}")

# 2. Formules des dimensions anomales (Tirées directement du code source LaTeX du papier)
# Pour f_g (Gauge) :
# f_{g}(\Lambda)= \frac{5(1-4\Lambda)}{18 \pi(1-2\Lambda)^2}
f_g_lambda = 5 * (1 - 4 * Lambda_star) / (18 * math.pi * (1 - 2 * Lambda_star)**2)

# Pour f_y (Yukawa) :
# f_y(\Lambda) = \frac{96 +\Lambda (-235 + \Lambda (103+56\Lambda))}{12\pi(3+2\Lambda(-5+4\Lambda))^2}
numerator_y = 96 + Lambda_star * (-235 + Lambda_star * (103 + 56 * Lambda_star))
denominator_y = 12 * math.pi * (3 + 2 * Lambda_star * (-5 + 4 * Lambda_star))**2
f_y_lambda = numerator_y / denominator_y

print(f"\n2. Évaluation des fonctions f_g(Lambda*) et f_y(Lambda*) pures :")
print(f"   f_g(Lambda*) = {f_g_lambda:.5f}")
print(f"   f_y(Lambda*) = {f_y_lambda:.5f}")

# 3. Calcul de la contribution effective au Flot (Ce qui correspond à nos f_g et f_y dans LVS)
# Dans l'équation (4), le terme gravitationnel est : - G_N * g * f_g(Lambda)
# Donc la dimension anomale "effective" LVS est : f_g_AS = G_N * f_g
f_g_AS = G_N_star * f_g_lambda

# Dans l'équation (1), le terme gravitationnel est : + G_N * y * f_y(Lambda)
# Comme LVS s'attend à un terme de type (- f * y), la dimension effective LVS est : f_y_AS = - G_N * f_y
f_y_AS = - G_N_star * f_y_lambda

print(f"\n3. Dimensions anomales effectives AS (Celles à comparer avec LVS) :")
print(f"   f_g_AS = {f_g_AS:.5f}  (Exigence LVS: ~ 0.010)")
print(f"   f_y_AS = {f_y_AS:.5f}  (Exigence LVS: ~ 0.013)")
