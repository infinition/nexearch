---
purpose: Complete instructions for LLM agents working with Nexearch
last_updated: 2026-04-03
version: 2.0
---

# AGENT_GUIDE - Multi-Domain Research Platform

> **You are reading this because you are an LLM/agent working on Fabien's research.**
> This platform centralizes ALL research across multiple domains. Research in one domain often feeds another (e.g., LVS physics theory -> Fixed-Point Substrate in ML).
> Follow these instructions precisely. Update ALL required files. Miss nothing.

---

## 0. Quick Start - Add a Solution in One Shot

**Complete checklist - do NOT skip any step:**

### Step A - Create solution folder (7 items)
1. `cp -r _template/ solutions/NNN_solution_name/`
2. `README.md` - YAML frontmatter + documentation + Next Steps/Roadmap
3. `core.py` (or `core.ipynb` for non-code research) - standalone implementation
4. `notebook.ipynb` - imports core, visualizations, analysis
5. `paper/main.tex` + `paper/refs.bib` - LaTeX paper (can be skeleton, agent updates progressively)
6. `writeups/*.md` - blog posts, book chapters, essays, tutorials (optional, with YAML frontmatter)
7. `results/*.json` - one JSON per experiment phase

### Step B - Update root files (4 items - MANDATORY)
8. `README.md` - add to Quick Navigation + Master Results + Solution Registry + Cross-References
9. `index.html` - add in JS arrays: `SOLUTIONS`, `EXPERIMENTS`, `WRITEUPS`, `ROADMAP` (and `FAILED` if applicable)
10. `RESEARCH_LOG.md` - add dated entry with hypothesis, method, results, decisions
11. `todo.md` - move any completed items to `[x]`, add new ideas discovered

### Step C - If anything failed
12. `archives/failed_approaches.md` - add with failure reason, lesson, revisit flag

**Files that must ALWAYS stay in sync:**
`README.md` tables = `index.html` JS data (`SOLUTIONS`, `EXPERIMENTS`, `WRITEUPS`, `ROADMAP`) = `solutions/NNN/results/*.json`

---

## 1. Research Domains

This platform covers ALL of Fabien's research. Solutions can belong to multiple domains.

| Domain | Tag | Description | Example Topics |
|--------|-----|-------------|----------------|
| **Machine Learning** | `ml` | Neural networks, training algorithms, architectures | Local learning, transformers, VLA/VLM/LLM |
| **Physics** | `physics` | Theoretical and computational physics | LVS theory, fixed-point dynamics, statistical mechanics |
| **Quantum** | `quantum` | Quantum computing, quantum information | Quantum algorithms, quantum error correction |
| **Cybersecurity** | `cybersec` | Security, cryptography, post-quantum | PQC, lattice crypto, adversarial robustness |
| **Robotics** | `robotics` | Embodied AI, manipulation, control | VLA, sim-to-real, motor control |
| **Neuroscience** | `neuro` | Brain-inspired computing, biological plausibility | Hebbian learning, spiking nets, plasticity |
| **Mathematics** | `math` | Pure/applied math supporting other research | Category theory, topology, information geometry |

**Cross-domain examples:**
- LVS theory (physics) -> Fixed-Point Substrate (ml) -> World Model (robotics)
- Entropy gating (neuro) -> Local learning (ml) -> Distributed training (ml)
- Lattice problems (math) -> PQC (cybersec) -> Quantum attacks (quantum)

---

## 2. Solution Structure

```
Nexearch/
+-- README.md                  # Master index - ALL solutions, ALL domains
+-- AGENT_GUIDE.md             # You are here
+-- RESEARCH_LOG.md            # Chronological decisions log
+-- todo.md                    # Raw ideas backlog (human-edited + agent-readable)
+-- .gitignore
+--
+-- datasets/                  # Shared datasets (gitignored)
+-- benchmarks/
|   +-- utils.py               # Shared dataloaders, metrics
+--
+-- solutions/
|   +-- NNN_solution_name/
|       +-- README.md          # YAML frontmatter - THE key file
|       +-- core.py            # Standalone implementation
|       +-- notebook.ipynb     # Imports core, adds visuals
|       +-- paper/             # LaTeX for publication
|       |   +-- main.tex
|       |   +-- refs.bib
|       |   +-- figures/
|       +-- results/           # JSON experiment results
+--
+-- _template/                 # Copy for new solutions
+-- archives/                  # Failed approaches + lessons
```

