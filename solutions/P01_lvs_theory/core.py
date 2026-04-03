"""
P01 - LVS Theory (Latent Vacuum Stationarity)
===============================================
Theoretical physics framework. No ML training.

All source material is self-contained in this folder:

    notebooks/                    Jupyter notebooks (computations)
        LVS_Formalization.ipynb   - Shaposhnikov-Wetterich m_H = 126 GeV (strongest result)
        LVS_Validation.ipynb      - 9 empirical validation tests (6 confirmed)
        LVS_Experiments.ipynb     - RG flows, Higgs stability, Page-Wootters
        LVS_Calculations.ipynb    - Dimensional analysis (why 3D is special)
        LVS_Visualizations.ipynb  - 5 interactive physics scenes
        *_executed.ipynb           - Pre-run versions with outputs

    source_docs/                  Theory documents
        LVS_Paper_v2.md           - Complete 13-section paper (main theory)
        discussion.md             - Critical analysis, strengths, limitations
        LVS_reference.pdf         - Reference PDF

    web/                          Web presentations
        LVS_Article.html          - Accessible article version
        LVS_Visualizer.html       - Interactive visualizer

    paper/                        LaTeX for publication
        main.tex                  - Paper skeleton
        refs.bib                  - BibTeX references

    writeups/                     Essays / blog posts
        it_from_fix.md            - "It from Fix" essay draft

    results/                      Structured results
        validation_tests.json     - 9 tests with status and sources

Results summary: see results/validation_tests.json
"""

import os

# All paths are now LOCAL to this solution folder
SOLUTION_DIR = os.path.dirname(os.path.abspath(__file__))
NOTEBOOKS_DIR = os.path.join(SOLUTION_DIR, 'notebooks')
SOURCE_DOCS_DIR = os.path.join(SOLUTION_DIR, 'source_docs')
WEB_DIR = os.path.join(SOLUTION_DIR, 'web')

# Key numbers from LVS validation
HIGGS_PREDICTED = 126.0    # GeV (Shaposhnikov-Wetterich fixed-point condition)
HIGGS_MEASURED = 125.25    # GeV (LHC 2012, PDG 2024)
HADRON_FIT_R2 = 0.999998   # Lattice QCD vs experiment
VALIDATION_CONFIRMED = 6
VALIDATION_SUPPORTED = 3
VALIDATION_TENSION = 0

# Key files
MAIN_PAPER = os.path.join(SOURCE_DOCS_DIR, 'LVS_Paper_v2.md')
DISCUSSION = os.path.join(SOURCE_DOCS_DIR, 'discussion.md')
STRONGEST_NOTEBOOK = os.path.join(NOTEBOOKS_DIR, 'LVS_Formalization.ipynb')
VALIDATION_NOTEBOOK = os.path.join(NOTEBOOKS_DIR, 'LVS_Validation.ipynb')
