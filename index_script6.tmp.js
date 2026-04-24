
// ============================================================
// DATA MODEL
// Metrics are flexible: accuracy, perplexity, success_rate, FID, etc.
// type: classifier | vla | vlm | llm | world-model | learning-rule
// ============================================================

const DOMAINS = ['ml','physics','quantum','cybersec','robotics','neuro','math'];
const CATEGORIES = ['local-learning','gradient-free','physics-inspired','hybrid','novel-arch','transformer-alt','neuromorphic','efficiency','vla','vlm','llm','world-model','crypto','quantum-algo'];
const TYPES = ['learning-rule','classifier','vla','vlm','llm','world-model','encoder','generator','theory','crypto-scheme','quantum-circuit'];

// TODO items (parsed from todo.md structure)
const TODOS = [
  {text:'Multi-resolution fixed-point substrate (multigrid) for CIFAR-10',done:false,priority:'high'},
  {text:'Spatial Hebbian for EG conv layers - patch-level correlation',done:false,priority:'high'},
  {text:'Benchmark FluidVLA on LIBERO manipulation tasks',done:false,priority:'high'},
  {text:'Benchmark FluidLM perplexity on WikiText-103',done:false,priority:'high'},
  {text:'Can entropy-gated plasticity replace softmax attention in transformers-',done:false,priority:'idea'},
  {text:'EG + spiking networks - entropy of spike rates (neuromorphic HW)',done:false,priority:'idea'},
  {text:'Fixed-Point Substrate as world model - learn environment dynamics',done:false,priority:'idea'},
  {text:'Combine FPS (002) with EG (001) - FPS medium + EG learning rule',done:false,priority:'idea'},
  {text:'LVS theory applied to quantum error correction',done:false,priority:'idea'},
  {text:'Post-quantum lattice crypto - fixed-point iteration on lattices',done:false,priority:'idea'},
  {text:'Information-theoretic bounds on local learning',done:false,priority:'idea'},
  {text:'Distributed local learning - no gradient sync across GPUs',done:false,priority:'idea'},
  {text:'Unified theory: LVS + entropy gating + world models',done:false,priority:'speculative'},
  {text:'Quantum fixed-point substrate',done:false,priority:'speculative'},
  {text:'Entropy-Gated Learning V1-V4 on MNIST (97.46%) -> solution 001',done:true,priority:'done'},
  {text:'Fixed-Point Substrate on MNIST/F-MNIST/CIFAR-10 (96.44%) -> solution 002',done:true,priority:'done'},
  {text:'CIFAR-10 attempts for both EG and FPS -> open challenge',done:true,priority:'done'},
];

