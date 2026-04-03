---
purpose: Research ideas backlog - raw ideas to explore in the future
last_updated: 2026-04-03
---

# Research TODO

> Write raw ideas here. An agent can read this to find the next thing to work on.
> Format: `- [ ] idea` (unchecked) or `- [x] idea` (done/started)

---

## High Priority

- [ ] Multi-resolution fixed-point substrate (multigrid 8x8 -> 16x16 -> 32x32) for CIFAR-10
- [ ] Spatial Hebbian for EG conv layers - patch-level correlation instead of channel-average
- [ ] Benchmark FluidVLA on LIBERO manipulation tasks
- [ ] Benchmark FluidLM perplexity on WikiText-103

## Ideas to Explore

- [ ] Can entropy-gated plasticity replace softmax attention in transformers?
- [ ] EG + spiking networks - entropy of spike rates as plasticity gate (neuromorphic hardware)
- [ ] Fixed-Point Substrate as world model - can the medium learn environment dynamics?
- [ ] Combine FPS (002) with Entropy-Gated (001) - FPS medium + EG learning rule
- [ ] LVS theory applied to quantum error correction - fixed points in code space
- [ ] Post-quantum lattice cryptography - can fixed-point iteration break/strengthen lattice problems?
- [ ] Information-theoretic bounds on local learning - what is the maximum accuracy without backprop?
- [ ] Distributed local learning - no gradient sync across GPUs, each GPU runs EG independently
- [ ] Can the fixed-point substrate paradigm work for NLP? Text as 1D spatial medium?
- [ ] Thermodynamic computing hardware - EG/FPS on analog chips

## Speculative / Long-term

- [ ] Unified theory: LVS fixed-points + entropy gating + world models = general intelligence?
- [ ] Biological validation: does the brain actually use entropy-gated plasticity?
- [ ] Quantum fixed-point substrate - quantum medium finding quantum equilibrium
- [ ] Category theory formalization of the fixed-point learning paradigm

## Done / Started

- [x] Entropy-Gated Learning V1-V4 on MNIST (97.46%) -> solution 001
- [x] Fixed-Point Substrate on MNIST/F-MNIST/CIFAR-10 (96.44%) -> solution 002
- [x] CIFAR-10 attempts for both EG and FPS -> open challenge