---

## 3. YAML Frontmatter (Solution README.md)

**ALL fields are required** unless marked "optional":

```yaml
---
id: "NNN"                        # Sequential: 001, 002, 003...
name: Human Readable Name        # Full name
abbreviation: SHORT              # 2-5 letter code
domains: [ml, physics]           # One or more domain tags (see table above)
category: local-learning         # Technical category (see below)
type: learning-rule              # Solution type (see below)
status: breakthrough             # breakthrough | promising | limited | wip | failed
date_created: 2026-04-03
author: Fabien
tags: [local-learning, entropy, hebbian]  # Searchable tags (free-form)

# Results
best_mnist: 97.46                # or null
best_cifar10: 48.22              # or null
# Add any other dataset results as best_DATASETNAME: value

# References
core_principle: "One sentence"   # The core insight
key_equation: "dW = ..."         # Main equation in code form
arxiv: null                      # arXiv ID (e.g., "2401.12345") or null
paper_status: draft              # none | draft | submitted | published
github: null                     # GitHub URL or null

# Cross-references (CRITICAL for multi-domain linking)
builds_on: []                    # Solution IDs this builds on (e.g., ["001"])
enables: []                      # Solution IDs this enables (e.g., ["F01"])
related_to: []                   # Related but not dependent (e.g., ["002"])

# Technical
activation: sigmoid              # or relu, spiking, none, custom
optimizer: sgd_momentum          # or adam, evolutionary, none, custom
layers_optimal: 2                # or null
---
```

### Categories (technical)

| Category | Tag | Description |
|----------|-----|-------------|
| Local Learning | `local-learning` | No backprop through feature layers |
| Gradient-Free | `gradient-free` | No gradient computation at all |
| Transformer Alternative | `transformer-alt` | Replace attention/transformers |
| Neuromorphic | `neuromorphic` | Spiking, event-driven |
| Physics-Inspired | `physics-inspired` | From physical principles |
| Hybrid | `hybrid` | Combines paradigms |
| Novel Architecture | `novel-arch` | New topology/computation model |
| Cryptographic | `crypto` | Crypto algorithms/protocols |
| Quantum Algorithm | `quantum-algo` | Quantum computing algorithms |
| Training Efficiency | `efficiency` | Less compute, same quality |

### Types and their metrics

| Type | Metrics | Units |
|------|---------|-------|
| `learning-rule` | accuracy, convergence_speed | %, steps |
| `classifier` | accuracy, F1, AUC | % |
| `vla` | success_rate, task_completion | % |
| `vlm` | accuracy, retrieval_score | % |
| `llm` | perplexity, BLEU, ROUGE | ppl, score |
| `world-model` | prediction_mse, FID, horizon | float |
| `encoder` | linear_probe_acc, kNN_acc | % |
| `generator` | FID, IS, LPIPS | float |
| `theory` | proof_status, predictions_verified | text |
| `crypto-scheme` | security_level, key_size, speed | bits, bytes, ops/s |
| `quantum-circuit` | gate_count, fidelity, depth | int, %, int |

---

## 4. Cross-References

**This is what makes the platform powerful.** Every solution should declare:

- `builds_on`: "I used ideas from solution X" (e.g., FPS `builds_on: ["LVS_theory"]`)
- `enables`: "My work makes solution Y possible" (e.g., EG `enables: ["F01"]`)
- `related_to`: "Similar topic but independent" (e.g., EG `related_to: ["002"]`)

This creates a **knowledge graph** across domains. An agent can traverse it to:
- Find all downstream applications of a physics theory
- Trace the lineage of an algorithm back to its theoretical roots
- Discover unexpected connections between domains

---

## 5. Paper Management

Each solution has a `paper/` folder:

```
paper/
+-- main.tex          # LaTeX source (use template)
+-- refs.bib          # BibTeX references
+-- figures/          # Generated figures (from notebook)
```

**Paper status lifecycle:**
`none` -> `draft` -> `submitted` -> `published`

**Agent responsibilities:**
- When creating a solution: copy paper template, fill in title/abstract skeleton
- When results improve: update tables and figures in the paper
- When preparing for submission: fill in all sections, compile, check references
- ArXiv ID goes in YAML frontmatter once submitted

---

## 5b. Writeup Management

Writeups are DIFFERENT from papers. They are blog posts, book chapters, essays, tutorials.