const SOLUTIONS = [
  {id:'001',name:'Entropy-Gated Learning',abbr:'EG',category:'local-learning',type:'learning-rule',
   status:'breakthrough',date:'2026-04-03',
   domains:['ml','neuro'],
   arxiv:null, paperStatus:'draft',
   crossRefs:{builds_on:[],enables:['F01'],related_to:['002']},
   github:null,
   principle:'Plasticity gated by local entropy. High entropy = learn, low entropy = stabilize. No backprop in feature layers.',
   nextStep:'Spatial Hebbian for Conv layers',
   bestResults:{MNIST:{metric:'accuracy',value:97.46,unit:'%'},['CIFAR-10']:{metric:'accuracy',value:48.22,unit:'%'}},
   params:{total:700000,local:680000,probe:20000},
   equation:{
     latex:'\\Delta W_i = \\sigma\\bigl(5(H_i - 0.4)\\bigr) \\cdot \\bigl(0.50\\,R + 0.25\\,D + 0.25\\,S\\bigr)',
     components:[
       {symbol:'H_i',desc:'Per-neuron binary entropy',latex:'H_i = -\\frac{1}{B}\\sum_b\\bigl[y\\log y + (1-y)\\log(1-y)\\bigr]'},
       {symbol:'R',desc:'Reconstruction gradient',latex:'R = y^\\top(x - yW)/B'},
       {symbol:'D',desc:'Decorrelation',latex:'D = -(C_{\\text{offdiag}} \\cdot W)'},
       {symbol:'S',desc:'Sparsity',latex:'S = -(\\bar{y} - \\tau)W'},
     ],
     code:`# Per neuron i:
H_i = -(y * log(y) + (1-y) * log(1-y)).mean(0)   # entropy
plasticity = sigmoid(5 * (H_i - 0.4))              # gate

recon  = y.T @ (x - y @ W) / B        # reconstruction
decorr = -(corr_offdiag @ W)           # decorrelation
sparse = -(mean_act - 0.12) * W        # sparsity

dW = plasticity * (0.50*recon + 0.25*decorr + 0.25*sparse)
momentum = 0.9 * momentum + dW
W += cosine_lr(step) * momentum`
   },
   versions:[
     {v:'V1',arch:'2L [500,500]+linear',acc:86.85,dataset:'MNIST',ep:5,stable:true,change:'First entropy-gated',status:'breakthrough'},
     {v:'V2-EG',arch:'3L [600x2,300]+linear',acc:87.91,dataset:'MNIST',ep:20,stable:true,change:'Kaiming init, adaptive LR',status:'promising'},
     {v:'V2-NTSO',arch:'3L [600x2,300]+linear',acc:88.90,dataset:'MNIST',ep:'6->NaN',stable:false,change:'Multi-signal plasticity',status:'failed'},
     {v:'Hybrid',arch:'4L [700x3,350]+linear',acc:86.07,dataset:'MNIST',ep:'6->decline',stable:false,change:'EG+NTSO combined',status:'failed'},
     {v:'V3',arch:'2L [500,300]+linear',acc:92.81,dataset:'MNIST',ep:50,stable:true,change:'no_grad, momentum, cosine LR',status:'breakthrough'},
     {v:'V4',arch:'2L [700,400]+MLP',acc:97.46,dataset:'MNIST',ep:89,stable:true,change:'Wider, MLP probe, chunked decorr',status:'breakthrough'},
     {v:'V4+aug',arch:'2L [700,400]+MLP+aug',acc:95.98,dataset:'MNIST',ep:100,stable:true,change:'Data augmentation hurts',status:'limited'},
     {v:'Conv V1',arch:'Conv sigmoid',acc:10.00,dataset:'CIFAR-10',ep:4,stable:true,change:'Sigmoid kills conv',status:'failed'},
     {v:'Conv V2',arch:'Conv ReLU+LocalBN',acc:48.22,dataset:'CIFAR-10',ep:6,stable:true,change:'Channel-avg Hebbian',status:'limited'},
     {v:'MLP',arch:'Dense(3072->500)',acc:41.16,dataset:'CIFAR-10',ep:80,stable:true,change:'No spatial bias',status:'limited'},
   ],
  },
  {id:'P01',name:'LVS Theory',abbr:'LVS',category:'physics-inspired',type:'theory',
   status:'limited',date:'2024 / 2026-04-24',
   domains:['physics','math'],
   arxiv:null, paperStatus:'preprint',
   crossRefs:{builds_on:[],enables:['002'],related_to:['001']},
   github:null,
   principle:'Observable reality = fixed points of the quantum vacuum. After 2026-04 methodological reset: the strong "global RG-flow minimization" form is FALSIFIED (predicted alpha_s(M_Z)=0.048 vs measured 0.1179). The Planck-scale boundary-condition form survives as a CONDITIONAL deduction: f_g~0.010, f_y~0.013. Eichhorn-Held FRG gives f_g~0.055, f_y~0.004 - factor 3-5 mismatch, within ~60% truncation uncertainty.',
   nextStep:'SARAH/RGBeta 2-loop validation + Eichhorn-Held literature audit + joint gauge-Yukawa treatment',
   bestResults:{'GlobalFlow':{metric:'verdict',value:'falsified',unit:''},'PlanckBC_fg':{metric:'f_g',value:0.010,unit:' (required)'},'PlanckBC_fy':{metric:'f_y',value:0.013,unit:' (required)'}},
   params:null,
   equation:{
     latex:'f_g \\equiv \\frac{\\partial_t g_*}{g_*}\\bigg|_{M_{Pl}} \\approx 10^{-2}, \\quad f_y \\equiv \\frac{\\partial_t y_*}{y_*}\\bigg|_{M_{Pl}} \\approx 10^{-2}',
     components:[
       {symbol:'f_g, f_y',desc:'Stationarity fractions at Planck scale (LVS boundary condition)'},
       {symbol:'\\partial_t',desc:'RG time derivative t = log(mu/M_Pl)'},
       {symbol:'\\text{FRG}',desc:'Eichhorn-Held 2018: f_g~0.055, f_y~0.004 (within ~60% truncation uncertainty)'},
       {symbol:'|\\psi(t)\\rangle_S = C\\langle t|\\Psi\\rangle',desc:'Page-Wootters: time emergence from static state (framework-level)'},
     ],
     code:`# LVS 2026-04 rigorous status\n# ---------------------------\n# Strong form (global flow min) -> FALSIFIED\n#   min int sum(beta_i^2) dt over alpha_s(M_Z) gives 0.048, not 0.1179.\n# Weak form (Planck-BC) -> CONDITIONAL deduction\n#   Requires f_g ~ 0.010, f_y ~ 0.013 (dimensional, non-distinctive).\n# FRG comparison (Eichhorn-Held 2018):\n#   f_g ~ 0.055, f_y ~ 0.004  -> factor 3-5 mismatch\n#   Within ~60% truncation uncertainty => not confirmed, not refuted.\n\nALPHA_S_OPT_GLOBAL_FLOW = 0.048   # Falsification point\nALPHA_S_MEASURED        = 0.1179\nLVS_FG_REQUIRED = 0.010\nLVS_FY_REQUIRED = 0.013\nEH_FG = 0.055\nEH_FY = 0.004\nFRG_TRUNCATION_UNCERTAINTY = 0.60`
   },
   versions:[
     {v:'Spark',arch:'Photon question',acc:0,dataset:'-',ep:'-',stable:true,change:'ds^2=0 for photon -> atemporality insight',status:'promising'},
     {v:'Paper v1',arch:'13-section paper',acc:6,dataset:'Validation (6/9)',ep:'-',stable:true,change:'Framework formalized: AS + PW + CW synthesis',status:'promising'},
     {v:'Validation v1',arch:'9-test scorecard',acc:6,dataset:'Multi-physics',ep:'-',stable:true,change:'6 confirmed - later recognized as minimum bar (no discriminative power)',status:'limited'},
     {v:'Formalization',arch:'RG + fixed-point',acc:126,dataset:'Higgs (GeV)',ep:'-',stable:true,change:'Shaposhnikov-Wetterich m_H=126 GeV (pre-existing result, not LVS-specific)',status:'promising'},
     {v:'Self-critique',arch:'Honest assessment',acc:0,dataset:'-',ep:'-',stable:true,change:'Acknowledged: not falsifiable beyond SM yet',status:'limited'},
     {v:'v3 Reformulation',arch:'Network of interactions',acc:0,dataset:'-',ep:'-',stable:true,change:'Mass=frequency, gravity=desync, dark energy=latent space',status:'promising'},
     {v:'Essay FR',arch:'20-chapter journal',acc:0,dataset:'-',ep:'-',stable:true,change:'Du Point Fixe au Point de Rupture (56K chars)',status:'promising'},
     {v:'GPU sims (2026-03)',arch:'d=3 / SU321 / DESI',acc:0,dataset:'Tuned simulations',ep:'-',stable:true,change:'Retrospectively recognized as tuned, not predictive - archived under biased explorations',status:'failed'},
     {v:'50% partial-LVS',arch:'sigma2 relative metric',acc:0,dataset:'-',ep:'-',stable:true,change:'Claimed optimum at 50% flattening - retracted after 3-metric robustness test',status:'failed'},
     {v:'Global flow min',arch:'min int sum(beta^2) dt',acc:0.048,dataset:'alpha_s(M_Z)',ep:'-',stable:true,change:'Strong LVS form. FALSIFIED: min at 0.048 vs measured 0.1179',status:'failed'},
     {v:'Planck-BC (rigorous)',arch:'f_g, f_y at M_Pl',acc:0.010,dataset:'f_g required',ep:'-',stable:true,change:'Conditional deduction: f_g~0.010, f_y~0.013. To be compared against FRG.',status:'promising'},
     {v:'Eichhorn-Held audit',arch:'FRG comparison',acc:0,dataset:'f_g=0.055, f_y=0.004',ep:'-',stable:true,change:'Factor 3-5 mismatch within 60% truncation uncertainty. Not confirmed, not refuted.',status:'limited'},
     {v:'Robustness test',arch:'sigma1/sigma2/sigma3',acc:0,dataset:'-',ep:'-',stable:true,change:'3 stationarity metrics agree - 50% optimum was a metric artifact',status:'promising'},
     {v:'Paper (rigorous)',arch:'LVS as conditional framework',acc:0,dataset:'Preprint',ep:'-',stable:true,change:'paper/lvs-preprint.md: honest, negative-result-aware rigorous paper',status:'promising'},
   ],
  },
  {id:'P02',name:'RAPC Modular Geometry',abbr:'RAPC',category:'physics-inspired',type:'theory',
   status:'wip',date:'2026-04-24',
   domains:['physics','quantum','math'],
   arxiv:null, paperStatus:'draft',
   crossRefs:{builds_on:['P01'],enables:[],related_to:['002','F03']},
   github:null,
   principle:'Geometry may be the stable sparse spectral compression of modular quantum correlations. ML/GPU is used as a research microscope only, not as a physical law.',
   nextStep:'Multi-scale bridge rule + wider phase diagram scan',
   bestResults:{'SparseGeometry':{metric:'stable_geo',value:9,unit:'/20 seeds'},'BMVGate':{metric:'concurrence',value:0.105,unit:''}},
   params:{nodes:6,seedsPerLambda:20,bestLambda:'0.08-0.20'},
   equation:{
     latex:'S(G)=I(G)-\lambda |E|-c(N_c-1)+\nu\lambda_2(L_G)-\mu\mathrm{Var}(d)',
     components:[
       {symbol:'I(G)',desc:'Preserved modular coupling weight'},
       {symbol:'|E|',desc:'Graph complexity / edge count'},
       {symbol:'N_c',desc:'Connected component count'},
       {symbol:'\lambda_2(L_G)',desc:'Algebraic connectivity of graph Laplacian'},
       {symbol:'\mathrm{Var}(d)',desc:'Degree variance locality penalty'},
     ],
     code:`score = information
score -= lambda_edges * edge_count
score -= disconnect_cost * (components - 1)
score += nu_gap * algebraic_connectivity
score -= mu_degree * degree_variance`
   },
   versions:[
     {v:'G1',arch:'BMV finite channel',acc:0.105,dataset:'Two-qubit toy',ep:'-',stable:true,change:'Bilocal phase entangles; LOCC does not',status:'promising'},
     {v:'G2',arch:'Modular phase',acc:0.644,dataset:'Two-qubit rho',ep:'-',stable:true,change:'K=-log(rho) yields bilocal ZZ generator',status:'promising'},
     {v:'G4',arch:'Hypergraph coarse-grain',acc:0.177,dataset:'3-node toy',ep:'-',stable:true,change:'Biased hidden node yields effective pair coefficient',status:'promising'},
     {v:'G9',arch:'Simple MDL phase scan',acc:6,dataset:'20 seeds/lambda',ep:6,stable:true,change:'Sparse geometric phase exists but narrow',status:'limited'},
     {v:'G10',arch:'Spectral locality scan',acc:9,dataset:'20 seeds/lambda',ep:6,stable:true,change:'Sparse geometric phase widened across lambda range',status:'promising'},
     {v:'G11',arch:'Patch gluing',acc:0,dataset:'20 seeds/lambda',ep:6,stable:true,change:'No bridge edges added',status:'failed'},
     {v:'G12',arch:'Residual patch gluing',acc:9,dataset:'20 seeds/lambda',ep:6,stable:true,change:'Stable 9/20 but still no bridges',status:'limited'},
   ],
  },
  {id:'002',name:'Fixed-Point Substrate',abbr:'FPS',category:'physics-inspired',type:'learning-rule',
   status:'promising',date:'2026-04-03',
   domains:['ml','physics'],
   arxiv:null, paperStatus:'draft',
   crossRefs:{builds_on:['P01'],enables:['F02'],related_to:['001']},
   github:null,
   principle:'Intelligence emerges from fixed points in a learnable medium. Input perturbs the medium, which collapses to equilibrium Z*=f(Z*). Zero backprop, constant memory. Inspired by LVS theory: It from Fix.',
   nextStep:'Multi-resolution substrate for CIFAR-10',
   bestResults:{MNIST:{metric:'accuracy',value:96.44,unit:'%'},['Fashion-MNIST']:{metric:'accuracy',value:77.15,unit:'%'},['CIFAR-10']:{metric:'accuracy',value:42.24,unit:'%'}},
   params:{total:2799210,local:2799210,probe:0},
   equation:{
     latex:'Z^* = \\tanh\\bigl(\\sum_s \\kappa_s \\nabla^2_s Z^* + W_{\\text{mix}} Z^* + \\alpha X + \\beta\\bigr)',
     components:[
       {symbol:'\\kappa_s',desc:'Multi-scale conductivity (3x3, 5x5, 7x7)',latex:'\\kappa_s(x) \\in \\mathbb{R}^{C \\times H \\times W}'},
       {symbol:'\\nabla^2_s',desc:'Discrete Laplacian at scale s',latex:'\\nabla^2_s Z = \\text{Conv2d}(Z, \\text{lap}_s)'},
       {symbol:'\\alpha',desc:'Input coupling strength',latex:'\\alpha(x) \\in \\mathbb{R}^{C \\times H \\times W}'},
       {symbol:'\\text{gate}',desc:'Entropy gate for learning',latex:'g_i = \\sigma(H_{\\text{local},i} + 0.5)'},
     ],
     code:`# Fixed-point iteration (7 iters with Anderson acceleration):
Z = tanh(kappa_3*Lap3(Z) + kappa_5*Lap5(Z) + kappa_7*Lap7(Z)
         + 0.5*W_mix@Z + alpha*X_proj + beta)

# Learning (all local, no backprop):
gate = sigmoid(H_local + 0.5)
dkappa = lr * gate * (Z * error)        # Hebbian
dalpha = lr * gate * (X_proj * error)   # input correlation
dW_mix = lr * (Z_avg.T @ err_avg) / B  # channel Hebbian`
   },
   versions:[
     {v:'v0.1',arch:'PDE temporal 48ch',acc:9.80,dataset:'MNIST',ep:5,stable:true,change:'Initial PDE approach',status:'failed'},
     {v:'v0.2',arch:'PDE + global pool',acc:19.80,dataset:'MNIST',ep:10,stable:true,change:'Better readout, still temporal',status:'limited'},
     {v:'v0.4a',arch:'Fixed-point 4x4 48ch',acc:76.20,dataset:'MNIST',ep:40,stable:true,change:'Paradigm shift to Z*=f(Z*)',status:'promising'},
     {v:'v0.4b',arch:'+ 7x7 regions + var',acc:85.18,dataset:'MNIST',ep:40,stable:true,change:'Regional variance readout',status:'promising'},
     {v:'v0.4c',arch:'+ spatial filters 64ch',acc:92.73,dataset:'MNIST',ep:40,stable:true,change:'Learnable retinal filters',status:'promising'},
     {v:'v0.5',arch:'96ch multi-Lap Anderson 2L',acc:96.44,dataset:'MNIST',ep:50,stable:true,change:'All levers engaged',status:'breakthrough'},
     {v:'v0.5',arch:'96ch 256h 7x7',acc:77.15,dataset:'Fashion-MNIST',ep:50,stable:true,change:'Fashion-MNIST benchmark',status:'promising'},
     {v:'v0.5',arch:'96ch 384h 8x8',acc:42.24,dataset:'CIFAR-10',ep:60,stable:true,change:'CIFAR-10 benchmark',status:'limited'},
   ],
  },
  {id:'F01',name:'FluidVLA',abbr:'FVLA',category:'vla',type:'vla',
   status:'wip',date:'2025',
   domains:['ml','robotics'],
   arxiv:null, paperStatus:'none',
   crossRefs:{builds_on:['001','002'],enables:[],related_to:['F02']},
   github:'https://github.com/infinition/FluidVLA',
   principle:'Vision-Language-Action model for robotic manipulation. End-to-end from pixels + language to actions.',
   nextStep:'Integration with local learning features',
   bestResults:{},
   equation:{latex:'a_t = \\pi_\\theta(o_t, l)',code:'# VLA: observation + language -> action\n# See FluidVLA repo for full architecture'},
   versions:[],
  },
  {id:'F02',name:'FluidWorld',abbr:'FW',category:'world-model',type:'world-model',
   status:'wip',date:'2025',
   domains:['ml','robotics'],
   arxiv:null, paperStatus:'none',
   crossRefs:{builds_on:['002'],enables:[],related_to:['F01']},
   github:'https://github.com/infinition/FluidWorld',
   principle:'World model for learning environment dynamics. Predicts future states from current state + action.',
   nextStep:'Benchmark on standard simulation tasks',
   bestResults:{},
   equation:{latex:'\\hat{s}_{t+1} = f_\\theta(s_t, a_t)',code:'# World Model: state + action -> next state\n# See FluidWorld repo for architecture'},
   versions:[],
  },
  {id:'F03',name:'FluidLM',abbr:'FLM',category:'transformer-alt',type:'llm',
   status:'promising',date:'2025',
   domains:['ml'],
   arxiv:null, paperStatus:'submitted',
   crossRefs:{builds_on:['P01'],enables:[],related_to:['F02','002']},
   github:'https://github.com/infinition/FluidLM',
   principle:'Transformer-free LM: O(N^2) attention replaced by O(N) reaction-diffusion PDEs. Tokens = concentrations, multi-scale diffusion + Mamba SSM + SwiGLU. Zero KV-cache, GPU-free inference, adaptive computation. 44.2M params, V4.5.0.',
   nextStep:'Scaling to 100M+ params, compare perplexity vs Transformer',
   bestResults:{'TinyStories':{metric:'loss',value:10.76,unit:''}},
   params:{total:44200000,core:18500000,embedding:25700000},
   equation:{
     latex:'\\frac{du}{dt} = \\sum_k D_k \\nabla^2 u + \\text{SSM}(u) + \\text{SwiGLU}(u) + \\alpha h',
     components:[
       {symbol:'D_k \\nabla^2 u',desc:'Multi-scale diffusion (dilations 1, 4, 16)'},
       {symbol:'\\text{SSM}(u)',desc:'Selective State Space (Mamba): content-based routing'},
       {symbol:'\\text{SwiGLU}(u)',desc:'Nonlinear reaction (8/3 expansion)'},
       {symbol:'\\alpha h',desc:'Global memory pump (B,D), O(1) constant memory'},
       {symbol:'\\text{turb} < \\epsilon \\Rightarrow \\text{HALT}',desc:'Adaptive computation (~30% savings)'},
     ],
     code:`# FluidLM V4.5.0 - PDE Language Model\n# Forward Euler integration:\nu_next = RMSNorm(u + dt * (\n    multi_scale_diffusion(u) +  # O(N) spatial coherence\n    selective_ssm(u) +           # Content-based routing\n    swiglu(u) +                  # Semantic reaction\n    alpha * h +                  # Global memory\n    alpha_local * local_mem      # Local context\n))\n# Halt when turbulence < epsilon (~30% compute saved)`
   },
   versions:[
     {v:'V4.2',arch:'PoC: Euler+learned PE',acc:0,dataset:'TinyStories',ep:'-',stable:true,change:'Proof of concept',status:'promising'},
     {v:'V4.3',arch:'+RoPE +MLP 4x',acc:0,dataset:'TinyStories',ep:'-',stable:true,change:'Improved architecture',status:'promising'},
     {v:'V4.4.0',arch:'+LongConv +sinPE +mem(B,L,D)',acc:0,dataset:'TinyStories',ep:'-',stable:true,change:'Major upgrade',status:'promising'},
     {v:'V4.4.4-7',arch:'+ForgetGate +GradClip +LocalMem',acc:0,dataset:'TinyStories',ep:'-',stable:true,change:'Stability fixes',status:'promising'},
     {v:'V4.4.8',arch:'+LaplacianGradLoss +Curriculum',acc:0,dataset:'TinyStories',ep:'-',stable:true,change:'From FluidWorld cross-pollination',status:'promising'},
     {v:'V4.5.0',arch:'SwiGLU+Mamba+MultiHead+RMSNorm',acc:10.76,dataset:'TinyStories (loss)',ep:851,stable:true,change:'Current: loss 10.76',status:'promising'},
   ],
  },
  {id:'003', name:'Gradient-Free Reservoir Lab', abbr:'GFRL', category:'gradient-free', type:'learning-rule',
   status:'breakthrough', date:'2026-04-03',
   domains:['ml','neuro','math'],
   crossRefs:{builds_on:['001'], enables:['004'], related_to:['002']},
   principle:'Diverse random reservoir dynamics + stacking + closed-form readout achieves near-backprop accuracy with zero gradients.',
   nextStep:'Convolutional reservoir for CIFAR-10 (PyTorch)',
   bestResults:{MNIST:{metric:'accuracy',value:97.28,unit:'%'},'Fashion-MNIST':{metric:'accuracy',value:88.65,unit:'%'},'CIFAR-10':{metric:'accuracy',value:46.43,unit:'%'}},
   paperStatus:'draft',
   equation:{
     latex:'W_{out} = (H^T H + \\lambda I)^{-1} H^T Y',
     code:'W_out = solve(H.T @ H + lam * I, H.T @ Y)',
     components:[
       {symbol:'H',desc:'Concatenated states from 8 diverse reservoirs'},
       {symbol:'\\lambda',desc:'Ridge regularization (0.01)'},
       {symbol:'Y',desc:'One-hot target labels'},
     ]
   },
   versions:[
     {v:'ESN',arch:'1 reservoir (2000)',acc:92.3,dataset:'MNIST',ep:0,stable:true,change:'Single echo state network',status:'promising'},
     {v:'Mega',arch:'4 reservoirs + HD + entropy',acc:94.1,dataset:'MNIST',ep:0,stable:true,change:'Diversity matters!',status:'promising'},
     {v:'Ultra',arch:'8 reservoirs + 3 input reps + stacking',acc:97.28,dataset:'MNIST',ep:0,stable:true,change:'BEST: 8 diverse + meta-reservoir',status:'breakthrough'},
     {v:'Ultra-Fashion',arch:'Same, Fashion-MNIST',acc:88.65,dataset:'Fashion-MNIST',ep:0,stable:true,change:'Generalizes to clothing',status:'breakthrough'},
     {v:'Ultra-CIFAR',arch:'Same, CIFAR-10',acc:46.43,dataset:'CIFAR-10',ep:0,stable:true,change:'Needs spatial features',status:'limited'},
   ],
  },
  {id:'004', name:'NoProp-Reservoir', abbr:'NPR', category:'gradient-free', type:'learning-rule',
   status:'promising', date:'2026-04-03',
   domains:['ml','neuro'],
   crossRefs:{builds_on:['003'], enables:[], related_to:['001','002']},
   principle:'Chain of reservoir-based denoisers where each block trains independently in closed form. ORIGINAL INVENTION.',
   nextStep:'Fashion-MNIST (fix OOM) + PyTorch GPU impl',
   bestResults:{MNIST:{metric:'accuracy',value:95.04,unit:'%'}},
   paperStatus:'none',
   equation:{
     latex:'W_{out,b} = (H_b^T H_b + \\lambda I)^{-1} H_b^T y',
     code:'W_out_b = solve(H_b.T @ H_b + lam * I, H_b.T @ y)',
     components:[
       {symbol:'H_b',desc:'Reservoir state of block b (fixed random dynamics)'},
       {symbol:'b',desc:'Block index in denoising chain (1..8)'},
       {symbol:'\\sigma_b',desc:'Noise level (decreasing schedule)'},
     ]
   },
   versions:[
     {v:'V1',arch:'6 blocks, 1000-dim',acc:91.80,dataset:'MNIST',ep:0,stable:true,change:'Proof of concept',status:'promising'},
     {v:'V2',arch:'8 blocks, 1500-dim',acc:95.04,dataset:'MNIST',ep:0,stable:true,change:'Scaled up: +3.2%',status:'promising'},
   ],
  },
  {id:'005',name:'Direct Local Learning',abbr:'DLL',category:'local-learning',type:'learning-rule',
   status:'breakthrough',date:'2026-04-03',
   domains:['ml','neuro'],
   crossRefs:{builds_on:['001'],enables:[],related_to:['006','007','003']},
   principle:'Each layer has its own classifier probe and optimizer. Gradient NEVER flows between layers (h.detach()). 3.3x faster on CPU for deep nets.',
   nextStep:'GPT-2 scale language modeling',
   bestResults:{MNIST:{metric:'accuracy',value:98.15,unit:'%'},['CIFAR-10']:{metric:'accuracy',value:56.47,unit:'%'}},
   paperStatus:'draft',
   equation:{
     latex:'h = \\text{layer}(h);\\; \\mathcal{L} = \\text{CE}(\\text{probe}(h), y);\\; h \\leftarrow h.\\text{detach}()',
     code:`for layer, probe, opt in zip(layers, probes, optimizers):
    h = layer(h)                    # Forward local
    loss = CE(probe(h), y)          # Local loss
    loss.backward()                 # Gradient LOCAL only
    opt.step()
    h = h.detach()                  # CUT gradient`,
     components:[
       {symbol:'\\text{probe}',desc:'Per-layer MLP classifier (128 hidden)',latex:'\\text{probe}_l: \\mathbb{R}^{d_l} \\to \\mathbb{R}^C'},
       {symbol:'h.\\text{detach}()',desc:'Cuts gradient flow between layers'},
       {symbol:'\\text{BN}',desc:'BatchNorm per layer (local normalization)'},
     ]
   },
   versions:[
     {v:'V1',arch:'MLP [500,300]+linear probe',acc:97.71,dataset:'MNIST',ep:10,stable:true,change:'First DirectLocal',status:'breakthrough'},
     {v:'V1-20ep',arch:'same, 20 epochs',acc:97.94,dataset:'MNIST',ep:20,stable:true,change:'More training',status:'breakthrough'},
     {v:'V2',arch:'MLP probe+dropout',acc:98.15,dataset:'MNIST',ep:20,stable:true,change:'BEST: MLP probes',status:'breakthrough'},
     {v:'V2-CIFAR',arch:'[2000,1000,500]+MLP probe',acc:56.47,dataset:'CIFAR-10',ep:20,stable:true,change:'Beats BP on CIFAR-10!',status:'breakthrough'},
     {v:'V2-Deep',arch:'[1000,500,300,100]',acc:98.01,dataset:'MNIST',ep:15,stable:true,change:'5-layer deep',status:'breakthrough'},
     {v:'V2-TF-4',arch:'ViT 4 blocks d=64',acc:96.21,dataset:'MNIST',ep:15,stable:true,change:'Transformer works!',status:'promising'},
     {v:'V2-TF-8',arch:'ViT 8 blocks d=64',acc:96.22,dataset:'MNIST',ep:15,stable:true,change:'Deep Transformer',status:'promising'},
   ],
  },
  {id:'006',name:'NoProp Diffusion',abbr:'NPD',category:'local-learning',type:'learning-rule',
   status:'breakthrough',date:'2026-04-03',
   domains:['ml','neuro'],
   crossRefs:{builds_on:['004'],enables:[],related_to:['005','007']},
   principle:'Each block independently denoises a noisy label embedding. No global forward OR backward pass. From DeepMind (arXiv:2503.24322, March 2025).',
   nextStep:'Full flow-matching impl + CIFAR-10',
   bestResults:{MNIST:{metric:'accuracy',value:97.89,unit:'%'}},
   paperStatus:'draft',
   equation:{
     latex:'z_{\\text{pred}} = \\text{block}(\\text{features}, z_{\\text{noisy}}, t);\\; \\mathcal{L} = \\|z_{\\text{pred}} - z_0\\|^2',
     code:`t = rand(0, 1)  # noise level
z_noisy = cos(t*pi/2) * z_clean + sin(t*pi/2) * noise
z_pred = block(features, z_noisy, t)
loss = MSE(z_pred, z_clean) + CE(proj(z_pred), y)`,
     components:[
       {symbol:'z_0',desc:'Clean label embedding'},
       {symbol:'t',desc:'Noise level in [0,1], cosine schedule'},
       {symbol:'\\text{block}',desc:'Independent denoiser (MLP)'},
     ]
   },
   versions:[
     {v:'V1',arch:'4 blocks, hidden=256, label_dim=32',acc:97.89,dataset:'MNIST',ep:15,stable:true,change:'First implementation',status:'breakthrough'},
   ],
  },
  {id:'007',name:'Mono-Forward',abbr:'MF',category:'local-learning',type:'learning-rule',
   status:'breakthrough',date:'2026-04-03',
   domains:['ml','neuro'],
   crossRefs:{builds_on:[],enables:[],related_to:['005','006']},
   principle:'Each layer classifies via learned projection matrix M. Simplest local learning rule. Paper (arXiv:2501.09238) reports BEATING backprop on CIFAR-10.',
   nextStep:'CNN version to reproduce CIFAR-10 result',
   bestResults:{MNIST:{metric:'accuracy',value:98.12,unit:'%'}},
   paperStatus:'draft',
   equation:{
     latex:'G = h \\cdot M^T;\\; \\mathcal{L} = \\text{CE}(G, y)',
     code:`h = relu(bn(linear(x_norm)))  # Forward
logits = M(h)                  # Project to classes
loss = CE(logits, y)           # Local loss
h = h.detach()                 # CUT`,
     components:[
       {symbol:'M',desc:'Per-layer projection matrix (out_dim x n_classes)'},
       {symbol:'G',desc:'Goodness: per-class activation scores'},
       {symbol:'x_{\\text{norm}}',desc:'Input normalized by L2 norm'},
     ]
   },
   versions:[
     {v:'V1',arch:'MLP [500,300], lr=0.01',acc:97.95,dataset:'MNIST',ep:15,stable:true,change:'First implementation',status:'breakthrough'},
     {v:'V1-Wide',arch:'MLP [1000,500,200], lr=0.005',acc:98.12,dataset:'MNIST',ep:15,stable:true,change:'Wider = better',status:'breakthrough'},
   ],
  },
];

