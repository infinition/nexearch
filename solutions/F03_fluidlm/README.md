---
id: "F03"
name: "FluidLM"
abbreviation: FLM
domains: [ml]
category: transformer-alt
type: llm
status: promising
date_created: 2025
author: Fabien
tags: [language-model, pde, reaction-diffusion, transformer-free, attention-free, O(N), adaptive-compute, cpu-inference, mamba, ssm, swiglu, diffusion, turing-patterns]
best_tinystories_loss: 10.76
best_mnist: null
best_cifar10: null
core_principle: "Replace O(N^2) attention with O(N) reaction-diffusion PDEs. Tokens = concentrations, learning = diffusion+reaction dynamics. GPU-free inference, no KV-cache."
key_equation: "du/dt = sum(D_k * nabla^2(u)) + SSM(u) + SwiGLU(u) + alpha*h"
arxiv: null
paper_status: submitted
paper_venue: "NeurIPS 2025"
github: "https://github.com/infinition/FluidLM"
builds_on: ["P01"]
enables: []
related_to: ["F02"]
params: {total: 44200000, core: 18500000, embedding: 25700000}
---

# F03 - FluidLM

## TL;DR
**Transformer-free language model** replacing O(N^2) self-attention with **reaction-diffusion PDEs**. Tokens = chemical concentrations, information spreads via multi-scale diffusion. O(N) scaling, zero KV-cache, GPU-free inference, adaptive computation (~30% savings). 44.2M params, V4.5.0, trained on TinyStories. Under NeurIPS 2025 submission.

---

## Core Equation

$$\frac{du}{dt} = \underbrace{\sum_k D_k \cdot \nabla^2(u)}_{\text{multi-scale diffusion}} + \underbrace{\text{SSM}(u)}_{\text{selective routing}} + \underbrace{\text{SwiGLU}(u, \theta)}_{\text{nonlinear reaction}} + \underbrace{\alpha \cdot h}_{\text{global memory}}$$

**Time integration (Forward Euler):**
$$u_{t+1} = \text{RMSNorm}\Big(u_t + \Delta t \cdot [\text{diffusion} + \text{SSM} + \text{reaction} + \alpha h + \alpha_{local} \cdot \text{local\_mem}]\Big)$$

**Adaptive halt (Turing Equilibrium):**
$$\text{turbulence} = \text{mean}\left(\frac{|u_{t+1} - u_t|}{|u_t| + \epsilon}\right) \xrightarrow{\text{if} < \epsilon} \text{HALT}$$

---

## Architecture (V4.5.0)

```
Token Input (seq_len=128-256)
    |
[Embedding] (d_model=512, weight-tied with head)
    |
[Sinusoidal PE] (0 params)
    |                         Multi-scale Diffusion (3 dilations: 1, 4, 16)
[FluidLayer x4] ------>  +-- Selective SSM (Mamba-style, d_state=16)
    |           T<=8      +-- SwiGLU Reaction (8/3 expansion)
    |           steps     +-- Local Memory (causal avg pool)
    |                     +-- Global Memory Pump h (B,D) + Forget Gate
    |
[RMSNorm]
    |
[Linear Head] (weight-tied)
    |
Logits (vocab: 50,257 GPT-2 BPE)
```

### Components

| Component | Role | Equation | Complexity |
|-----------|------|----------|------------|
| Multi-Scale Diffusion | Spatial coherence, syntax | `D_k * [1,-2,1] @ u` at dilations [1,4,16] | O(N) |
| Selective SSM (Mamba) | Content-based routing | `h_t = A_t*h_{t-1} + B_t*x_t; y_t = C_t*h_t` | O(N) |
| SwiGLU Reaction | Semantic nonlinearity | `(W_gate(x) * swish(W_up(x))) @ W_down` | O(N*d) |
| Global Memory Pump | Cross-sequence context | `h <- decay*h + gate*tanh(summary)`, O(1) memory | O(d) |
| Local Memory | Top-level structure | Causal avg pool + projection | O(N) |
| Laplacian Grad Loss | Spatial regularizer | Penalizes high-freq noise on hidden states | - |
| Adaptive Halt | Compute savings | Stop when turbulence < epsilon (~30% save) | - |

