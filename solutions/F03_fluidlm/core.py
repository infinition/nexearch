"""
F03 - FluidLM - Core Reference
================================
Transformer-free language model using reaction-diffusion PDEs.

The full implementation is in source/:
    source/text_models.py  - Architecture (FluidNet, FluidLayer, SelectiveSSM, SwiGLU)
    source/train_engine.py - Training loop with curriculum scheduling
    source/web_app.py      - Streamlit real-time dashboard
    source/config.json     - Hyperparameters (hot-reloadable)

To train:
    cd source/
    python prepare_data.py          # Download TinyStories
    python launch_lab.py            # Train + dashboard at localhost:8501

To use the model:
    from source.text_models import FluidNet
    model = FluidNet(config)
    logits = model(token_ids)       # O(N) forward pass, no KV-cache

Paper: paper/fluidlm.pdf (NeurIPS 2025 submission)
Results: results/training_stats.json
"""

import os

SOLUTION_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(SOLUTION_DIR, 'source')
PAPER_DIR = os.path.join(SOLUTION_DIR, 'paper')

# Key numbers
PARAMS_TOTAL = 44_200_000
PARAMS_EMBEDDING = 25_700_000
PARAMS_CORE = PARAMS_TOTAL - PARAMS_EMBEDDING
BEST_LOSS = 10.76        # TinyStories, step 801
VERSION = "4.5.0"
D_MODEL = 512
N_LAYERS = 4
T_STEPS = 6
VOCAB_SIZE = 50_257      # GPT-2 BPE
DILATIONS = [1, 4, 16]   # Multi-scale diffusion