const EXPERIMENTS = [
  // sol: solution ID, solName: human-readable name shown in table
  {phase:1,sol:'-',solName:'Baseline',name:'Backprop Baseline',cat:'reference',type:'classifier',dataset:'MNIST',metric:'accuracy',val:98.04,unit:'%',ep:5,stable:true,verdict:'Reference'},
  {phase:6,sol:'001',solName:'Entropy-Gated',name:'Entropy-Gated V4',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:97.46,unit:'%',ep:100,stable:true,verdict:'Breakthrough'},
  {phase:6,sol:'001',solName:'Entropy-Gated',name:'EG V4 + augmentation',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:95.98,unit:'%',ep:100,stable:true,verdict:'Aug hurts'},
  {phase:5,sol:'001',solName:'Entropy-Gated',name:'Entropy-Gated V3',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:92.81,unit:'%',ep:50,stable:true,verdict:'Never plateaus'},
  {phase:4,sol:'001',solName:'Entropy-Gated',name:'NTSO V2',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:88.90,unit:'%',ep:20,stable:false,verdict:'Diverges ep19'},
  {phase:4,sol:'001',solName:'Entropy-Gated',name:'Entropy-Gated V2',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:87.91,unit:'%',ep:20,stable:true,verdict:'Still climbing'},
  {phase:3,sol:'001',solName:'Entropy-Gated',name:'Entropy-Gated V1',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:86.85,unit:'%',ep:5,stable:true,verdict:'First breakthrough'},
  {phase:4,sol:'001',solName:'Entropy-Gated',name:'EG+NTSO Hybrid',cat:'hybrid',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:86.07,unit:'%',ep:20,stable:false,verdict:'Worse than pure EG'},
  {phase:2,sol:'001',solName:'Entropy-Gated',name:'Reaction-Diffusion',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:11.35,unit:'%',ep:4,stable:true,verdict:'PDE dead-end'},
  {phase:3,sol:'001',solName:'Entropy-Gated',name:'Gradient-Free Contrastive',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:11.35,unit:'%',ep:5,stable:false,verdict:'Diverges'},
  {phase:1,sol:'001',solName:'Entropy-Gated',name:'Forward-Forward (Hinton)',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:9.80,unit:'%',ep:5,stable:false,verdict:'NaN'},
  {phase:3,sol:'001',solName:'Entropy-Gated',name:'Learning by Disagreement',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:9.80,unit:'%',ep:5,stable:false,verdict:'NaN'},
  {phase:3,sol:'001',solName:'Entropy-Gated',name:'Spectral Resonance',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:9.80,unit:'%',ep:5,stable:false,verdict:'NaN'},
  {phase:1,sol:'001',solName:'Entropy-Gated',name:'Predictive Coding',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:0,unit:'%',ep:0,stable:false,verdict:'Crashed'},
  {phase:1,sol:'001',solName:'Entropy-Gated',name:'Equilibrium Propagation',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:0,unit:'%',ep:0,stable:false,verdict:'Not completed'},
  {phase:1,sol:'001',solName:'Entropy-Gated',name:'InfoMax',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:0,unit:'%',ep:0,stable:false,verdict:'Not completed'},
  {phase:1,sol:'001',solName:'Entropy-Gated',name:'Competitive Hebbian',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:0,unit:'%',ep:0,stable:false,verdict:'Not completed'},
  {phase:1,sol:'001',solName:'Entropy-Gated',name:'Diff Target Propagation',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:0,unit:'%',ep:0,stable:false,verdict:'Not completed'},
  {phase:2,sol:'001',solName:'Entropy-Gated',name:'Thermodynamic Free Energy',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:0,unit:'%',ep:0,stable:false,verdict:'Not completed'},
  {phase:2,sol:'001',solName:'Entropy-Gated',name:'Wave Interference',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:0,unit:'%',ep:0,stable:false,verdict:'Not completed'},
  {phase:2,sol:'001',solName:'Entropy-Gated',name:'Kuramoto Oscillators',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:0,unit:'%',ep:0,stable:false,verdict:'Not completed'},
  {phase:2,sol:'001',solName:'Entropy-Gated',name:'Gossip Protocol',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:0,unit:'%',ep:0,stable:false,verdict:'Not completed'},
  {phase:7,sol:'-',solName:'Baseline',name:'Backprop Conv',cat:'reference',type:'classifier',dataset:'CIFAR-10',metric:'accuracy',val:85.83,unit:'%',ep:100,stable:true,verdict:'Reference'},
  {phase:7,sol:'001',solName:'Entropy-Gated',name:'EG-Conv V2 (ReLU+BN)',cat:'local-learning',type:'learning-rule',dataset:'CIFAR-10',metric:'accuracy',val:48.22,unit:'%',ep:100,stable:true,verdict:'Limited'},
  {phase:7,sol:'001',solName:'Entropy-Gated',name:'EG-MLP (flatten)',cat:'local-learning',type:'learning-rule',dataset:'CIFAR-10',metric:'accuracy',val:41.16,unit:'%',ep:80,stable:true,verdict:'Limited'},
  {phase:7,sol:'001',solName:'Entropy-Gated',name:'EG-Conv V1 (Sigmoid)',cat:'local-learning',type:'learning-rule',dataset:'CIFAR-10',metric:'accuracy',val:10.00,unit:'%',ep:4,stable:true,verdict:'Dead-end'},
  // P02 - RAPC Modular Geometry
  {phase:1,sol:'P02',solName:'RAPC',name:'BMV finite channel',cat:'physics-inspired',type:'theory',dataset:'Two-qubit toy',metric:'concurrence',val:0.105,unit:'',ep:'-',stable:true,verdict:'Bilocal quantum channel entangles; LOCC controls do not'},
  {phase:2,sol:'P02',solName:'RAPC',name:'Modular phase extraction',cat:'physics-inspired',type:'theory',dataset:'Two-qubit rho',metric:'concurrence',val:0.644,unit:'',ep:'-',stable:true,verdict:'K=-log(rho) extracts bilocal ZZ generator'},
  {phase:4,sol:'P02',solName:'RAPC',name:'Hypergraph coarse-graining',cat:'physics-inspired',type:'theory',dataset:'3-node modular hyperedge',metric:'J_eff',val:0.177,unit:'',ep:'-',stable:true,verdict:'Reference-biased hidden node creates effective pair edge'},
  {phase:9,sol:'P02',solName:'RAPC',name:'Simple MDL phase scan',cat:'physics-inspired',type:'theory',dataset:'Random modular hypergraphs',metric:'sparse_geometric',val:6,unit:'/20',ep:6,stable:true,verdict:'Sparse geometry exists but phase is narrow'},
  {phase:10,sol:'P02',solName:'RAPC',name:'Spectral-locality phase scan',cat:'physics-inspired',type:'theory',dataset:'Random modular hypergraphs',metric:'sparse_geometric',val:9,unit:'/20',ep:6,stable:true,verdict:'Best current result: locality prior widens geometric phase'},
  {phase:11,sol:'P02',solName:'RAPC',name:'Patch gluing scan',cat:'physics-inspired',type:'theory',dataset:'Random modular hypergraphs',metric:'bridges_added',val:0,unit:'',ep:6,stable:true,verdict:'Failed bridge rule: no bridges added'},
  {phase:12,sol:'P02',solName:'RAPC',name:'Residual patch gluing scan',cat:'physics-inspired',type:'theory',dataset:'Random modular hypergraphs',metric:'sparse_geometric',val:9,unit:'/20',ep:6,stable:true,verdict:'Stable 9/20 but still no bridge generation'},
  // 002 - Fixed-Point Substrate
  // P01 - LVS Theory
  // P01 LVS Theory - all computational/validation experiments
  // Early "validation" phase (2024-2026-Q1) - kept for provenance, reinterpreted as minimum-bar / non-discriminative
  {phase:0,sol:'P01',solName:'LVS Theory',name:'9-test empirical validation (v1, reinterpreted)',cat:'physics-inspired',type:'theory',dataset:'Multi-physics',metric:'tests_confirmed',val:6,unit:'/9',ep:'-',stable:true,verdict:'Minimum-bar - no discriminative power (2026-04 audit)'},
  {phase:0,sol:'P01',solName:'LVS Theory',name:'Higgs mass (Shaposhnikov-Wetterich)',cat:'physics-inspired',type:'theory',dataset:'LHC',metric:'prediction',val:126,unit:' GeV',ep:'-',stable:true,verdict:'Pre-existing SW result (2009) - not LVS-specific'},
  {phase:0,sol:'P01',solName:'LVS Theory',name:'Hadron mass fit (lattice QCD)',cat:'physics-inspired',type:'theory',dataset:'PDG',metric:'R2',val:99.9998,unit:'%',ep:'-',stable:true,verdict:'Correlational fit - not a prediction'},
  {phase:0,sol:'P01',solName:'LVS Theory',name:'Top quark quasi-fixed-point',cat:'physics-inspired',type:'theory',dataset:'Tevatron/LHC',metric:'deviation',val:97.3,unit:'%',ep:'-',stable:true,verdict:'y_t^2 ~ (8/9)g_3^2 (Pendleton-Ross 1981) - not LVS-specific'},
  {phase:0,sol:'P01',solName:'LVS Theory',name:'Lambda prediction (Fisher-KPP)',cat:'physics-inspired',type:'theory',dataset:'Cosmology',metric:'ratio',val:1.08,unit:'x',ep:'-',stable:true,verdict:'Tautological - equals Friedmann. Dead end.'},
  {phase:0,sol:'P01',solName:'LVS Theory',name:'d=3 uniqueness analysis',cat:'physics-inspired',type:'theory',dataset:'Theory',metric:'constraints',val:4,unit:'/4',ep:'-',stable:true,verdict:'Ehrenfest+quantum+Huygens+knots all select d=3 - not LVS-specific'},
  {phase:0,sol:'P01',solName:'LVS Theory',name:'Page-Wootters simulation (32-level)',cat:'physics-inspired',type:'theory',dataset:'Simulation',metric:'emergence',val:100,unit:'%',ep:'-',stable:true,verdict:'Reproduces Page-Wootters 1983 - framework illustration, not prediction'},
  // Rigorous phase (2026-04) - methodological reset
  {phase:12,sol:'P01',solName:'LVS Theory',name:'Global RG-flow minimization (strong LVS)',cat:'physics-inspired',type:'theory',dataset:'SM 1-loop RGE',metric:'alpha_s_opt',val:0.048,unit:'',ep:'-',stable:true,verdict:'FALSIFIED: opt=0.048 vs measured 0.1179'},
  {phase:12,sol:'P01',solName:'LVS Theory',name:'3-metric robustness (sigma1/sigma2/sigma3)',cat:'physics-inspired',type:'theory',dataset:'SM 1-loop RGE',metric:'agreement',val:3,unit:'/3',ep:'-',stable:true,verdict:'Passed: prior 50% optimum was a metric artifact - retracted'},
  {phase:12,sol:'P01',solName:'LVS Theory',name:'Planck-BC dimensional analysis',cat:'physics-inspired',type:'theory',dataset:'1-loop RGE',metric:'f_g_required',val:0.010,unit:'',ep:'-',stable:true,verdict:'Conditional deduction: f_g~0.010, f_y~0.013'},
  {phase:13,sol:'P01',solName:'LVS Theory',name:'Eichhorn-Held 2018 comparison (FRG)',cat:'physics-inspired',type:'theory',dataset:'arXiv:1707.01107',metric:'f_g_FRG',val:0.055,unit:'',ep:'-',stable:true,verdict:'Factor 3-5 mismatch, within ~60% truncation - not confirmed/not refuted'},
  {phase:13,sol:'P01',solName:'LVS Theory',name:'Yukawa residue at M_Pl',cat:'physics-inspired',type:'theory',dataset:'1-loop RGE',metric:'beta_yt',val:1,unit:' (nonzero)',ep:'-',stable:true,verdict:'beta_yt != 0 even when gauge beta vanishes - joint treatment required'},
  // F03 - FluidLM
  {phase:0,sol:'F03',solName:'FluidLM',name:'FluidLM V4.2 PoC',cat:'transformer-alt',type:'llm',dataset:'TinyStories',metric:'loss',val:0,unit:'',ep:'-',stable:true,verdict:'Proof of concept: PDE trains'},
  {phase:0,sol:'F03',solName:'FluidLM',name:'FluidLM V4.4.0 Major',cat:'transformer-alt',type:'llm',dataset:'TinyStories',metric:'loss',val:0,unit:'',ep:'-',stable:true,verdict:'LongConv + memory pump'},
  {phase:0,sol:'F03',solName:'FluidLM',name:'FluidLM V4.4.8 +FluidWorld',cat:'transformer-alt',type:'llm',dataset:'TinyStories',metric:'loss',val:0,unit:'',ep:'-',stable:true,verdict:'Laplacian grad_loss from FluidWorld'},
  {phase:0,sol:'F03',solName:'FluidLM',name:'FluidLM V4.5.0 (current)',cat:'transformer-alt',type:'llm',dataset:'TinyStories',metric:'loss',val:10.76,unit:'',ep:851,stable:true,verdict:'SwiGLU+Mamba+RMSNorm. Best loss 10.76'},
  // 002 - Fixed-Point Substrate
  {phase:8,sol:'002',solName:'Fixed-Point Substrate',name:'FPS v0.1 PDE Temporal',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:9.80,unit:'%',ep:5,stable:true,verdict:'PDE = random'},
  {phase:8,sol:'002',solName:'Fixed-Point Substrate',name:'FPS v0.2 PDE + pool',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:19.80,unit:'%',ep:10,stable:true,verdict:'Diffusion destroys info'},
  {phase:8,sol:'002',solName:'Fixed-Point Substrate',name:'FPS v0.4a Fixed-Point',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:76.20,unit:'%',ep:40,stable:true,verdict:'Paradigm shift works'},
  {phase:8,sol:'002',solName:'Fixed-Point Substrate',name:'FPS v0.4b +regions+var',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:85.18,unit:'%',ep:40,stable:true,verdict:'Better readout'},
  {phase:8,sol:'002',solName:'Fixed-Point Substrate',name:'FPS v0.4c +filters 64ch',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:92.73,unit:'%',ep:40,stable:true,verdict:'Retinal filters'},
  {phase:8,sol:'002',solName:'Fixed-Point Substrate',name:'FPS v0.5 Full Power',cat:'physics-inspired',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:96.44,unit:'%',ep:50,stable:true,verdict:'All levers - 1.6% gap'},
  {phase:8,sol:'002',solName:'Fixed-Point Substrate',name:'FPS v0.5 Fashion-MNIST',cat:'physics-inspired',type:'learning-rule',dataset:'Fashion-MNIST',metric:'accuracy',val:77.15,unit:'%',ep:50,stable:true,verdict:'Promising'},
  {phase:8,sol:'002',solName:'Fixed-Point Substrate',name:'FPS v0.5 CIFAR-10',cat:'physics-inspired',type:'learning-rule',dataset:'CIFAR-10',metric:'accuracy',val:42.24,unit:'%',ep:60,stable:true,verdict:'Limited - needs multi-res'},
  // 003 - Gradient-Free Reservoir Lab
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'Echo State Network (single)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:92.3,unit:'%',ep:0,stable:true,verdict:'Baseline champion, 2.5s'},
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'Thermodynamic (CD)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:88.9,unit:'%',ep:15,stable:true,verdict:'Strong physics-based'},
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'Direct Feedback Alignment',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:89.0,unit:'%',ep:20,stable:true,verdict:'Partial gradient-free'},
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'Local Contrastive',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:85.3,unit:'%',ep:20,stable:true,verdict:'SimCLR-like local'},
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'Mono-Forward (2025)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:88.5,unit:'%',ep:20,stable:true,verdict:'Local classifiers per layer'},
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'NoProp Diffusion (2025)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:80.0,unit:'%',ep:25,stable:true,verdict:'Block-independent'},
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'Mega Reservoir (4 diverse)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:94.1,unit:'%',ep:0,stable:true,verdict:'Diversity is key'},
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'ULTRA RESERVOIR (8+stacking)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:97.28,unit:'%',ep:0,stable:true,verdict:'BEST: -1.2% from backprop'},
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'Ultra Reservoir Fashion-MNIST',cat:'gradient-free',type:'learning-rule',dataset:'Fashion-MNIST',metric:'accuracy',val:88.65,unit:'%',ep:0,stable:true,verdict:'Breakthrough: -0.4% from BP'},
  {phase:9,sol:'003',solName:'Reservoir Lab',name:'Ultra Reservoir CIFAR-10',cat:'gradient-free',type:'learning-rule',dataset:'CIFAR-10',metric:'accuracy',val:46.43,unit:'%',ep:0,stable:true,verdict:'Limited: needs spatial features'},
  // 004 - NoProp-Reservoir (ORIGINAL)
  {phase:9,sol:'004',solName:'NoProp-Reservoir',name:'NoProp+Reservoir V1',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:91.8,unit:'%',ep:0,stable:true,verdict:'ORIGINAL: reservoir denoiser chain'},
  {phase:9,sol:'004',solName:'NoProp-Reservoir',name:'NoProp+Reservoir V2 (scaled)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:95.04,unit:'%',ep:0,stable:true,verdict:'ORIGINAL: 8 blocks 1500-dim'},
  // 005 - Direct Local Learning (Session 2)
  {phase:10,sol:'005',solName:'DirectLocal',name:'DirectLocal v1 (linear probe)',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:97.71,unit:'%',ep:10,stable:true,verdict:'First DirectLocal - matches BP'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'DirectLocal v2 (MLP probe)',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:98.15,unit:'%',ep:20,stable:true,verdict:'BEST: beats BP (98.06%)'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'DirectLocal Deep (5 layers)',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:98.01,unit:'%',ep:15,stable:true,verdict:'Scales to depth'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'DirectLocal v2 CIFAR-10',cat:'local-learning',type:'learning-rule',dataset:'CIFAR-10',metric:'accuracy',val:56.47,unit:'%',ep:20,stable:true,verdict:'Beats BP (56.38%) on CIFAR-10'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'DirectLocal ViT 4-block',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:96.21,unit:'%',ep:15,stable:true,verdict:'Transformer works: -0.8% gap'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'DirectLocal ViT 8-block',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:96.22,unit:'%',ep:15,stable:true,verdict:'Deep Transformer: -0.98% gap'},
  // 005 - Failed gradient-free attempts
  {phase:10,sol:'005',solName:'DirectLocal',name:'ProtoLocal (gradient-free)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:44.26,unit:'%',ep:10,stable:true,verdict:'Gradient-free barrier: prototypes fail'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'ContrastLocal (gradient-free)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:35.57,unit:'%',ep:10,stable:true,verdict:'Contrastive signal too weak'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'HebbFF (gradient-free)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:10.54,unit:'%',ep:10,stable:true,verdict:'Hebbian FF diverges'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'HSIC pure (gradient-free)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:38.97,unit:'%',ep:15,stable:true,verdict:'Linear kernel insufficient'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'HSIC+Probe hybrid',cat:'hybrid',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:42.06,unit:'%',ep:15,stable:true,verdict:'HSIC features unhelpful'},
  // 005 - Round 1-2 failed algorithms
  {phase:10,sol:'005',solName:'DirectLocal',name:'EqProp+Momentum',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:87.49,unit:'%',ep:10,stable:true,verdict:'Local Hebbian - surpassed by DLL'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'EqProp-Tuned',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:70.07,unit:'%',ep:10,stable:true,verdict:'Too slow to converge'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'NOVA belief diffusion',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:48.90,unit:'%',ep:5,stable:true,verdict:'Belief diffusion too slow'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'HESP Hybrid',cat:'hybrid',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:49.40,unit:'%',ep:10,stable:true,verdict:'EqProp+error clash'},
  {phase:10,sol:'005',solName:'DirectLocal',name:'Thermodynamic LL',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:70.0,unit:'%',ep:5,stable:true,verdict:'Backprop in disguise'},
  // 006 - NoProp Diffusion
  {phase:10,sol:'006',solName:'NoProp Diffusion',name:'NoProp 4-block (cosine)',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:97.89,unit:'%',ep:15,stable:true,verdict:'Block-independent: -0.33% gap'},
  // 007 - Mono-Forward
  {phase:10,sol:'007',solName:'Mono-Forward',name:'Mono-Forward [500,300]',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:97.95,unit:'%',ep:15,stable:true,verdict:'Simplest local rule'},
  {phase:10,sol:'007',solName:'Mono-Forward',name:'Mono-Forward Wide [1000,500,200]',cat:'local-learning',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:98.12,unit:'%',ep:15,stable:true,verdict:'Wider = closer to BP'},
  // 006 - SCFF failed implementation
  {phase:10,sol:'006',solName:'NoProp Diffusion',name:'SCFF (implementation failed)',cat:'gradient-free',type:'learning-rule',dataset:'MNIST',metric:'accuracy',val:10.49,unit:'%',ep:15,stable:true,verdict:'Paper: 98.7%, our impl: 10.49%'},
];

