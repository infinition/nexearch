---
id: "P02"
name: RAPC Modular Geometry
abbreviation: RAPC
domains: [physics, quantum, math]
category: physics-inspired
type: theory
status: wip
date_created: 2026-04-24
author: Fabien
tags: [quantum-gravity, modular-theory, von-neumann-algebras, coarse-graining, emergent-geometry, bmv]

best_mnist: null
best_cifar10: null
best_sparse_geometric: 45
best_stable_geo: 45

core_principle: "Geometry may be the stable sparse spectral compression of modular quantum correlations."
key_equation: "score = I_modular - lambda*edges - disconnect_cost*(components-1) + nu*lambda_2(L) - mu*Var(degree)"
arxiv: null
paper_status: draft
github: null

builds_on: ["P01"]
enables: []
related_to: ["002", "F03"]

activation: none
optimizer: none
layers_optimal: null
---

# P02 - RAPC Modular Geometry

## TL;DR

RAPC is a toy research program for testing whether spacetime-like geometry can emerge from algebraic quantum correlations without assuming points, a background metric, or a fixed time variable. The working hypothesis is:

```text
geometry = stable sparse spectral compression of modular correlations
```

The current code is not a theory of quantum gravity. It is a falsification lab. It checks whether increasingly strict toy gates can produce BMV-capable links, effective pair geometry, sparse locality, and stable graph phases.

## Core Chain

```text
global state rho
-> modular Hamiltonian K = -log(rho)
-> non-factorizing modular couplings
-> coarse-grained effective pair graph
-> sparse spectral compression
-> BMV-capable links
```

## Core Score

```python
score = information
score -= lambda_edges * edge_count
score -= disconnect_cost * (components - 1)
score += nu_gap * algebraic_connectivity
score -= mu_degree * degree_variance
```

## Version History

| Version | Gate | Result | Verdict |
|---------|------|--------|---------|
| G1 | BMV finite channel | Bilocal phase gives concurrence 0.105; LOCC gives 0 | Passed toy BMV gate |
| G2 | Modular phase | `K=-log(rho)` extracts `ZZ:0.35`, concurrence 0.644 | Passed finite modular gate |
| G3 | Subalgebra selection | Finds hidden pair `(0,1)` and dominant edge | Passed pair selection gate |
| G4 | Hypergraph coarse-graining | `Z0Z1Z2 + hZ2 -> J_eff Z0Z1` | Passed hypergraph to pair gate |
| G5 | Automatic coarse-graining | Distinguishes direct vs generated edges | Passed generated-edge gate |
| G6 | Iterated flow | Found empty, dense, decaying, and stable-topology regimes | Mixed |
| G7 | Sparse budget | Tree/MDL prevents densification, preserves BMV capacity | Promising |
| G8 | MDL budget selection | Three phases: dense, sparse, empty | Promising but narrow |
| G9 | Phase scan | Simple MDL sparse geometry only 6/20 at best | Limited |
| G10 | Spectral locality scan | Sparse geometry widened to 9/20 over broad lambda range | Best current result |
| G11 | Patch gluing | No bridges added | Failed, useful diagnosis |
| G12 | Residual patch gluing | Stable 9/20, still no bridges | Limited |

## Best Result

The strongest current toy result is the spectral-locality phase scan:

```text
lambda=0.08 -> sparse_geometric 9/20, stable_geo 9/20
lambda=0.10 -> sparse_geometric 9/20, stable_geo 8/20
lambda=0.12 -> sparse_geometric 9/20, stable_geo 9/20
lambda=0.16 -> sparse_geometric 9/20, stable_geo 9/20
lambda=0.20 -> sparse_geometric 9/20, stable_geo 9/20
```

Compared with simple MDL:

```text
lambda=0.08 -> sparse_geometric 1/20
lambda>=0.10 -> sparse_geometric 0/20
```

Adding spectral locality is therefore a real improvement in this toy setup.

## Key Design Decisions

| Decision | Why |
|----------|-----|
| Use finite Type-I toy models first | Full Type-III von Neumann algebra machinery is too heavy for first falsification gates |
| Treat ML/GPU as microscope only | The final rule must be explicit; a neural network cannot be a fundamental law |
| Use BMV as first empirical-facing gate | If a candidate cannot produce non-LOCC entangling links, it fails the gravity-quantum interface |
| Separate direct and generated edges | A link already present microscopically is not the same as geometry emerging by coarse-graining |
| Add spectral locality | Compression alone produced fragmented or empty graphs too often |

## What Failed

| Variant | Result | Lesson |
|---------|--------|--------|
| Pure pairwise scan on three-body hyperedge | No pair selected | Fundamental substrate may be hypergraph-like |
| Unbiased hidden node | No effective pair edge | Reference/asymmetry is required for pair geometry |
| Simple MDL phase scan | Sparse geometry narrow, max 6/20 | Compression alone is too weak |
| First patch gluing | `mean_bridges=0` | Pair-only flow discards hypergraph memory |
| Residual patch gluing | Still `mean_bridges=0` | Current bridge rule is too conservative or seeds lack weak inter-patch links |

## Files

- `core.py` - standalone entry point and summary runner
- `source/` - all RAPC toy scripts
- `notebook.ipynb` - RAPC Lab notebook with scans, plots, and GPU smoke test
- `results/` - CSV scans plus JSON summaries
- `writeups/` - detailed gate-by-gate notes with YAML frontmatter
- `paper/` - draft LaTeX skeleton

## Reproduction

```bash
cd C:\DEV\Workspace\active\coding\Nexsearch\solutions\P02_rapc_modular_geometry
python core.py
python source\rapc_spectral_locality_scan_toy.py
jupyter lab notebook.ipynb
```

## Current Scientific Status

RAPC is a useful toy framework, not a confirmed physical theory. The current evidence supports only this limited statement:

```text
In finite toy models, modular-correlation compression plus spectral locality can produce stable sparse BMV-capable effective graphs more robustly than compression alone.
```

It does not yet derive:

```text
Lorentzian 4D spacetime
Einstein equations
Born rule from first principles
Type-III to Type-II crossed product dynamics
universal horizon entropy A/4G
```

## Next Steps / Roadmap

### Priority 1 - Make Patch Gluing Work or Fail Clearly
- [ ] Design bridge candidates that preserve weak inter-patch modular memory
- [ ] Compare conservative, aggressive, and variational bridge rules
- [ ] Add a no-densification guard for bridge selection

### Priority 2 - Map the Phase Diagram
- [ ] Run 1000+ seeds per lambda using the RTX 4070 Ti as exploration hardware
- [ ] Track sparse-geometric phase width vs `disconnect_cost`, `nu_gap`, `mu_degree`
- [ ] Measure whether the sparse phase survives at larger node counts

### Priority 3 - Replace Toy Imports
- [ ] Replace finite tensor-factor assumptions with subalgebra selection rules
- [ ] Replace Pauli-basis projection with basis-independent operator algebra diagnostics
- [ ] Replace hand-chosen modular time with observer/coarse-graining data

### Speculative / Long-term
- [ ] Relate effective graph Laplacian spectra to emergent dimension estimators
- [ ] Connect the entropy budget to horizon-area scaling
- [ ] Formulate a Type-II crossed-product analogue of the toy flow