### Parameter Count (44.2M total)

| Component | Params | Notes |
|-----------|--------|-------|
| Embedding (weight-tied) | ~25.7M | GPT-2 vocab (50,257) |
| SwiGLU Reaction x4 | ~10.7M | 8/3 expansion |
| Selective SSM x4 | ~3.4M | Mamba-style |
| Memory Gates x4 | ~2.1M | h-aware sigmoid |
| Multi-Head LongConv x4 | ~1.2M | K=33/65/129/257 |
| Local Memory x4 | ~1.05M | Causal pool |
| Diffusion coeffs x4 | ~6K | Learnable per scale |
| RMSNorm + dt_gate | ~8K | Per-layer |

---

## Version History

| Version | Date | Key Changes | Status |
|---------|------|-------------|--------|
| V4.2.0 | 2025 | PoC: Forward Euler, learned pos_emb, simple diffusion | Proof of concept |
| V4.3.0 | 2025 | RoPE, MLP 4x expansion | Improved |
| V4.4.0 | 2026 | CausalLongConv K=65, sinusoidal PE, cosine LR, memory pump (B,L,D) | Major upgrade |
| V4.4.1-3 | 2026 | Bug fixes: dt slider, LongConv init, h-state O(1) restored | Stability |
| V4.4.4-7 | 2026 | Forget Gate, layer-wise grad clip, local memory, desaturated gates | Stability |
| V4.4.8 | 2026 | Laplacian grad_loss + curriculum scheduler (from FluidWorld) | Cross-pollination |
| **V4.5.0** | **2026** | **SwiGLU, Selective SSM (Mamba), Multi-Head LongConv, RMSNorm** | **Current** |

---

## Training Results

**Dataset:** TinyStories (English child stories, ~28MB, GPT-2 BPE tokenization)

| Metric | Value | Notes |
|--------|-------|-------|
| Best loss | 10.76 | Step 801 |
| Initial loss | ~219 | Step 51 |
| Convergence | 219 -> 10.76 | Steep descent over 800 steps |
| Tokens seen | 27.9M | |
| VRAM | 10.9-16.2 GB | Linear with seq_len |
| Avg adaptive steps | 8-12 | Out of max T=8 |
| Turbulence | 0.44-0.62 | Diffusion measure |

### What's Demonstrated
- Architecture trains and converges
- Linear memory scaling (vs quadratic for Transformer)
- Adaptive computation fires correctly
- O(1) memory pump (128x less than seq-length variant)
- Multi-scale diffusion propagates information

### What's NOT Demonstrated Yet
- Competitive perplexity vs equivalent-size Transformers
- Scaling beyond 44M params
- Generalization beyond TinyStories
- Whether V4.5.0 breaks through loss plateau

---

## Complexity Comparison

| Property | Transformer | FluidLM |
|----------|-------------|---------|
| Per-layer | O(N^2 * d) | O(N * d * s) |
| Memory | O(N * d * L) | O(N * d) |
| KV-cache | O(N * d * L) growing | 0 (eliminated) |
| Per-token inference | O(N) growing | O(d * s) constant |
| CPU efficiency | Poor (random access) | Excellent (sequential, SIMD) |
| Adaptive compute | No | Yes (~30% savings) |

---

## Loss Decomposition

```
total = main_loss + eq_weight*turbulence + 0.01*diffusion_reg + gate_reg + grad_loss_weight*laplacian_smoothness
```

| Loss | Purpose | Weight |
|------|---------|--------|
| main_loss | CrossEntropy(logits, targets) | 1.0 |
| eq_loss | Equilibrium regularizer (turbulence) | 0.01 (curriculum) |
| diff_loss | Diffusion coefficient bounds | 0.01 |
| gate_reg | Memory gate saturation penalty | 0.08 |
| grad_loss | Laplacian smoothness (from FluidWorld) | 0.005 (curriculum) |

---

## Training Configuration

```json
{
  "lr": 0.0003, "batch_size": 4, "seq_len": 128, "d_model": 512,
  "t_steps": 6, "dt": 0.1, "epsilon": 0.05,
  "eq_weight": 0.01, "gate_reg_weight": 0.08, "grad_loss_weight": 0.005,
  "curriculum_steps": 5000, "warmup_steps": 500, "total_steps": 50000,
  "grad_accum_steps": 8, "temperature": 0.8, "repetition_penalty": 1.5
}
```