const FAILED = [
  {name:'RAPC simple MDL compression',cat:'physics-inspired',acc:'6/20 sparse geometry',fail:'Sparse connected phase narrow; most seeds fragment or empty',lesson:'Compression alone is too weak; spectral locality is required',revisit:'Replaced by spectral-locality score'},
  {name:'RAPC patch gluing',cat:'physics-inspired',acc:'0 bridges',fail:'No inter-patch bridges selected',lesson:'Pair-only flow discards useful hypergraph memory or bridge rule is too conservative',revisit:'Yes - redesign bridge candidates'},
  {name:'Forward-Forward (Hinton)',cat:'local-learning',acc:'9.80%',fail:'NaN from ep 1',lesson:'Goodness threshold unstable',revisit:'Maybe'},
  {name:'Predictive Coding',cat:'local-learning',acc:'crash',fail:'Dimension mismatch',lesson:'Complex to implement correctly',revisit:'Yes'},
  {name:'Equilibrium Propagation',cat:'local-learning',acc:'-',fail:'Not completed',lesson:'Well-published, worth testing',revisit:'Yes'},
  {name:'Reaction-Diffusion',cat:'physics-inspired',acc:'11.35%',fail:'Stuck at random',lesson:'PDE attractors != classification',revisit:'No'},
  {name:'Wave Interference',cat:'physics-inspired',acc:'-',fail:'Phase NaN',lesson:'Complex arithmetic fragile fp32',revisit:'No'},
  {name:'Kuramoto Oscillators',cat:'physics-inspired',acc:'-',fail:'Uniform sync',lesson:'Sync != discrimination',revisit:'No'},
  {name:'Gossip Protocol',cat:'gradient-free',acc:'-',fail:'Info destruction',lesson:'Averaging kills signal',revisit:'No'},
  {name:'Learning by Disagreement',cat:'gradient-free',acc:'9.80%',fail:'NaN',lesson:'Need error signal, not topology',revisit:'No'},
  {name:'Gradient-Free Contrastive',cat:'gradient-free',acc:'11.35%',fail:'Loss explodes',lesson:'Cosine similarity too noisy',revisit:'Maybe'},
  {name:'Spectral Resonance',cat:'physics-inspired',acc:'9.80%',fail:'Freq drift',lesson:'Needs frequency bounds',revisit:'No'},
  {name:'NTSO V2',cat:'local-learning',acc:'88.90%',fail:'Diverges ep 19',lesson:'Multi-signal instability',revisit:'Maybe'},
  {name:'EG+NTSO Hybrid',cat:'hybrid',acc:'86.07%',fail:'Stagnates',lesson:'Competing plasticity = conflict',revisit:'No'},
  {name:'EG-Conv V1 (Sigmoid)',cat:'local-learning',acc:'10%',fail:'Sigmoid saturation',lesson:'Never sigmoid in conv',revisit:'No'},
  {name:'EG V4 + augmentation',cat:'local-learning',acc:'95.98%',fail:'Aug hurts (-1.5%)',lesson:'Noisy inputs confuse recon',revisit:'No'},
  {name:'FPS PDE Temporal (v0.1-v0.3)',cat:'physics-inspired',acc:'19.8%',fail:'Diffusion destroys spatial info',lesson:'Time-stepping PDE loses structure; fixed-point is the right paradigm',revisit:'No'},
  {name:'FPS scalar input projection',cat:'physics-inspired',acc:'92.7%',fail:'Channel diversity too low',lesson:'Each channel needs unique spatial receptive field, not just a scalar',revisit:'No'},
  {name:'FPS single-scale Laplacian',cat:'physics-inspired',acc:'85.2%',fail:'No long-range coupling',lesson:'Multi-scale (3+5+7) needed for spatial interactions',revisit:'No'},
  {name:'FPS linear readout',cat:'physics-inspired',acc:'85.2%',fail:'Saturates early',lesson:'Nonlinear Hebbian readout recovers 11% more from same features',revisit:'No'},
  // 003 - Gradient-Free Reservoir Lab failed approaches
  {name:'Forward-Forward (003 reimpl)',cat:'gradient-free',acc:'17.4%',fail:'Simplified impl, goodness threshold',lesson:'Paper reports 98.5% with full architecture',revisit:'Yes (Self-Contrastive FF)'},
  {name:'Hebbian + WTA',cat:'gradient-free',acc:'8.8%',fail:'No error signal',lesson:'Finds features but cant discriminate',revisit:'No'},
  {name:'Simulated Annealing',cat:'gradient-free',acc:'14.4%',fail:'Weight space too large',lesson:'Global random search needs structure',revisit:'No'},
  {name:'Tropical Geometry',cat:'gradient-free',acc:'12.6%',fail:'Max-plus not discriminative',lesson:'Beautiful theory, weak practice alone',revisit:'Maybe (+ reservoir)'},
  {name:'Entropy-Gated standalone',cat:'gradient-free',acc:'17.2%',fail:'Good regulator, bad teacher',lesson:'Works as component not standalone',revisit:'No standalone'},
  {name:'Fractal/Chaos Attractor',cat:'gradient-free',acc:'17.9%',fail:'Attractor basins dont separate classes',lesson:'Perturbation search too noisy',revisit:'Low'},
  {name:'Simplified DTP',cat:'gradient-free',acc:'8.5%',fail:'Inverse mapping didnt learn',lesson:'Paper reports 99.2% with proper impl',revisit:'Yes (PyTorch)'},
  {name:'Simplified DLL (ICML 2025)',cat:'gradient-free',acc:'12.5%',fail:'Apical-basal interaction too crude',lesson:'Paper reports ~98%',revisit:'Yes (from GitHub)'},
  {name:'Three-Factor Neuromodulated',cat:'gradient-free',acc:'11.7%',fail:'Reward signal too sparse',lesson:'Needs per-neuron eligibility',revisit:'Maybe'},
  {name:'Prospective Configuration',cat:'gradient-free',acc:'36.0%',fail:'Target inference doesnt converge',lesson:'Needs proper variational inference',revisit:'Yes'},
  {name:'v-PuNN (p-adic)',cat:'gradient-free',acc:'16.55%',fail:'No native p-adic arithmetic',lesson:'Ultrametric structure essential. Paper: 99.96%',revisit:'YES - high priority'},
  {name:'Ultra Reservoir CIFAR-10',cat:'gradient-free',acc:'46.4%',fail:'No spatial features',lesson:'Flat reservoir cant see 2D patterns',revisit:'Yes (conv reservoir)'},
  {name:'Conv Reservoir CIFAR-10',cat:'gradient-free',acc:'OOM',fail:'50k images * patches * reservoirs',lesson:'Need PyTorch + GPU batching',revisit:'Yes'},
  // Session 2 - Local Learning Paradigm Search
  {name:'Thermodynamic LL (S2)',cat:'local-learning',acc:'~70%',fail:'Target propagation = backprop light',lesson:'Back-projection of targets is just backprop in disguise',revisit:'No'},
  {name:'Predictive Coding (S2)',cat:'local-learning',acc:'NaN',fail:'Numerical instability',lesson:'Inference iterations unstable without careful tuning',revisit:'Maybe'},
  {name:'FF + InfoGeom (S2)',cat:'local-learning',acc:'NaN',fail:'Numerical instability',lesson:'Natural gradient + FF needs careful Fisher estimation',revisit:'Maybe'},
  {name:'Reaction-Diffusion NN (S2)',cat:'physics-inspired',acc:'~40%',fail:'PDE convergence too slow',lesson:'Same PDE dead-end confirmed again',revisit:'No'},
  {name:'Cellular Automata NN (S2)',cat:'novel-arch',acc:'~85%*',fail:'Readout needs backprop',lesson:'Not truly local if readout uses global gradient',revisit:'No'},
  {name:'NOVA belief diffusion (S2)',cat:'local-learning',acc:'48.9%',fail:'Diffusion too slow',lesson:'Belief propagation needs many steps, convergence uncertain',revisit:'Maybe'},
  {name:'EqProp-Tuned (S2)',cat:'local-learning',acc:'70.1%',fail:'Gap too large',lesson:'2 relaxation phases = 2x compute for mediocre results',revisit:'No'},
  {name:'HESP Hybrid (S2)',cat:'hybrid',acc:'49.4%',fail:'EqProp+error clash',lesson:'Mixing physical equilibrium with error signals = conflict',revisit:'No'},
  {name:'ProtoLocal (S2)',cat:'gradient-free',acc:'44.3%',fail:'Prototypes not discriminative',lesson:'Class prototypes too coarse for deep feature learning',revisit:'Maybe (RBF kernel)'},
  {name:'HebbFF (S2)',cat:'gradient-free',acc:'10.5%',fail:'Hebbian FF diverges',lesson:'Hebbian gating of goodness is numerically unstable',revisit:'No'},
  {name:'ContrastLocal (S2)',cat:'gradient-free',acc:'35.6%',fail:'Signal degrades over epochs',lesson:'Without gradient, contrastive push/pull loses discrimination',revisit:'No'},
  {name:'HSIC pure (S2)',cat:'gradient-free',acc:'39.0%',fail:'Linear kernel insufficient',lesson:'HSIC needs RBF kernel for nonlinear features (O(B^2) cost)',revisit:'Maybe'},
  {name:'HSIC+Probe (S2)',cat:'hybrid',acc:'42.1%',fail:'HSIC features unhelpful for probe',lesson:'HSIC-learned features dont help downstream classifier',revisit:'No'},
  {name:'SCFF impl (S2)',cat:'gradient-free',acc:'10.5%',fail:'Implementation incomplete',lesson:'Paper reports 98.7% - needs full augmentation pipeline',revisit:'Yes (full reimpl)'},
];

const LESSONS = [
  'You need an error signal. Topology/geometry/sync without prediction error leads to NaN.',
  'Simpler plasticity > complex. One gate (entropy) beats 4 competing signals.',
  'PDE dynamics are a dead-end for learning. Their attractors do not align with classification.',
  'Sigmoid for dense, ReLU for conv. Sigmoid kills convolutional feature maps.',
  'Stability > peak accuracy. NTSO peaked 88.9% but EG won 97.46% by never diverging.',
  '2 layers optimal for local learning. Deeper = worse credit assignment without backprop.',
  'Reconstruction is the key signal. "Can I predict my input-" drives learning.',
  'Data augmentation hurts local learning - noisy inputs confuse reconstruction.',
  '@torch.no_grad() is critical - without it, PyTorch builds autograd graph causing memory leak.',
  'Fixed-point > PDE temporal. Finding equilibrium Z*=f(Z*) is fundamentally better than simulating dynamics.',
  'The readout is the bottleneck, not the medium. FPS jumped 85->96% just by improving how we read the fixed point.',
  'Anderson acceleration cuts fixed-point iterations from 11 to 7 for free.',
  'Multi-scale Laplacian (3+5+7) is essential - single-scale misses long-range spatial coupling.',
  'Learnable spatial filters (retinal receptors) give each channel a unique view - massive improvement over scalar projection.',
  // From 003 Gradient-Free Reservoir Lab
  'Reservoir computing is the gradient-free king. Random fixed dynamics + ridge readout beats all complex local rules.',
  'Diversity > depth for gradient-free. 8 diverse shallow reservoirs >> 1 deep network.',
  'HD encoding is a free lunch. Random bipolar projection adds robustness with zero trainable params.',
  'Simplified paper implementations are misleading. DTP/DLL/FF/v-PuNN report 98%+ but need exact framework.',
  'CIFAR needs spatial features. No flat/global approach works on 2D data without conv preprocessing.',
  'Block independence + reservoir = powerful combo. NoProp+Reservoir 95.04% exceeds both individually.',
  // Session 2 - Local Learning Paradigm
  'The gradient-free barrier is real. All attempts (Hebbian, prototypes, HSIC, contrastive) cap at ~44% MNIST.',
  'Per-layer probes are the winning pattern. DirectLocal/MonoForward/NoProp all use per-layer classifiers with h.detach().',
  'CPU advantage grows with depth. DirectLocal 3.3x faster than backprop on CPU for 12 layers.',
  'DirectLocal works on Transformers. 96.22% vs 97.20% BP on ViT-8 proves it extends beyond MLPs.',
  'Local gradient (1-layer) is necessary. Zero-gradient approaches all fail. The minimum viable gradient is intra-layer only.',
];

