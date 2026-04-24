import nbformat as nbf
import os

def create_notebook_1():
    nb = nbf.v4.new_notebook()
    
    md_intro = """# Voie 1: LVS & Asymptotic Safety (Gravité + SM)

## Contexte
La formulation naïve de LVS échoue avec le Modèle Standard seul car elle ignore la gravité. Dans le scénario de l'*Asymptotic Safety* (Reuter, Wetterich, Eichhorn), les fluctuations quantiques de la métrique spatio-temporelle aux échelles trans-planckiennes apportent de nouvelles contributions aux équations du groupe de renormalisation (RG).

Pour un couplage $X$ (jauge ou Yukawa), la fonction $\\beta$ est modifiée :
$$ \\beta_X = \\beta_X^{SM} - f_X X $$
où $f_X$ est une contribution gravitationnelle (souvent proportionnelle à la constante de Newton adimensionnée).

## Objectif
Si LVS exige que la Nature choisisse un point fixe, alors la gravité quantique est *nécessaire* pour atteindre ce point fixe. L'objectif ici est d'implémenter ces contributions gravitationnelles $f_g$ et $f_y$ et d'étudier si l'exigence d'un point fixe stationnaire (stationnarité de LVS) permet de contraindre ou de prédire la valeur de la masse du quark top ($M_t$) ou d'autres paramètres, comme proposé par Eichhorn & Held.
"""
    
    code_init = """import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# TODO: Implémenter les beta-fonctions avec les termes gravitationnels f_g et f_y
# beta_g = beta_g_SM - f_g * g
# beta_y = beta_y_SM - f_y * y
"""
    
    nb['cells'] = [
        nbf.v4.new_markdown_cell(md_intro),
        nbf.v4.new_code_cell(code_init)
    ]
    
    with open('notebooks/Voie_1_Asymptotic_Safety.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)


def create_notebook_2():
    nb = nbf.v4.new_notebook()
    
    md_intro = """# Voie 2: Modèle Jouet (Toy Model) LVS

## Contexte
Le Modèle Standard est un système extrêmement complexe. Pour démontrer la validité conceptuelle de la théorie LVS (Latent Vacuum Stationarity), il est souvent plus puissant de construire un "Toy Model" (un modèle mathématique simplifié) qui capture l'essence du principe.

## Objectif
Nous allons définir un système dynamique abstrait avec 2 ou 3 "couplages". 
1. Définir un espace de configurations et un flot RG abstrait.
2. Appliquer le principe de LVS : la "réalité observée" correspond aux configurations stationnaires (points fixes stables) du système.
3. Démontrer mathématiquement que les valeurs des "constantes" de cet univers jouet sont entièrement déterminées par la condition de stationnarité, éliminant ainsi le besoin de "fine-tuning".
"""
    
    code_init = """import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Définition d'un Toy Model (ex: 2 couplages x et y)
def toy_rg_flow(state, t):
    x, y = state
    # Exemple de flot avec un point fixe non-trivial
    dx = x * (1 - x**2 - y**2) - y
    dy = y * (1 - x**2 - y**2) + x
    return [dx, dy]

# TODO: Analyser la stationnarité, les valeurs propres, et "l'émergence" des constantes
"""
    
    nb['cells'] = [
        nbf.v4.new_markdown_cell(md_intro),
        nbf.v4.new_code_cell(code_init)
    ]
    
    with open('notebooks/Voie_2_Toy_Model.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)


def create_notebook_3():
    nb = nbf.v4.new_notebook()
    
    md_intro = """# Voie 3: Le passage à 2-boucles et la coïncidence de Near-Criticality

## Contexte
À 1-boucle, nous avons découvert que le ratio $y_t/g_3$ présente une stationnarité étonnante, mais le couplage du Higgs $\\lambda$ ne franchit jamais zéro. Cependant, l'analyse rigoureuse du Modèle Standard à 2-boucles (Buttazzo et al. 2013) montre que :
1. $\\lambda$ croise zéro vers $10^{10} - 10^{11}$ GeV.
2. $\\beta_\\lambda$ s'annule vers $10^{17.5}$ GeV (proche de l'échelle de Planck).
C'est ce que Buttazzo appelle une "annulation accidentelle" (near-criticality).

## Objectif
Dans l'optique de LVS, cette annulation n'est pas accidentelle mais structurelle. L'objectif est d'implémenter rigoureusement les équations RG à 2-boucles pour $g_1, g_2, g_3, y_t, \\lambda$. Nous pourrons alors tester l'hypothèse selon laquelle les échelles de stationnarité (comme le minimum de $\\lambda$ et la stationnarité de $(y_t^2+\\lambda)/g_3^2$) coïncident, ce qui serait la signature explicite de LVS aux hautes énergies.
"""
    
    code_init = """import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# TODO: Implémenter les coefficients à 2-boucles (Machacek-Vaughn / Buttazzo 2013)
# Attention aux conventions de normalisation du potentiel de Higgs !
"""
    
    nb['cells'] = [
        nbf.v4.new_markdown_cell(md_intro),
        nbf.v4.new_code_cell(code_init)
    ]
    
    with open('notebooks/Voie_3_2Loop_Coincidence.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)

if __name__ == '__main__':
    os.makedirs('notebooks', exist_ok=True)
    create_notebook_1()
    create_notebook_2()
    create_notebook_3()
    print("Notebooks Voie 1, 2 et 3 créés avec succès dans notebooks/")