**Differential LR:** Diffusion coefficients get 10x-100x boost (dilation-dependent), SSM gets 2x.

---

## Cross-References

- **Builds on [P01 LVS Theory](../P01_lvs_theory/):** PDE dynamics as computational substrate inspired by fixed-point physics
- **Related to [F02 FluidWorld](https://github.com/infinition/FluidWorld):** Same PDE foundation, cross-pollinated Laplacian grad_loss and curriculum scheduler
- **Related to [002 Fixed-Point Substrate](../002_fixed_point_substrate/):** Both explore PDE/fixed-point computation, but FPS uses equilibrium while FluidLM uses temporal dynamics

---

## Files (self-contained)

### source/ - Core Implementation
| File | Lines | Content |
|------|-------|---------|
| `text_models.py` | 498 | RMSNorm, SinusoidalPE, SwiGLU, SelectiveSSM, FluidLayer, FluidNet |
| `train_engine.py` | 881 | DataLoader, BPE, training loop, loss, logging |
| `web_app.py` | 1520 | Streamlit real-time dashboard |
| `launch_lab.py` | ~50 | Orchestrates training + dashboard |
| `prepare_data.py` | ~30 | TinyStories downloader |
| `config.json` | - | Hyperparameters (hot-reloadable) |
| `README.md` | - | Original project README |

### paper/ - Publication
| File | Content |
|------|---------|
| `fluidlm.tex` | LaTeX paper (NeurIPS 2025 format) |
| `fluidlm.pdf` | Compiled PDF |
| `references.bib` | BibTeX |
| `neurips_2025.sty` | NeurIPS style file |

### results/
| File | Content |
|------|---------|
| `training_stats.json` | Loss trajectory, metrics per step |

---

## Honest Assessment

### Strengths
- Clean O(N) alternative to attention with solid theoretical grounding
- GPU-free inference is a genuine advantage for deployment
- Adaptive computation is elegant and functional
- Architecture is modular and well-documented
- Cross-pollination with FluidWorld validates PDE approach for different modalities

### Weaknesses
- Not yet competitive with Transformers on perplexity
- Only tested on TinyStories (28MB) - needs larger corpora
- Forward Euler is first-order (may limit quality ceiling)
- 44M params is too small to draw scaling conclusions
- Loss plateau at ~10.8 may indicate architectural ceiling

### Unknown
- Scaling laws (does FluidLM scale like Transformers with more params/data?)
- Quality ceiling (is PDE inherently less expressive than attention?)
- Whether Selective SSM (V4.5.0) breaks through the loss plateau

---

## Next Steps / Roadmap

### Priority 1 - Validation
- [ ] Compare perplexity to same-size Transformer on TinyStories
- [ ] Train on larger corpus (OpenWebText, ~40GB)
- [ ] Confirm V4.5.0 breaks through loss plateau
- [ ] Formal proof: adaptive compute correlates with input difficulty

### Priority 2 - Scaling
- [ ] 100M and 300M parameter variants
- [ ] Needle-in-Haystack test at 4K/16K/64K context
- [ ] Establish scaling laws (loss vs params, loss vs compute)

### Priority 3 - Architecture
- [ ] Persistent h-state across segments (cross-document memory)
- [ ] Extended dilations [1, 4, 16, 64, 256, 1024]
- [ ] RK4 integrator (higher-order, more stable)
- [ ] Adjoint backprop for VRAM reduction

### Priority 4 - Deployment
- [ ] ONNX export + INT8 quantization
- [ ] Rust inference engine (~5MB binary)
- [ ] Multi-platform: ARM, CoreML, OpenVINO, WASM
- [ ] Benchmark CPU inference latency vs Transformer

### Priority 5 - Cross-Domain
- [ ] Apply FluidLM architecture to code generation
- [ ] Explore connection to EG (001): can entropy-gated plasticity improve FluidLM training?
- [ ] FluidLM + FluidWorld: unified PDE foundation for language + vision