const ROADMAP = [
  {sol:'P02',p:1,text:'Design weak bridge candidates that preserve inter-patch modular memory without densifying'},
  {sol:'P02',p:1,text:'Run 1000+ seed phase scans on RTX 4070 Ti to measure robustness of the sparse geometric phase'},
  {sol:'P02',p:2,text:'Replace Pauli-basis projections with basis-independent operator algebra diagnostics'},
  {sol:'P02',p:2,text:'Estimate emergent dimension from graph ball growth and Laplacian spectra'},
  {sol:'P02',p:3,text:'Formulate a Type-II crossed-product analogue of the finite toy flow'},
  {sol:'001',p:1,text:'Spatial Hebbian for Conv layers - patch-level correlation, not channel-average'},
  {sol:'001',p:1,text:'Local Batch Norm with learnable affine'},
  {sol:'001',p:2,text:'Layer-wise pretraining - freeze layer 1, train layer 2'},
  {sol:'001',p:2,text:'Local target propagation - combine EG with DTP for deeper nets'},
  {sol:'001',p:3,text:'Fully local probe - kNN or Hebbian classifier, zero backprop'},
  {sol:'001',p:3,text:'Free energy connection - prove EG minimizes variational free energy'},
  {sol:'001',p:4,text:'EG as attention replacement - entropy-gated lateral competition'},
  {sol:'001',p:4,text:'EG + spiking networks - neuromorphic HW compatible'},
  {sol:'F01',p:1,text:'Benchmark FluidVLA on standard manipulation tasks (success rate)'},
  {sol:'F01',p:2,text:'Integrate EG local learning into VLA encoder'},
  {sol:'F02',p:1,text:'Benchmark FluidWorld prediction accuracy (MSE, FID)'},
  {sol:'F02',p:2,text:'Compare to Dreamer, IRIS, other world models'},
  {sol:'F03',p:1,text:'Compare perplexity to same-size Transformer on TinyStories (fair baseline)'},
  {sol:'F03',p:1,text:'Confirm V4.5.0 (SwiGLU+Mamba) breaks through loss plateau'},
  {sol:'F03',p:1,text:'Train on larger corpus (OpenWebText ~40GB)'},
  {sol:'F03',p:2,text:'100M and 300M parameter variants - establish scaling laws'},
  {sol:'F03',p:2,text:'Needle-in-Haystack test at 4K/16K/64K context length'},
  {sol:'F03',p:2,text:'Formal proof: adaptive compute correlates with input difficulty'},
  {sol:'F03',p:3,text:'Persistent h-state across segments (cross-document memory)'},
  {sol:'F03',p:3,text:'Extended dilations [1, 4, 16, 64, 256, 1024]'},
  {sol:'F03',p:3,text:'RK4 integrator (higher-order stability vs Forward Euler)'},
  {sol:'F03',p:3,text:'Adjoint backprop for VRAM reduction'},
  {sol:'F03',p:4,text:'ONNX export + INT8 quantization'},
  {sol:'F03',p:4,text:'Rust inference engine (~5MB binary)'},
  {sol:'F03',p:4,text:'Explore EG (001) entropy-gated plasticity for FluidLM training'},
  {sol:'F03',p:4,text:'Unified PDE foundation with FluidWorld (language + vision)'},
  // 003 - Gradient-Free Reservoir Lab
  {sol:'003',p:1,text:'Convolutional Reservoir for CIFAR-10 - PyTorch impl with patches + Gabor + spatial pooling'},
  {sol:'003',p:1,text:'Proper v-PuNN implementation with native p-adic arithmetic (paper: 99.96%)'},
  {sol:'003',p:2,text:'Scale Ultra Reservoir to ImageNet (PyTorch + GPU)'},
  {sol:'003',p:2,text:'Combine with EG (001): entropy-gated reservoir selection'},
  {sol:'003',p:2,text:'Combine with FPS (002): fixed-point dynamics as reservoir'},
  {sol:'003',p:3,text:'p-Adic VAPO + Reservoir: ultrametric encoding of reservoir states'},
  {sol:'003',p:3,text:'Write paper on diverse multi-reservoir ensemble paradigm'},
  // 004 - NoProp-Reservoir (ORIGINAL)
  {sol:'004',p:1,text:'Fix OOM for Fashion-MNIST (chunked ridge regression)'},
  {sol:'004',p:1,text:'PyTorch implementation for GPU acceleration'},
  {sol:'004',p:1,text:'Cosine noise schedule (from diffusion models literature)'},
  {sol:'004',p:2,text:'Convolutional variant for CIFAR-10 (patch-level reservoirs)'},
  {sol:'004',p:2,text:'Theoretical analysis: why does the denoising chain converge-'},
  {sol:'004',p:3,text:'Write NeurIPS/ICML paper on NoProp-Reservoir architecture'},
  {sol:'004',p:3,text:'Online version with recursive least squares for streaming data'},
  {sol:'004',p:4,text:'Neuromorphic implementation on SpiNNaker/Loihi'},
  // 005 - Direct Local Learning
  {sol:'005',p:1,text:'Test DirectLocal on GPT-2 scale language modeling'},
  {sol:'005',p:1,text:'Multi-threaded C++ implementation (1 thread per layer) for true parallelism'},
  {sol:'005',p:2,text:'ImageNet with ResNet/ViT architectures'},
  {sol:'005',p:2,text:'Combine with NoProp denoising for fully decoupled blocks'},
  {sol:'005',p:3,text:'FPGA/neuromorphic hardware benchmark'},
  {sol:'005',p:3,text:'Pipeline parallelism integration for distributed training'},
  // 006 - NoProp Diffusion
  {sol:'006',p:1,text:'Full flow-matching objective from DeepMind paper'},
  {sol:'006',p:1,text:'CIFAR-10 and CIFAR-100 benchmarks'},
  {sol:'006',p:2,text:'Continuous-time variant (NoProp-CT) for memory savings'},
  {sol:'006',p:2,text:'Compare memory usage vs backprop at scale'},
  {sol:'006',p:3,text:'Apply to Transformer blocks (NoProp-Transformer)'},
  // 007 - Mono-Forward
  {sol:'007',p:1,text:'CNN version to reproduce paper CIFAR-10 result (56.99% beating BP)'},
  {sol:'007',p:1,text:'Compare with DirectLocal on identical architectures'},
  {sol:'007',p:2,text:'Test on Transformer blocks'},
  {sol:'007',p:2,text:'Investigate why MF converges to better minima than BP (paper claim)'},
  {sol:'007',p:3,text:'Energy/compute measurement vs backprop (reproduce 41% energy reduction)'},
  // P01 Roadmap - rewritten 2026-04-24 after methodological reset (strong LVS falsified, Planck-BC conditional)
  {sol:'P01',p:1,text:'Polish rigorous preprint (paper/lvs-preprint.md): honest framing as conditional framework, not predictive theory'},
  {sol:'P01',p:1,text:'SARAH/RGBeta 2-loop validation of 1-loop Planck-BC result (f_g~0.010, f_y~0.013)'},
  {sol:'P01',p:1,text:'Full Eichhorn-Held 2018 literature audit: which f_g, f_y values survive newer FRG truncations-'},
  {sol:'P01',p:1,text:'Joint gauge-Yukawa stationarity treatment (Yukawa residue beta_yt != 0 at M_Pl must be addressed)'},
  {sol:'P01',p:2,text:'Direction 1: Pendleton-Ross style IR attractors - LVS as infrared fixed-point selector-'},
  {sol:'P01',p:2,text:'Direction 2: Yukawa-sector joint stationarity (direction2_yukawa.py)'},
  {sol:'P01',p:2,text:'Direction 3: Hill-type attractor analysis of SM trajectory (fig_hill_attractor.png)'},
  {sol:'P01',p:2,text:'Identify ONE genuinely distinctive prediction (current Planck-BC is dimensional and non-distinctive)'},
  {sol:'P01',p:3,text:'Contact Eichhorn, Held, or Wetterich group for expert review of Planck-BC comparison'},
  {sol:'P01',p:3,text:'Track FRG truncation program: does 60% uncertainty shrink- (would tighten LVS comparison)'},
  {sol:'P01',p:3,text:'Formalize LVS -> FPS bridge - FPS 002 remains the concrete computational realization'},
  {sol:'P01',p:3,text:'Submit rigorous preprint (arXiv hep-th/gr-qc) - as negative result + conditional framework'},
  {sol:'P01',p:4,text:'Track DESI/Euclid BAO: if w != -1 firms up, revisit LVS cosmological implications'},
  {sol:'P01',p:4,text:'Explore stationarity-selection principles in other UV completions (string landscape, AS)'},
  {sol:'P01',p:4,text:'Cross-domain: stationarity formalism for neural learning rules (connect back to FPS 002)'},
  {sol:'global',p:1,text:'Transformer alternatives - local competition instead of attention'},
  {sol:'global',p:2,text:'Gradient-free at scale - evolutionary + entropy gating'},
  {sol:'global',p:3,text:'Cross-pollinate: EG features in VLA/LM pipelines'},
  {sol:'002',p:1,text:'Multi-resolution substrate (multigrid 8x8->16x16->32x32) for CIFAR-10'},
  {sol:'002',p:1,text:'Hierarchical fixed points - coarse-to-fine equilibrium'},
  {sol:'002',p:2,text:'Push Fashion-MNIST to 85%+ with more channels and longer training'},
  {sol:'002',p:2,text:'Benchmark on CIFAR-100 and STL-10'},
  {sol:'002',p:3,text:'Prove convergence guarantees (Banach fixed-point conditions)'},
  {sol:'002',p:3,text:'Formal comparison with DEQ (Deep Equilibrium) networks'},
  {sol:'002',p:4,text:'Substrate as world model - can the medium learn environment dynamics-'},
  {sol:'002',p:4,text:'Combine FPS with Entropy-Gated Learning (001) for hybrid approach'},
];

const TIMELINE = [
  {phase:1,cls:'p',label:'Phase 1 - Baselines',text:'7 classic local algorithms. FF: NaN. Predictive Coding: crashed.',decision:'Classic approaches limited. Need radical ideas.'},
  {phase:2,cls:'f',label:'Phase 2 - Radical',text:'6 novel algorithms. Reaction-Diffusion: 11.35%. Entropy-Gated concept identified.',decision:'Kill PDE/wave/oscillator. Promote EG.'},
  {phase:3,cls:'s',label:'Phase 3 - Shootout',text:'EG V1: 86.85% - clear winner. NTSO: 77.71%. Others: NaN.',decision:'Deep optimize EG and NTSO.'},
  {phase:4,cls:'p',label:'Phase 4 - Deep Opt',text:'NTSO: 88.90% peak then diverges. EG V2: 87.91% stable. Hybrid: 86.07%.',decision:'Simplicity wins. Pure EG only.'},
  {phase:5,cls:'s',label:'Phase 5 - EG V3',text:'@torch.no_grad() fix. Momentum + cosine LR. 92.81%, never plateaus.',decision:'Push wider + MLP probe.'},
  {phase:6,cls:'s',label:'Phase 6 - EG V4',text:'[700,400] + MLP probe: 97.46%. Gap to backprop: 0.58%.',decision:'BREAKTHROUGH. Test CIFAR-10.'},
  {phase:7,cls:'p',label:'Phase 7 - CIFAR-10',text:'EG-Conv V2: 48.22%. Backprop ref: 85.83%. Gap: 37.6%.',decision:'Open challenge. Need spatial Hebbian.'},
  {phase:8,cls:'s',label:'Phase 8 - Fixed-Point Substrate',text:'New paradigm: Z*=f(Z*). PDE temporal failed (9.8-19.8%), pivot to fixed-point. Iterated: 76%->85%->92%->96.44% MNIST. Fashion-MNIST: 77.15%. CIFAR-10: 42.24%.',decision:'Fixed-point equilibrium validated. Multi-resolution needed for CIFAR.'},
];

// ============================================================
// RENDERING ENGINE
// ============================================================

const C={green:'#43e97b',red:'#f5576c',orange:'#f6d365',blue:'#4facfe',purple:'#a18cd1',gray:'#6b7d96',cyan:'#38f9d7'};

// Header stats - dynamic per dataset
function renderHeader(){
  const datasets=[...new Set(EXPERIMENTS.filter(e=>e.val>0).map(e=>e.dataset))];
  let html=`<div class="stat"><div class="stat-value">${SOLUTIONS.length}</div><div class="stat-label">Solutions</div></div>`;
  html+=`<div class="stat"><div class="stat-value">${EXPERIMENTS.length}</div><div class="stat-label">Experiments</div></div>`;
  datasets.forEach(ds=>{
    const best=Math.max(...EXPERIMENTS.filter(e=>e.dataset===ds&&e.cat!=='reference').map(e=>e.val));
    const ref=EXPERIMENTS.find(e=>e.dataset===ds&&e.cat==='reference');
    const color=ref&&best>=ref.val*0.95-'var(--green)':best>20-'var(--orange)':'var(--red)';
    const unit=EXPERIMENTS.find(e=>e.dataset===ds)-.unit||'%';
    html+=`<div class="stat"><div class="stat-value" style="color:${color}">${best}${unit}</div><div class="stat-label">Best ${ds}</div></div>`;
  });
  // Show WIP solutions count
  const wip=SOLUTIONS.filter(s=>s.status==='wip').length;
  if(wip) html+=`<div class="stat"><div class="stat-value" style="color:var(--purple)">${wip}</div><div class="stat-label">WIP</div></div>`;
  document.getElementById('headerStats').innerHTML=html;
}

// Nav
document.querySelectorAll('.nav-tab').forEach(t=>{
  t.addEventListener('click',()=>showTab(t.dataset.tab));
});

// Populate filter dropdowns
function populateFilters(){
  const cats=new Set(),types=new Set(),ds=new Set();
  SOLUTIONS.forEach(s=>{cats.add(s.category);types.add(s.type)});
  EXPERIMENTS.forEach(e=>{cats.add(e.cat);ds.add(e.dataset);types.add(e.type)});
  ['solCatFilter','expCat','failCat'].forEach(id=>{
    const sel=document.getElementById(id);if(!sel)return;
    cats.forEach(c=>{if(c==='reference')return;const o=document.createElement('option');o.value=c;o.textContent=c;sel.appendChild(o)});
  });
  ['solTypeFilter'].forEach(id=>{
    const sel=document.getElementById(id);if(!sel)return;
    types.forEach(t=>{const o=document.createElement('option');o.value=t;o.textContent=t;sel.appendChild(o)});
  });
  ['expDataset','overviewDataset'].forEach(id=>{
    const sel=document.getElementById(id);if(!sel)return;
    if(id!=='overviewDataset')ds.forEach(d=>{const o=document.createElement('option');o.value=d;o.textContent=d;sel.appendChild(o)});
  });
}

// Solutions list
function renderSolutions(){
  document.getElementById('solList').innerHTML=SOLUTIONS.map(s=>{
    const bestKey=Object.keys(s.bestResults)[0];
    const bestVal=bestKey-s.bestResults[bestKey].value+s.bestResults[bestKey].unit:'WIP';
    const bestColor=s.status==='breakthrough'-'var(--green)':s.status==='wip'-'var(--purple)':'var(--orange)';
    const doms=(s.domains||[]).join(',');
    return `<div class="sol-item" data-id="${s.id}" data-cat="${s.category}" data-type="${s.type}" data-status="${s.status}" data-name="${s.name.toLowerCase()}" data-domains="${doms}" onclick="showSolution('${s.id}')">
      <div class="sol-id">${s.id}</div>
      <div class="sol-name">${s.name}<div style="margin-top:2px">${domainBadges(s.domains)}</div></div>
      <div class="sol-desc">${s.principle.substring(0,80)}...</div>
      <div class="sol-meta"><span class="badge badge-${s.status}">${s.status}</span> ${paperBadge(s.paperStatus)}</div>
      <div class="sol-acc" style="color:${bestColor}">${bestVal}</div>
    </div>`;
  }).join('');
}

