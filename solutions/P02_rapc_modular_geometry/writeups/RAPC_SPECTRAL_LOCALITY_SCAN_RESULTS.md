---
title: "Rapc Spectral Locality Scan Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Gate-by-gate RAPC technical note for modular geometry toy experiments."
tags: [RAPC, modular-geometry, quantum-gravity, toy-model]
---

# RAPC spectral-locality phase scan results

This is the tenth RAPC falsification gate.

Previous scan:

```text
score = information - lambda * complexity
```

Problem:

```text
the sparse geometric phase existed, but was narrow
```

This scan adds spectral/locality terms:

```text
score = information
        - lambda_edges * edge_count
        - disconnect_cost * (components - 1)
        + nu_gap * algebraic_connectivity
        - mu_degree * degree_variance
```

The script is:

```text
rapc_spectral_locality_scan_toy.py
```

The raw CSV is:

```text
rapc_spectral_locality_scan_results.csv
```

## Plain Meaning

The previous model asked:

```text
Which graph is short and informative-
```

This model asks:

```text
Which graph is short, informative, connected, and locally well-behaved-
```

The new score rewards connected spectral structure and mildly penalizes uneven
degree distribution.

## Parameters

```text
n = 6
20 random seeds per lambda
6 flow steps
disconnect_cost = 0.25
nu_gap = 0.18
mu_degree = 0.035
```

The random seeds are intentionally the same family as the previous scan, so the
comparison is meaningful.

## Summary

```text
lambda=0.02 empty=00/20 frag=10/20 geo=07/20 dense=03/20 stable_geo=07/20 mean_edges=5.50 mean_gap=0.009 mean_info=0.428
lambda=0.04 empty=00/20 frag=11/20 geo=08/20 dense=01/20 stable_geo=06/20 mean_edges=4.75 mean_gap=0.006 mean_info=0.359
lambda=0.06 empty=00/20 frag=11/20 geo=08/20 dense=01/20 stable_geo=08/20 mean_edges=4.50 mean_gap=0.005 mean_info=0.334
lambda=0.08 empty=00/20 frag=11/20 geo=09/20 dense=00/20 stable_geo=09/20 mean_edges=4.45 mean_gap=0.005 mean_info=0.315
lambda=0.10 empty=00/20 frag=11/20 geo=09/20 dense=00/20 stable_geo=08/20 mean_edges=4.25 mean_gap=0.005 mean_info=0.291
lambda=0.12 empty=00/20 frag=11/20 geo=09/20 dense=00/20 stable_geo=09/20 mean_edges=4.20 mean_gap=0.004 mean_info=0.273
lambda=0.16 empty=00/20 frag=11/20 geo=09/20 dense=00/20 stable_geo=09/20 mean_edges=4.15 mean_gap=0.004 mean_info=0.260
lambda=0.20 empty=00/20 frag=11/20 geo=09/20 dense=00/20 stable_geo=09/20 mean_edges=4.10 mean_gap=0.004 mean_info=0.240
```

## Comparison To Previous Scan

Previous best:

```text
lambda=0.02 -> sparse_geometric 6/20
lambda=0.04 -> sparse_geometric 3/20
lambda=0.06 -> sparse_geometric 2/20
lambda=0.08 -> sparse_geometric 1/20
lambda>=0.10 -> sparse_geometric 0/20
```

New spectral-locality scan:

```text
lambda=0.02 -> sparse_geometric 7/20
lambda=0.04 -> sparse_geometric 8/20
lambda=0.06 -> sparse_geometric 8/20
lambda=0.08 -> sparse_geometric 9/20
lambda=0.10 -> sparse_geometric 9/20
lambda=0.12 -> sparse_geometric 9/20
lambda=0.16 -> sparse_geometric 9/20
lambda=0.20 -> sparse_geometric 9/20
```

This is a real improvement. The sparse geometric phase is much wider and no
longer collapses to empty graphs at high lambda.

## Main Result

Adding a spectral/locality prior widens the geometric phase.

In plain language:

```text
compression alone is too weak
compression + locality preference is much better
```

This supports the RAPC idea that emergent geometry is not just compressed
correlation. It is compressed correlation with a locality/stability criterion.

## Remaining Failure

The model still leaves about half the seeds fragmented:

```text
fragmented_sparse ~= 10-11/20
```

This is not random noise. It means the spectral score can prefer connected
graphs when candidate bridges exist, but it cannot invent bridges that are not
present in the effective candidate edge set.

So the next missing ingredient is probably:

```text
multi-scale bridge generation
```

or:

```text
patch gluing across weak modular links
```

## Important Caveat

The algebraic connectivity values are small:

```text
mean_gap ~= 0.004 to 0.009
```

So the connected graphs are weakly connected. They are sparse patches, not
robust manifolds. This is still toy geometry, not a recovered continuum.

## New RAPC Principle

The emerging candidate principle is now:

```text
geometry = stable sparse spectral compression of modular correlations
```

Not:

```text
geometry = all correlations
```

and not even merely:

```text
geometry = compressed correlations
```

The spectral/locality part matters.

## Next Gate

The next technical gate is:

```text
multi-scale patch gluing
```

Procedure:

1. Find sparse connected components after spectral selection.
2. Compress each component into a patch node.
3. Recompute effective modular couplings between patches.
4. Select weak bridge edges under a separate bridge budget.
5. Test whether fragmented seeds become connected without densifying.

This would mimic the idea that local patches form first, and larger spacetime
connectivity emerges at the next scale.