Each solution can have a `writeups/` folder with `.md` files:
```
writeups/
+-- intro_article.md     # Blog-style article
+-- chapter_3.md         # Book chapter
+-- tutorial_quickstart.md  # How-to tutorial
```

**Each writeup .md file must have YAML frontmatter:**
```yaml
---
title: "Title"
type: article           # article | book | chapter | essay | tutorial
date: 2026-04-03
author: Fabien
solution: "001"         # solution ID
status: draft           # draft | review | published
abstract: "One paragraph summary."
tags: [local-learning]
---
```

**Types and their rendering:**
| Type | Style | Best for |
|------|-------|----------|
| `article` | Clean, 720px width, balanced | Blog posts, medium articles |
| `book` | Wider margins, centered headings, justified text | Book chapters |
| `chapter` | Same as book | Individual chapters of a larger work |
| `essay` | Narrow (600px), generous line-height, italic headings | Reflective, conceptual pieces |
| `tutorial` | Wide (800px), code-friendly, accent-colored headings | Step-by-step guides, how-tos |

**To register a writeup in the dashboard:**
Add an entry in the `WRITEUPS` array in `index.html`:
```javascript
{id:'wu-001-intro', title:'Title', type:'article', sol:'001', solName:'Entropy-Gated Learning',
 date:'2026-04-03', status:'draft', abstract:'...', tags:['tag1'],
 content:`## Intro\n\nYour markdown content here...`}
```

**Note:** The `content` field contains the full markdown. For long writeups, you can also use `fetch()` to load from the .md file at runtime (works on GitHub Pages but not file://).

---

## 6. Results JSON Format

Generic format - works for any type of research:

```json
{
  "solution_id": "001",
  "experiment": "Phase 6 - EG V4 Push 95%+",
  "date": "2026-04-03",
  "dataset": "MNIST",
  "type": "learning-rule",
  "metric": "accuracy",
  "unit": "%",
  "best_value": 97.46,
  "baseline_name": "Backprop MLP",
  "baseline_value": 98.04,
  "epochs": 100,
  "total_params": 700000,
  "gpu_hours": 1.5,
  "stable": true,
  "history": [
    {"epoch": 1, "loss": 1.60, "value": 80.46, "time": 16.0}
  ]
}
```

For non-ML research (physics, crypto), adapt fields:
```json
{
  "solution_id": "P01",
  "experiment": "LVS prediction verification",
  "metric": "predictions_verified",
  "unit": "count",
  "best_value": 3,
  "notes": "3 out of 5 predictions confirmed experimentally"
}
```

---

## 7. Updating index.html

The HTML dashboard reads data from JS arrays. When adding a solution, add to:

### SOLUTIONS array
```javascript
{id:'NNN', name:'...', abbr:'...', category:'...', type:'...',
 status:'...', date:'...', github:'...', arxiv:'...',
 domains:['ml','physics'],  // multi-domain tags
 crossRefs:{builds_on:['001'], enables:['F01'], related_to:['002']},
 principle:'...', nextStep:'...',
 bestResults:{MNIST:{metric:'accuracy',value:97.46,unit:'%'}},
 paperStatus:'draft',
 equation:{latex:'...', code:'...', components:[...]},
 versions:[...]}
```

### EXPERIMENTS array
```javascript
{phase:1, sol:'001', solName:'Entropy-Gated', name:'...', cat:'...',
 type:'...', dataset:'...', metric:'...', val:97.46, unit:'%',
 ep:100, stable:true, verdict:'...'}
```

### ROADMAP array
```javascript
{sol:'001', p:1, text:'Description of what to do next'}
```

---

## 8. Technical Environment

- **Python:** `C:/Users/infinition/miniconda3/envs/lerobot312/python.exe`
- **GPU:** RTX 4070 Ti (12GB) - keep models under ~10GB VRAM
- **PyTorch:** Use `@torch.no_grad()` for manual weight updates
- **LaTeX:** Standard pdflatex or overleaf-compatible
- **Never use em-dash character** - use hyphen `-` instead

---

## 9. What NOT to Do

- Don't download datasets outside `datasets/`
- Don't modify `_template/` (copy it)
- Don't forget to update root README.md AND index.html when adding results
- Don't repeat known failed approaches (check archives/ first)
- Don't skip cross-references - they are the connective tissue of the platform
- Don't skip paper/ creation - even a skeleton is valuable
- Don't forget todo.md - move items to `[x]` when started
- Don't leave results only in one place - sync README + index.html + JSON