function filterSolutions(){
  const q=document.getElementById('solSearch').value.toLowerCase();
  const cat=document.getElementById('solCatFilter').value;
  const st=document.getElementById('solStatusFilter').value;
  const ty=document.getElementById('solTypeFilter').value;
  document.querySelectorAll('.sol-item').forEach(el=>{
    const show=(!q||el.dataset.name.includes(q))&&(!cat||el.dataset.cat===cat)&&(!st||el.dataset.status===st)&&(!ty||el.dataset.type===ty);
    el.style.display=show-'flex':'none';
  });
}

function showSolution(id){
  const s=SOLUTIONS.find(x=>x.id===id);
  if(!s){console.error('Solution not found:',id);return}
  try{
  const p=document.getElementById('detailPanel');p.classList.remove('hidden');

  // === KPI ROW ===
  let kpis='';
  Object.entries(s.bestResults).forEach(([ds,r])=>{
    const col=r.value>=90-'var(--green)':r.value>=40-'var(--orange)':'var(--red)';
    kpis+=`<div class="kpi"><div class="kpi-value" style="color:${col}">${r.value}${r.unit}</div><div class="kpi-label">Best ${ds}</div></div>`;
  });
  if(s.params)kpis+=`<div class="kpi"><div class="kpi-value">${Math.round(s.params.local/s.params.total*100)}%</div><div class="kpi-label">Params local</div></div>`;
  // Count related experiments & roadmap items
  const relExp=EXPERIMENTS.filter(e=>e.sol===s.id);
  const relFailed=relExp.filter(e=>e.val<10||(e.stable===false&&e.val<50));
  const relRM=ROADMAP.filter(r=>r.sol===s.id);
  kpis+=`<div class="kpi"><div class="kpi-value">${relExp.length}</div><div class="kpi-label">Experiments</div></div>`;
  kpis+=`<div class="kpi"><div class="kpi-value">${relRM.length}</div><div class="kpi-label">Roadmap items</div></div>`;

  // === EQUATION ===
  let eqHtml='';
  if(s.equation){
    eqHtml=`<h3>Core Equation</h3><div class="eq-block"><div class="katex-render" data-display="true" data-tex="${escapeAttr(s.equation.latex)}"></div></div>`;
    if(s.equation.components){
      eqHtml+=`<table style="margin:8px 0"><tr><th>Symbol</th><th>Description</th><th>Equation</th></tr>`;
      s.equation.components.forEach(c=>{
        eqHtml+=`<tr><td><span class="katex-render" data-tex="${escapeAttr(c.symbol||'')}"></span></td><td>${c.desc||''}</td><td>${c.latex-`<span class="katex-render" data-tex="${escapeAttr(c.latex)}"></span>`:''}</td></tr>`;
      });
      eqHtml+=`</table>`;
    }
    if(s.equation.code){
      eqHtml+=`<h3>Implementation</h3><pre><code class="language-python">${escapeHtml(s.equation.code)}</code></pre>`;
    }
  }

  // === VERSION HISTORY ===
  let verHtml='';
  if(s.versions.length){
    verHtml=`<h3>Version History</h3><table><tr><th>Version</th><th>Architecture</th><th>Dataset</th><th>Result</th><th>Ep</th><th>Stable</th><th>Change</th><th>Status</th></tr>`;
    s.versions.forEach(v=>{
      const col=v.acc>=90-'acc-best':v.acc>=40-'acc-mid':'acc-fail';
      verHtml+=`<tr><td><strong>${v.v}</strong></td><td><code>${v.arch}</code></td><td>${v.dataset||'MNIST'}</td>
        <td class="${col}">${v.acc}%</td><td>${v.ep}</td>
        <td>${v.stable-'Yes':'<span style="color:var(--red)">No</span>'}</td>
        <td>${v.change}</td><td><span class="badge badge-${v.status}">${v.status}</span></td></tr>`;
    });
    verHtml+=`</table>`;
  }

  // === RELATED EXPERIMENTS (from EXPERIMENTS array) ===
  let expHtml='';
  if(relExp.length){
    const sorted=[...relExp].sort((a,b)=>b.val-a.val);
    expHtml=`<h3>All Experiments (${relExp.length})</h3><table><tr><th>Phase</th><th>Algorithm</th><th>Dataset</th><th>Metric</th><th>Value</th><th>Ep</th><th>Stable</th><th>Verdict</th></tr>`;
    sorted.forEach(e=>{
      const cl=e.val>=50-'acc-best':e.val>=10-'acc-mid':'acc-fail';
      expHtml+=`<tr><td>${e.phase}</td><td><strong>${e.name}</strong></td><td>${e.dataset}</td><td>${e.metric}</td>
        <td class="${cl}">${e.val>0-e.val+e.unit:'-'}</td><td>${e.ep}</td>
        <td>${e.stable-'Yes':'<span style="color:var(--red)">No</span>'}</td><td>${e.verdict}</td></tr>`;
    });
    expHtml+=`</table>`;
  }

  // === RELATED FAILED / LESSONS ===
  let failHtml='';
  const relF=FAILED.filter(f=>{
    // match by name patterns from this solution's experiments
    return relExp.some(e=>f.name===e.name || e.name.includes(f.name) || f.name.includes(s.abbr||'---'));
  });
  // Also include any failed versions from the versions array
  const failedVersions=(s.versions||[]).filter(v=>v.status==='failed');
  if(relF.length || failedVersions.length){
    failHtml=`<h3>Failed Approaches & Lessons</h3>`;
    if(failedVersions.length){
      failHtml+=`<table><tr><th>Version</th><th>Result</th><th>Change</th><th>Why it failed</th></tr>`;
      failedVersions.forEach(v=>{
        failHtml+=`<tr><td><strong>${v.v}</strong></td><td class="acc-fail">${v.acc}%</td><td>${v.change}</td>
          <td style="color:var(--text2)">${v.stable===false-'Unstable / diverged':'Did not improve'}</td></tr>`;
      });
      failHtml+=`</table>`;
    }
    if(relF.length){
      failHtml+=`<div style="margin-top:8px">`;
      relF.forEach(f=>{
        failHtml+=`<div class="lesson"><div class="lesson-n" style="background:var(--red)">!</div><div><strong>${f.name}</strong> (${f.acc}) - ${f.fail}. <em style="color:var(--text2)">${f.lesson}</em></div></div>`;
      });
      failHtml+=`</div>`;
    }
  }

  // === ROADMAP ===
  let rmHtml='';
  if(relRM.length){
    rmHtml=`<h3>Roadmap (${relRM.length} items)</h3>`;
    relRM.sort((a,b)=>a.p-b.p).forEach(r=>{
      rmHtml+=`<div class="rm-item"><div class="rm-p p${r.p}">P${r.p}</div><div>${r.text}</div></div>`;
    });
  }

  // === WRITEUPS ===
  let wuHtml='';
  const relWU=WRITEUPS.filter(w=>w.sol===s.id);
  if(relWU.length){
    wuHtml=`<h3>Writeups (${relWU.length})</h3>`;
    relWU.forEach(w=>{
      wuHtml+=`<div class="wu-list-item" onclick="showTab('writeups');setTimeout(()=>openWriteup('${w.id}'),100)" style="margin-bottom:8px;padding:10px 14px">
        <div style="display:flex;gap:8px;align-items:center">
          <span class="wu-type-badge wu-type-${w.type}">${w.type}</span>
          <strong>${w.title}</strong>
          <span class="badge badge-${w.status==='published'-'breakthrough':'limited'}" style="font-size:10px">${w.status}</span>
        </div>
      </div>`;
    });
  }

  // === ASSEMBLE ===
  p.innerHTML=`
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
      <div>
        <h2 style="border:none;padding:0;margin:0">${s.id} - ${s.name}</h2>
        <p style="color:var(--text2);margin-top:4px">${s.principle}</p>
        ${s.github-`<p style="margin-top:4px"><a href="${s.github}" target="_blank">${s.github}</a></p>`:''}
      </div>
      <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
        <span class="badge badge-${s.status}" style="font-size:13px;padding:4px 12px">${s.status}</span>
        <code>${s.category}</code><code>${s.type}</code>
        ${paperBadge(s.paperStatus)}
        ${s.arxiv-`<a href="https://arxiv.org/abs/${s.arxiv}" target="_blank" style="font-size:12px">arXiv:${s.arxiv}</a>`:''}
      </div>
    </div>
    <div style="margin:8px 0">${domainBadges(s.domains)}</div>
    ${s.crossRefs-`<div style="margin:6px 0">${crossRefLinks(s.crossRefs)}</div>`:''}
    <div class="kpi-row">${kpis}</div>
    ${eqHtml}
    ${verHtml}
    ${expHtml}
    ${failHtml}
    ${wuHtml}
    ${rmHtml}
    ${!rmHtml&&s.nextStep-`<h3>Next Step</h3><p>${s.nextStep}</p>`:''}`;

  // Render KaTeX
  p.querySelectorAll('.katex-render').forEach(el=>{
    try{
      katex.render(el.dataset.tex, el, {
        throwOnError:false,
        displayMode: el.dataset.display === 'true'
      });
    }catch(e){ el.textContent = el.dataset.tex; }
  });
  // Highlight code
  p.querySelectorAll('pre code').forEach(b=>hljs.highlightElement(b));
  // Init sort on dynamically generated tables in the detail panel
  initTableSort(p);
  p.scrollIntoView({behavior:'smooth',block:'start'});
  }catch(err){console.error('showSolution error for',id,err);document.getElementById('detailPanel').innerHTML='<p style="color:var(--red)">Error rendering solution: '+err.message+'</p>';}
}

function escapeHtml(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function escapeAttr(s){if(!s)return '';return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

// ============================================================
// GENERIC TABLE SORTING - works on any <table> in the page
// Click header = sort asc, click again = desc, click again = asc...
// Auto-detects numeric vs string columns
// ============================================================
function initTableSort(root){
  (root||document).querySelectorAll('table').forEach(table=>{
    const headers=table.querySelectorAll('thead th');
    if(!headers.length) return;
    // Add sort arrows
    headers.forEach((th,i)=>{
      if(th.querySelector('.sort-arrow')) return; // already init
      th.innerHTML+=`<span class="sort-arrow">&#8597;</span>`;
      th.addEventListener('click',()=>sortTable(table,i,th));
    });
  });
}

function sortTable(table,colIdx,clickedTh){
  const tbody=table.querySelector('tbody')||table;
  const headerRow=table.querySelector('thead tr');
  if(!headerRow) return;
  const rows=Array.from(tbody.querySelectorAll('tr'));
  if(!rows.length) return;

  // Toggle direction
  const wasAsc=clickedTh.classList.contains('sort-asc');
  // Clear all headers in this table
  headerRow.querySelectorAll('th').forEach(th=>{th.classList.remove('sort-asc','sort-desc')});
  const dir=wasAsc-'desc':'asc';
  clickedTh.classList.add('sort-'+dir);

  // Extract cell values
  rows.sort((a,b)=>{
    const cellA=a.children[colIdx];
    const cellB=b.children[colIdx];
    if(!cellA||!cellB) return 0;
    let va=cellA.textContent.trim();
    let vb=cellB.textContent.trim();

    // Try numeric (strip % and other units)
    const na=parseFloat(va.replace(/[^0-9.\-]/g,''));
    const nb=parseFloat(vb.replace(/[^0-9.\-]/g,''));
    if(!isNaN(na)&&!isNaN(nb)){
      return dir==='asc'-na-nb:nb-na;
    }
    // Handle '-' or empty as lowest
    if(va==='-'||va==='') va='\uffff';
    if(vb==='-'||vb==='') vb='\uffff';
    // String compare
    return dir==='asc'-va.localeCompare(vb):vb.localeCompare(va);
  });

  // Re-append sorted rows
  rows.forEach(r=>tbody.appendChild(r));
}

// Experiments table
function renderExp(){
  // Populate solution filter dropdown
  const solSel=document.getElementById('expSol');
  if(solSel.options.length<=1){
    const sols=new Set(EXPERIMENTS.map(e=>e.solName));
    sols.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=s;solSel.appendChild(o)});
  }
  const sort=document.getElementById('expSort').value;
  let sorted=[...EXPERIMENTS];
  if(sort==='acc-desc')sorted.sort((a,b)=>b.val-a.val);
  else if(sort==='acc-asc')sorted.sort((a,b)=>a.val-b.val);
  else if(sort==='phase-asc')sorted.sort((a,b)=>a.phase-b.phase);
  else sorted.sort((a,b)=>a.name.localeCompare(b.name));
  document.getElementById('expBody').innerHTML=sorted.map(e=>{
    const cl=e.val>=50-'acc-best':e.val>=10-'acc-mid':'acc-fail';
    const solBadge=e.sol==='-'-`<span style="color:var(--text2)">-</span>`
      :`<span style="color:var(--accent);font-weight:600">${e.sol}</span> <span style="color:var(--text2);font-size:11px">${e.solName}</span>`;
    return `<tr data-search="${e.name} ${e.cat} ${e.dataset} ${e.verdict} ${e.solName}".toLowerCase() data-dataset="${e.dataset}" data-cat="${e.cat}" data-val="${e.val}" data-sol="${e.solName}">
      <td>${e.phase}</td><td>${solBadge}</td><td><strong>${e.name}</strong></td><td><code>${e.cat}</code></td>
      <td>${e.dataset}</td><td>${e.metric}</td><td class="${cl}">${e.val>0-e.val+e.unit:'-'}</td>
      <td>${e.ep}</td><td>${e.stable-'Yes':'<span style="color:var(--red)">No</span>'}</td><td>${e.verdict}</td></tr>`;
  }).join('');
  filterExp();
}

function filterExp(){
  const q=document.getElementById('expSearch').value.toLowerCase();
  const ds=document.getElementById('expDataset').value;
  const cat=document.getElementById('expCat').value;
  const st=document.getElementById('expStatus').value;
  const sol=document.getElementById('expSol').value;
  let count=0;
  document.querySelectorAll('#expBody tr').forEach(r=>{
    let show=true;
    if(q&&!r.textContent.toLowerCase().includes(q))show=false;
    if(ds&&r.dataset.dataset!==ds)show=false;
    if(cat&&r.dataset.cat!==cat)show=false;
    if(sol&&r.dataset.sol!==sol)show=false;
    if(st){const v=parseFloat(r.dataset.val);
      if(st==='success'&&v<50)show=false;
      if(st==='limited'&&(v<10||v>=50))show=false;
      if(st==='failed'&&v>=10)show=false;
    }
    r.style.display=show-'':'none';
    if(show)count++;
  });
  document.getElementById('expCount').textContent=count;
}

// Failed table
function renderFailed(){
  document.getElementById('failBody').innerHTML=FAILED.map(f=>`
    <tr data-search="${f.name} ${f.cat} ${f.fail} ${f.lesson}" data-cat="${f.cat}" data-revisit="${f.revisit}">
      <td><strong>${f.name}</strong></td><td><code>${f.cat}</code></td><td class="acc-fail">${f.acc}</td>
      <td>${f.fail}</td><td>${f.lesson}</td>
      <td>${f.revisit==='Yes'-'<span style="color:var(--green)">Yes</span>':f.revisit==='Maybe'-'<span style="color:var(--orange)">Maybe</span>':'No'}</td>
    </tr>`).join('');
  document.getElementById('lessonsContainer').innerHTML=LESSONS.map((l,i)=>
    `<div class="lesson"><div class="lesson-n">${i+1}</div><div>${l}</div></div>`).join('');
}

function filterFail(){
  const q=document.getElementById('failSearch').value.toLowerCase();
  const cat=document.getElementById('failCat').value;
  const rev=document.getElementById('failRevisit').value;
  document.querySelectorAll('#failBody tr').forEach(r=>{
    let show=true;
    if(q&&!r.dataset.search.includes(q))show=false;
    if(cat&&r.dataset.cat!==cat)show=false;
    if(rev&&r.dataset.revisit!==rev)show=false;
    r.style.display=show-'':'none';
  });
}

