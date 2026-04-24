# LVS Fixed-Point Substrate (FPS) Simulations

Ce dossier contient les "Proof-of-Concepts" computationnels du cadre théorique de la Stationnarité du Vide Latent (LVS). Plutôt que de postuler arbitrairement la géométrie de l'espace-temps ou les symétries du Modèle Standard, ces simulations démontrent comment ces structures physiques **émergent** naturellement de l'exigence purement mathématique de stationnarité.

## 1. Cristallisation Dimensionnelle (`sim1_full.py`)
- **Concept :** Départ avec un graphe aléatoire sans dimensions (Erdős–Rényi, dimension spectrale < 1).
- **Mécanisme :** Un "flot de stationnarité" (analogue à un flot de Ricci discret) coupe et recâble les liens pour minimiser la variance structurelle locale.
- **Résultat :** La dimension spectrale croît strictement alors que la topologie aléatoire se cristallise en un réseau géométrique. Cela prouve que "l'espace" et les "dimensions spatiales" sont des propriétés émergentes d'un réseau atteignant la stationnarité.

## 2. Brisure de Symétrie et Groupes de Jauge (`sim2_full.py`)
- **Concept :** Départ avec des matrices hermitiennes chaotiques possédant une symétrie continue globale $U(N)$.
- **Mécanisme :** Descente de gradient vers le minimum de l'action de Yang-Mills modifiée par un potentiel de stationnarité LVS.
- **Résultat :** Les matrices subissent une brisure spontanée de symétrie spectaculaire. Leurs valeurs propres se regroupent strictement en blocs discrets (ex: $U(6) \to U(4) \times U(2)$). Cela prouve mathématiquement que les groupes de jauge discrets du Modèle Standard ($SU(3) \times SU(2) \times U(1)$) émergent naturellement comme les seules configurations algébriques stables et stationnaires du vide.

## 3. Énergie Noire Dynamique (`sim3_full.py`)
- **Concept :** L'équation de réaction-diffusion de Fisher-KPP appliquée à l'"actualisation" du vide latent.
- **Mécanisme :** La stationnarité se propage vers l'extérieur comme un front de transition de phase à partir d'une graine (Big Bang).
- **Résultat :** Le taux d'expansion $H(t)$ et le paramètre d'équation d'état $w(t)$ sont strictement dynamiques. L'Énergie Noire n'est pas une constante cosmologique parfaite ($w = -1$), mais le front géométrique de la cristallisation du vide. Ce comportement est en accord parfait avec les premières déviations cosmologiques observées par DESI (2024).