// Timeline
function renderTimeline(){
  document.getElementById('timelineContainer').innerHTML=TIMELINE.map(t=>`
    <div class="tl-item ${t.cls}">
      <div class="tl-label">${t.label}</div>
      <div class="card" style="margin-top:4px">
        <p>${t.text}</p>
        <p style="color:var(--text2);margin-top:6px;font-size:12px"><strong>Decision:</strong> ${t.decision}</p>
      </div>
    </div>`).join('');
}

// Roadmap
// Resolve solution ID to human-readable name
function solLabel(id){
  if(id==='global') return 'Global Research';
  const s=SOLUTIONS.find(x=>x.id===id);
  return s - `${s.id} ${s.name}` : id;
}

function renderRM(){
  const sel=document.getElementById('rmSolFilter');
  const seen=new Set();
  ROADMAP.forEach(r=>{
    if(!seen.has(r.sol)){
      seen.add(r.sol);
      const o=document.createElement('option');
      o.value=r.sol;
      o.textContent=solLabel(r.sol);
      sel.appendChild(o);
    }
  });
  filterRM();
}
function filterRM(){
  const sol=document.getElementById('rmSolFilter').value;
  const pri=document.getElementById('rmPriFilter').value;
  document.getElementById('rmContainer').innerHTML=ROADMAP.filter(r=>(!sol||r.sol===sol)&&(!pri||r.p==pri)).map(r=>{
    const label=solLabel(r.sol);
    const color=r.sol==='global'-'var(--text2)':'var(--accent)';
    return `<div class="rm-item"><div class="rm-p p${r.p}">P${r.p}</div><div><span style="color:${color};font-weight:600">${label}</span> - ${r.text}</div></div>`;
  }).join('');
}

// ============================================================
// CHARTS
// ============================================================
const chartDefaults={responsive:true,plugins:{legend:{labels:{color:'#e6edf3',font:{size:11}}}},
  scales:{y:{grid:{color:'#1a2030'},ticks:{color:'#6b7d96'}},x:{grid:{color:'#1a2030'},ticks:{color:'#6b7d96',font:{size:10}}}}};

// ============================================================
// DYNAMIC DASHBOARD - domain cards + domain-specific views
// ============================================================
const domainMeta={
  ml:{name:'Machine Learning',icon:'&#9881;',color:C.blue},
  physics:{name:'Physics',icon:'&#9883;',color:C.purple},
  quantum:{name:'Quantum',icon:'&#9878;',color:C.cyan},
  cybersec:{name:'Cybersecurity',icon:'&#9888;',color:C.red},
  robotics:{name:'Robotics',icon:'&#9881;',color:C.orange},
  neuro:{name:'Neuroscience',icon:'&#9829;',color:C.green},
  math:{name:'Mathematics',icon:'&#8734;',color:C.gray},
};

let activeDashCharts=[];
function destroyDashCharts(){activeDashCharts.forEach(c=>c.destroy());activeDashCharts=[]}

function renderDomainCards(){
  // Compute stats per domain
  const domStats={};
  DOMAINS.forEach(d=>{domStats[d]={solutions:0,experiments:0,best:null,bestLabel:'',wip:0}});
  SOLUTIONS.forEach(s=>{
    (s.domains||[]).forEach(d=>{
      if(!domStats[d]) return;
      domStats[d].solutions++;
      if(s.status==='wip') domStats[d].wip++;
      // Track best result
      Object.entries(s.bestResults||{}).forEach(([ds,r])=>{
        if(!domStats[d].best||r.value>domStats[d].best){domStats[d].best=r.value;domStats[d].bestLabel=`${r.value}${r.unit} ${ds}`}
      });
    });
  });
  EXPERIMENTS.forEach(e=>{
    const sol=SOLUTIONS.find(s=>s.id===e.sol);
    if(sol)(sol.domains||[]).forEach(d=>{if(domStats[d])domStats[d].experiments++});
  });

  // Render cards
  const container=document.getElementById('domainCards');
  container.innerHTML=DOMAINS.map(d=>{
    const s=domStats[d];const m=domainMeta[d]||{name:d,icon:'-',color:C.gray};
    const hasData=s.solutions>0;
    return `<div class="card" style="cursor:pointer;border-left:3px solid ${m.color};padding:14px;${!hasData-'opacity:.4':''}" onclick="switchDomain(null,'${d}')">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div style="font-size:14px;font-weight:600;color:${m.color}">${m.icon} ${m.name}</div>
        ${s.wip-`<span class="badge badge-wip" style="font-size:9px">WIP</span>`:''}
      </div>
      <div style="margin-top:8px;display:flex;gap:16px;font-size:12px;color:var(--text2)">
        <div><strong style="color:var(--text)">${s.solutions}</strong> solutions</div>
        <div><strong style="color:var(--text)">${s.experiments}</strong> experiments</div>
      </div>
      ${s.bestLabel-`<div style="margin-top:6px;font-size:13px"><strong style="color:${m.color}">${s.bestLabel}</strong></div>`:'<div style="margin-top:6px;font-size:12px;color:var(--text2)">No results yet</div>'}
    </div>`;
  }).join('');

  // Render domain sub-tabs
  const tabs=document.getElementById('domainTabs');
  tabs.innerHTML=`<div class="nav-tab active" onclick="switchDomain(this,'all')" style="border:none">All Domains</div>`;
  DOMAINS.forEach(d=>{
    const m=domainMeta[d]||{name:d};
    if(domStats[d].solutions>0){
      tabs.innerHTML+=`<div class="nav-tab" onclick="switchDomain(this,'${d}')" style="border:none">${m.name}</div>`;
    }
  });

  switchDomain(null,'all');
}

function switchDomain(btn,domain){
  // Update tab state
  document.querySelectorAll('#domainTabs .nav-tab').forEach(t=>t.classList.remove('active'));
  if(btn) btn.classList.add('active');
  else document.querySelector(`#domainTabs .nav-tab`)-.classList.add('active');

  const container=document.getElementById('dashboardContent');
  destroyDashCharts();

  // Filter solutions & experiments by domain
  const sols=domain==='all'-SOLUTIONS:SOLUTIONS.filter(s=>(s.domains||[]).includes(domain));
  const exps=domain==='all'-EXPERIMENTS:EXPERIMENTS.filter(e=>{
    const sol=SOLUTIONS.find(s=>s.id===e.sol);
    return sol&&(sol.domains||[]).includes(domain) || e.cat==='reference';
  });

  // Build dashboard HTML
  let html='<div class="chart-grid">';

  // Chart 1: Results bar chart (filtered)
  const chartData=exps.filter(e=>e.val>0).sort((a,b)=>b.val-a.val).slice(0,20);
  html+=`<div class="chart-card"><h3>Results${domain!=='all'-' - '+((domainMeta[domain]||{}).name||domain):''}</h3><canvas id="dashChart1"></canvas></div>`;

  // Chart 2: Status distribution
  html+=`<div class="chart-card"><h3>Status Distribution</h3><canvas id="dashChart2"></canvas></div>`;
  html+=`</div><div class="chart-grid">`;

  // Chart 3: Solutions by category
  html+=`<div class="chart-card"><h3>By Category</h3><canvas id="dashChart3"></canvas></div>`;

  // Chart 4: Evolution of best solution in this domain
  const bestSol=sols.filter(s=>s.versions&&s.versions.length).sort((a,b)=>{
    const aMax=Math.max(...a.versions.map(v=>v.acc));
    const bMax=Math.max(...b.versions.map(v=>v.acc));
    return bMax-aMax;
  })[0];
  if(bestSol){
    html+=`<div class="chart-card"><h3>Evolution - ${bestSol.name}</h3><canvas id="dashChart4"></canvas></div>`;
  } else {
    html+=`<div class="chart-card"><h3>No version history yet</h3><div style="padding:40px;text-align:center;color:var(--text2)">Add experiments to see evolution</div></div>`;
  }
  html+=`</div>`;

  // Solutions table for this domain
  html+=`<div class="card"><div class="card-title" style="margin-bottom:10px">Solutions${domain!=='all'-' in '+(domainMeta[domain]||{}).name:''}</div>`;
  html+=`<table><thead><tr><th>ID</th><th>Name</th><th>Domains</th><th>Status</th><th>Best Result</th><th>Paper</th><th>Next Step</th></tr></thead><tbody>`;
  sols.forEach(s=>{
    const bestKey=Object.keys(s.bestResults||{})[0];
    const bestStr=bestKey-`${s.bestResults[bestKey].value}${s.bestResults[bestKey].unit} ${bestKey}`:'WIP';
    const bestColor=s.status==='breakthrough'-'acc-best':s.status==='wip'-'':'acc-mid';
    html+=`<tr style="cursor:pointer" onclick="showTab('solutions');setTimeout(()=>showSolution('${s.id}'),100)">
      <td><code>${s.id}</code></td><td><strong>${s.name}</strong></td>
      <td>${domainBadges(s.domains)}</td>
      <td><span class="badge badge-${s.status}">${s.status}</span></td>
      <td class="${bestColor}">${bestStr}</td>
      <td>${paperBadge(s.paperStatus)}</td>
      <td style="color:var(--text2);font-size:12px">${s.nextStep||''}</td></tr>`;
  });
  html+=`</tbody></table></div>`;

  container.innerHTML=html;

  // Render charts
  if(chartData.length){
    activeDashCharts.push(new Chart(document.getElementById('dashChart1'),{type:'bar',
      data:{labels:chartData.map(e=>e.name.substring(0,20)+(e.dataset!=='MNIST'-' ('+e.dataset+')':'')),
        datasets:[{data:chartData.map(e=>e.val),backgroundColor:chartData.map(e=>e.val>=50-C.green:e.val>=10-C.orange:C.red),borderRadius:4}]},
      options:{...chartDefaults,indexAxis:'y',plugins:{legend:{display:false}},
        scales:{x:{...chartDefaults.scales.x,beginAtZero:true,ticks:{...chartDefaults.scales.x.ticks,callback:v=>v+'%'}},
                y:{...chartDefaults.scales.y,ticks:{...chartDefaults.scales.y.ticks,font:{size:10}}}}}}));
  }

  // Status donut
  const st={success:0,limited:0,failed:0,wip:0};
  sols.forEach(s=>{if(s.status==='breakthrough')st.success++;else if(s.status==='promising')st.success++;else if(s.status==='wip')st.wip++;else if(s.status==='limited')st.limited++;else st.failed++});
  activeDashCharts.push(new Chart(document.getElementById('dashChart2'),{type:'doughnut',
    data:{labels:['Success','WIP','Limited','Failed'],datasets:[{data:[st.success,st.wip,st.limited,st.failed],
      backgroundColor:[C.green,C.purple,C.orange,C.red]}]},
    options:{responsive:true,plugins:{legend:{position:'right',labels:{color:'#d4dce8',font:{size:11}}}}}}));

  // Category donut
  const cats={};exps.filter(e=>e.cat!=='reference').forEach(e=>{cats[e.cat]=(cats[e.cat]||0)+1});
  const catColors=[C.blue,C.green,C.orange,C.purple,C.red,C.gray,C.cyan];
  activeDashCharts.push(new Chart(document.getElementById('dashChart3'),{type:'doughnut',
    data:{labels:Object.keys(cats),datasets:[{data:Object.values(cats),backgroundColor:catColors.slice(0,Object.keys(cats).length)}]},
    options:{responsive:true,plugins:{legend:{position:'right',labels:{color:'#d4dce8',font:{size:11}}}}}}));

  // Evolution chart
  if(bestSol && document.getElementById('dashChart4')){
    const vers=bestSol.versions.filter(v=>v.dataset==='MNIST'||!v.dataset);
    if(vers.length){
      activeDashCharts.push(new Chart(document.getElementById('dashChart4'),{type:'line',
        data:{labels:vers.map(v=>v.v),datasets:[{label:'Accuracy',
          data:vers.map(v=>v.acc),borderColor:C.green,backgroundColor:'rgba(67,233,123,.08)',
          fill:true,tension:.3,pointRadius:5,
          pointBackgroundColor:vers.map(v=>v.stable-C.green:C.red)}]},
        options:{...chartDefaults,scales:{...chartDefaults.scales,y:{...chartDefaults.scales.y,
          ticks:{...chartDefaults.scales.y.ticks,callback:v=>v+'%'}}}}}));
    }
  }
  // Init sort on generated table
  initTableSort(container);
}

function buildOverviewChart(){renderDomainCards()}

// Timeline chart
const tlChart=new Chart(document.getElementById('timelineChart'),{type:'line',
  data:{labels:TIMELINE.map(t=>t.label.replace('Phase ','P')),datasets:[
    {label:'Best local MNIST',data:[9.80,11.35,86.85,88.90,92.81,97.46,97.46],borderColor:C.green,backgroundColor:'rgba(67,233,123,.08)',fill:true,tension:.3,pointRadius:5},
    {label:'Backprop MNIST ref',data:Array(7).fill(98.04),borderColor:C.gray,borderDash:[5,5],pointRadius:0},
    {label:'Best local CIFAR-10',data:[null,null,null,null,null,null,48.22],borderColor:C.orange,pointRadius:7,pointBackgroundColor:C.orange},
  ]},options:{...chartDefaults,scales:{...chartDefaults.scales,y:{...chartDefaults.scales.y,min:0,max:100,ticks:{...chartDefaults.scales.y.ticks,callback:v=>v+'%'}}}}});

function toggleEvo(btn,idx){
  btn.classList.toggle('active');
  tlChart.data.datasets[idx].hidden=!btn.classList.contains('active');
  tlChart.update();
}

// ============================================================
// INIT
// ============================================================
// ============================================================
// GLOBAL SEARCH - searches across ALL data
// ============================================================
function clearGlobalSearch(){
  const input=document.getElementById('globalSearch');
  input.value='';
  document.getElementById('searchWrap').classList.remove('has-value');
  document.getElementById('globalResults').classList.add('hidden');
  input.focus();
}

function globalSearchHandler(){
  const input=document.getElementById('globalSearch');
  const q=input.value.toLowerCase().trim();
  const wrap=document.getElementById('searchWrap');
  const res=document.getElementById('globalResults');
  // Toggle clear button visibility
  if(input.value.length>0) wrap.classList.add('has-value'); else wrap.classList.remove('has-value');
  if(q.length<2){res.classList.add('hidden');return}
  res.classList.remove('hidden');
  let hits=[];
  // Search solutions
  SOLUTIONS.forEach(s=>{
    const blob=`${s.name} ${s.principle} ${s.category} ${s.type} ${(s.domains||[]).join(' ')} ${s.equation-.code||''} ${s.equation-.latex||''} ${(s.tags||[]).join(' ')}`.toLowerCase();
    if(blob.includes(q)) hits.push({type:'Solution',label:`${s.id} - ${s.name}`,sub:s.principle.substring(0,80),action:()=>{showTab('solutions');setTimeout(()=>showSolution(s.id),100)}});
  });
  // Search experiments
  EXPERIMENTS.forEach(e=>{
    const blob=`${e.name} ${e.solName} ${e.cat} ${e.dataset} ${e.verdict}`.toLowerCase();
    if(blob.includes(q)) hits.push({type:'Experiment',label:e.name,sub:`${e.dataset} ${e.val}${e.unit} - ${e.verdict}`,action:()=>showTab('experiments')});
  });
  // Search failed
  FAILED.forEach(f=>{
    const blob=`${f.name} ${f.fail} ${f.lesson}`.toLowerCase();
    if(blob.includes(q)) hits.push({type:'Lesson',label:f.name,sub:f.lesson,action:()=>showTab('failed')});
  });
  // Search lessons
  LESSONS.forEach((l,i)=>{
    if(l.toLowerCase().includes(q)) hits.push({type:'Lesson',label:`Lesson #${i+1}`,sub:l.substring(0,80),action:()=>showTab('failed')});
  });
  // Search roadmap
  ROADMAP.forEach(r=>{
    if(r.text.toLowerCase().includes(q)) hits.push({type:'Roadmap',label:solLabel(r.sol),sub:r.text.substring(0,80),action:()=>showTab('roadmap')});
  });
  // Search todos
  TODOS.forEach(t=>{
    if(t.text.toLowerCase().includes(q)) hits.push({type:'Todo',label:t.done-'[done]':'[open]',sub:t.text.substring(0,80),action:()=>showTab('todo')});
  });
  // Search writeups
  WRITEUPS.forEach(w=>{
    const blob=`${w.title} ${w.abstract||''} ${(w.tags||[]).join(' ')} ${w.content||''}`.toLowerCase();
    if(blob.includes(q)) hits.push({type:'Writeup',label:w.title,sub:`${w.type} - ${w.status}`,action:()=>{showTab('writeups');setTimeout(()=>openWriteup(w.id),100)}});
  });
  // Limit and render
  hits=hits.slice(0,15);
  res.innerHTML=hits.length-hits.map(h=>
    `<div class="sr-item" onclick="clearGlobalSearch();(${h.action.toString()})()">
      <div class="sr-type">${h.type}</div><div><strong>${h.label}</strong><br><span style="color:var(--text2);font-size:11px">${h.sub}</span></div>
    </div>`).join(''):`<div style="padding:16px;color:var(--text2);text-align:center">No results for "${q}"</div>`;
}

function showTab(id){
  document.querySelectorAll('.nav-tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(x=>x.classList.remove('active'));
  document.querySelector(`.nav-tab[data-tab="${id}"]`)-.classList.add('active');
  document.getElementById(id)-.classList.add('active');
}

// ============================================================
// TODO RENDERING
// ============================================================
let todoFilter='all';
function renderTodos(){
  const q=(document.getElementById('todoSearch')-.value||'').toLowerCase();
  const items=TODOS.filter(t=>{
    if(todoFilter==='open'&&t.done)return false;
    if(todoFilter==='done'&&!t.done)return false;
    if(q&&!t.text.toLowerCase().includes(q))return false;
    return true;
  });
  document.getElementById('todoContainer').innerHTML=items.map(t=>{
    const priBadge=t.priority==='high'-'<span class="badge" style="background:rgba(248,81,73,.15);color:var(--red);margin-left:6px">high</span>'
      :t.priority==='idea'-'<span class="badge" style="background:rgba(88,166,255,.15);color:var(--accent);margin-left:6px">idea</span>'
      :t.priority==='speculative'-'<span class="badge" style="background:rgba(188,140,255,.15);color:var(--purple);margin-left:6px">speculative</span>':'';
    return `<div class="todo-item">
      <div class="todo-check ${t.done-'done':''}">${t.done-'&#10003;':''}</div>
      <div style="${t.done-'text-decoration:line-through;color:var(--text2)':''}">${t.text}${priBadge}</div>
    </div>`;
  }).join('');
}
function filterTodos(){renderTodos()}
function toggleTodoFilter(btn,mode){
  btn.parentElement.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  todoFilter=mode;
  renderTodos();
}

// ============================================================
// HELPER: domain badges HTML
// ============================================================
function domainBadges(domains){
  if(!domains||!domains.length) return '';
  return domains.map(d=>`<span class="domain-badge domain-${d}">${d}</span>`).join(' ');
}

// HELPER: cross-ref links
function crossRefLinks(refs){
  if(!refs) return '';
  let html='';
  const render=(label,ids)=>{
    if(!ids||!ids.length) return '';
    return `<span style="color:var(--text2);font-size:11px">${label}:</span> `+ids.map(id=>{
      const s=SOLUTIONS.find(x=>x.id===id);
      return s-`<span class="xref" onclick="showSolution('${id}')">${id} ${s.name}</span>`:`<span class="xref">${id}</span>`;
    }).join(' ')+' ';
  };
  html+=render('Builds on',refs.builds_on);
  html+=render('Enables',refs.enables);
  html+=render('Related',refs.related_to);
  return html;
}

// HELPER: paper status badge
function paperBadge(status){
  if(!status||status==='none') return '<span class="paper-none">no paper</span>';
  return `<span class="paper-${status}">${status}</span>`;
}

// ============================================================
// WRITEUPS
// ============================================================
// type: article | book | chapter | essay | tutorial
// status: draft | review | published
// content: markdown string (embedded here, or fetched from file)
const WRITEUPS = [
  {id:'wu-P02-summary',
   title:'RAPC Modular Geometry - Research Summary',
   type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Gate-by-gate summary of RAPC, a toy falsification lab for emergent geometry as sparse spectral compression of modular correlations.',
   tags:['RAPC','modular-geometry','quantum-gravity','BMV','spectral-locality'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_SPECTRAL_LOCALITY_SCAN_RESULTS.md',
   content:null
  },
  {id:'wu-P02-bmv', title:'RAPC BMV Gate', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_BMV_RESULTS.md', content:null},
  {id:'wu-P02-modular-phase', title:'RAPC Modular Phase Gate', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_MODULAR_PHASE_RESULTS.md', content:null},
  {id:'wu-P02-subalgebra', title:'RAPC Subalgebra Selection', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_SUBALGEBRA_SELECTION_RESULTS.md', content:null},
  {id:'wu-P02-hypergraph', title:'RAPC Hypergraph Coarse-Graining', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_HYPERGRAPH_COARSE_GRAIN_RESULTS.md', content:null},
  {id:'wu-P02-auto-coarse', title:'RAPC Automatic Coarse-Graining', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_AUTO_COARSE_GRAIN_RESULTS.md', content:null},
  {id:'wu-P02-iterated-flow', title:'RAPC Iterated Flow', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_ITERATED_FLOW_RESULTS.md', content:null},
  {id:'wu-P02-sparse-budget', title:'RAPC Sparse Budget Flow', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_SPARSE_BUDGET_FLOW_RESULTS.md', content:null},
  {id:'wu-P02-mdl-budget', title:'RAPC MDL Budget Selection', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_MDL_BUDGET_SELECTION_RESULTS.md', content:null},
  {id:'wu-P02-phase-scan', title:'RAPC Phase Scan', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_PHASE_SCAN_RESULTS.md', content:null},
  {id:'wu-P02-patch-gluing', title:'RAPC Patch Gluing', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_PATCH_GLUING_RESULTS.md', content:null},
  {id:'wu-P02-residual-patch', title:'RAPC Residual Patch Gluing', type:'article', sol:'P02', solName:'RAPC Modular Geometry', date:'2026-04-24', status:'draft',
   abstract:'Detailed RAPC technical note for the modular geometry toy research line.',
   tags:['RAPC','modular-geometry','quantum-gravity'],
   file:'solutions/P02_rapc_modular_geometry/writeups/RAPC_RESIDUAL_PATCH_GLUING_RESULTS.md', content:null},
  {id:'wu-P01-rigorous-preprint',
   title:'LVS as a Planck-Scale Boundary Condition: A Conditional Framework',
   type:'article', sol:'P01', solName:'LVS Theory', date:'2026-04', status:'draft',
   abstract:'Rigorous preprint (April 2026). Strong global-flow form of LVS is falsified. Planck-BC form survives as a conditional deduction (f_g~0.010, f_y~0.013) to be compared against FRG fixed-point values. Eichhorn-Held 2018 gives f_g~0.055, f_y~0.004 - factor 3-5 mismatch within ~60% truncation uncertainty.',
   tags:['LVS','physics','preprint','english','rigorous','negative-result','FRG','asymptotic-safety','boundary-condition'],
   file:'solutions/P01_lvs_theory/paper/lvs-preprint.md',
   content:null
  },
  {id:'wu-P01-scientific-status',
   title:'LVS - Scientific Status (April 2026)',
   type:'article', sol:'P01', solName:'LVS Theory', date:'2026-04', status:'draft',
   abstract:'One-page honest status note after methodological reset. Summarizes what is falsified, what is conditional, what remains to be tested.',
   tags:['LVS','physics','status','english','rigorous','methodology'],
   file:'solutions/P01_lvs_theory/rigorous_2026_04/LVS_Scientific_Status.md',
   content:null
  },
  {id:'wu-P01-master-synthesis',
   title:'LVS Master Synthesis',
   type:'essay', sol:'P01', solName:'LVS Theory', date:'2026-04', status:'draft',
   abstract:'Top-level research synthesis tying together the rigorous 2026-04 work with the broader LVS programme.',
   tags:['LVS','physics','synthesis','english'],
   file:'solutions/P01_lvs_theory/LVS_Master_Synthesis.md',
   content:null
  },
  {id:'wu-P01-itfromfix',
   title:'It from Fix: Why Reality Might Be a Fixed Point',
   type:'essay', sol:'P01', solName:'LVS Theory', date:'2024', status:'draft',
   abstract:'What if the universe doesn\'t evolve- What if reality is simply the stable configuration of something deeper-',
   tags:['LVS','fixed-point','physics','philosophy','time-emergence','english'],
   file:'solutions/P01_lvs_theory/writeups/it_from_fix.md',
   content:null
  },
  {id:'wu-P01-dupointfixe',
   title:'Du Point Fixe au Point de Rupture',
   type:'book', sol:'P01', solName:'LVS Theory', date:'2026-04', status:'draft',
   abstract:'Journal complet d\'une exploration intellectuelle. 20 chapitres, 63 000 caracteres. De l\'etincelle du photon a l\'epilogue.',
   tags:['LVS','physics','french','intellectual-journal','photon','fixed-point','symmetry-breaking'],
   file:'solutions/P01_lvs_theory/writeups/Du Point Fixe au Point de Rupture.md',
   content:null
  },
  {id:'wu-P01-pause',
   title:'Et si l\'Univers etait sur Pause -',
   type:'article', sol:'P01', solName:'LVS Theory', date:'2026-03', status:'draft',
   abstract:'Comment les PDE, des exercices de pensee et des confirmations experimentales ont relie le photon, le vide quantique et l\'expansion en un seul principe.',
   tags:['LVS','physics','french','vulgarisation','photon','vacuum','expansion','fixed-point'],
   file:'solutions/P01_lvs_theory/writeups/Et_si_lunivers_etait_en_pause.md',
   content:null
  },
  {id:'wu-001-neurons',
   title:'What if Neurons Could Decide When to Learn-',
   type:'article', sol:'001', solName:'Entropy-Gated Learning', date:'2026-04-03', status:'draft',
   abstract:'The story of how entropy-gated plasticity achieved 97.46% on MNIST without backpropagation - and what it means for the future of AI training.',
   tags:['local-learning','entropy','no-backprop','paradigm-shift','english'],
   file:'solutions/001_entropy_gated_learning/writeups/overview.md',
   content:null
  },
];

// Minimal markdown to HTML (no external dep)
function mdToHtml(md){
  if(!md) return '<p style="color:var(--text2)">No content yet.</p>';
  let html=md
    // Code blocks first (before other rules)
    .replace(/```(\w*)\n([\s\S]*-)```/g,(m,lang,code)=>`<pre><code class="language-${lang||'text'}">${escapeHtml(code.trim())}</code></pre>`)
    // Inline code
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    // Headers
    .replace(/^#### (.+)$/gm,'<h4>$1</h4>')
    .replace(/^### (.+)$/gm,'<h3>$1</h3>')
    .replace(/^## (.+)$/gm,'<h2>$1</h2>')
    .replace(/^# (.+)$/gm,'<h1>$1</h1>')
    // Bold / italic
    .replace(/\*\*(.+-)\*\*/g,'<strong>$1</strong>')
    .replace(/\*(.+-)\*/g,'<em>$1</em>')
    // Blockquotes
    .replace(/^> (.+)$/gm,'<blockquote>$1</blockquote>')
    // Horizontal rules
    .replace(/^---$/gm,'<hr>')
    // Unordered lists
    .replace(/^- (.+)$/gm,'<li>$1</li>')
    // Links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank">$1</a>')
    // Images
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g,'<img src="$2" alt="$1">')
    // Paragraphs (lines not already tagged)
    .replace(/^(-!<[huplbio]|<li|<hr|<pre|<block)(.+)$/gm,'<p>$1</p>')
    // Wrap consecutive <li> in <ul>
    .replace(/(<li>.*<\/li>\n-)+/g,m=>`<ul>${m}</ul>`);
  // LaTeX blocks
  html=html.replace(/\$\$([^$]+)\$\$/g,'<div class="katex-render" data-display="true" data-tex="$1"></div>');
  html=html.replace(/\$([^$]+)\$/g,'<span class="katex-render" data-tex="$1"></span>');
  return html;
}

function renderWriteups(){
  // Populate solution filter
  const solSel=document.getElementById('wuSol');
  if(solSel.options.length<=1){
    const sols=new Set(WRITEUPS.map(w=>w.sol).filter(Boolean));
    sols.forEach(s=>{const o=document.createElement('option');o.value=s;o.textContent=solLabel(s);solSel.appendChild(o)});
  }
  filterWriteups();
}

function filterWriteups(){
  const q=(document.getElementById('wuSearch')-.value||'').toLowerCase();
  const type=document.getElementById('wuType')-.value||'';
  const sol=document.getElementById('wuSol')-.value||'';
  const status=document.getElementById('wuStatus')-.value||'';

  const items=WRITEUPS.filter(w=>{
    if(q && !`${w.title} ${w.abstract} ${(w.tags||[]).join(' ')}`.toLowerCase().includes(q)) return false;
    if(type && w.type!==type) return false;
    if(sol && w.sol!==sol) return false;
    if(status && w.status!==status) return false;
    return true;
  });

  const list=document.getElementById('wuList');
  if(!items.length){
    list.innerHTML=`<div style="text-align:center;padding:40px;color:var(--text2)">
      <p style="font-size:16px;margin-bottom:8px">No writeups yet</p>
      <p style="font-size:13px">Add writeups in <code>solutions/NNN/writeups/</code> as .md files, then register them in the WRITEUPS array in index.html</p>
    </div>`;
    return;
  }

  list.innerHTML=items.map(w=>{
    const solInfo=w.sol-`<span style="color:var(--accent);font-size:12px">${solLabel(w.sol)}</span>`:'';
    return `<div class="wu-list-item" onclick="openWriteup('${w.id}')">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
        <div>
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:4px">
            <span class="wu-type-badge wu-type-${w.type}">${w.type}</span>
            <span class="badge badge-${w.status==='published'-'breakthrough':w.status==='review'-'promising':'limited'}" style="font-size:10px">${w.status}</span>
            ${solInfo}
          </div>
          <div style="font-size:16px;font-weight:600;margin-bottom:4px">${w.title}</div>
          <div style="font-size:13px;color:var(--text2)">${w.abstract||''}</div>
        </div>
        <div style="color:var(--text2);font-size:12px;white-space:nowrap">${w.date}</div>
      </div>
    </div>`;
  }).join('');
}

function openWriteup(id){
  const w=WRITEUPS.find(x=>x.id===id);if(!w) return;
  const reader=document.getElementById('wuReader');
  reader.classList.remove('hidden');
  reader.className=`wu-reader wu-style-${w.type}`;

  const solInfo=w.sol-`<span style="color:var(--accent)">${solLabel(w.sol)}</span> | `:'';
  const tagHtml=(w.tags||[]).map(t=>`<code style="font-size:11px">${t}</code>`).join(' ');

  function renderBody(md){
    reader.innerHTML=`
      <div class="wu-reader-head">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
          <div>
            <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px">
              <span class="wu-type-badge wu-type-${w.type}">${w.type}</span>
              <span class="badge badge-${w.status==='published'-'breakthrough':w.status==='review'-'promising':'limited'}">${w.status}</span>
            </div>
            <h2 style="border:none;padding:0;margin:0;font-size:24px">${w.title}</h2>
            <div style="color:var(--text2);font-size:13px;margin-top:6px">${solInfo}${w.date} | ${tagHtml}</div>
          </div>
          <button class="filter-btn" onclick="document.getElementById('wuReader').classList.add('hidden')" style="font-size:16px;padding:4px 10px">&times;</button>
        </div>
      </div>
      <div class="wu-reader-body">${mdToHtml(md)}</div>`;
    reader.querySelectorAll('.katex-render').forEach(el=>{
      try{katex.render(el.dataset.tex,el,{throwOnError:false,displayMode:el.dataset.display==='true'})}catch(e){el.textContent=el.dataset.tex}
    });
    reader.querySelectorAll('pre code').forEach(b=>hljs.highlightElement(b));
    reader.scrollIntoView({behavior:'smooth',block:'start'});
  }

  // Priority: 1) WRITEUP_CONTENT (built from .md), 2) fetch file, 3) embedded content
  const builtContent = (typeof WRITEUP_CONTENT !== 'undefined') && WRITEUP_CONTENT[id];
  if(builtContent){
    renderBody(builtContent);
  } else if(w.file){
    reader.innerHTML='<div style="padding:40px;text-align:center;color:var(--text2)">Loading...</div>';
    fetch(w.file).then(r=>{
      if(!r.ok) throw new Error(r.status);
      return r.text();
    }).then(md=>renderBody(md))
    .catch(()=>renderBody(w.content||'*Could not load. Run:* `python build_writeups.py` *to rebuild.*'));
  } else {
    renderBody(w.content||'*No content.*');
  }
}

// ============================================================
// INIT
// ============================================================
renderHeader();populateFilters();renderSolutions();renderExp();renderFailed();renderTimeline();renderRM();renderWriteups();renderTodos();buildOverviewChart();
// Init column sorting on all static tables
initTableSort();
