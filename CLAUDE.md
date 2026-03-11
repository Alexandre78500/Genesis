# Autoresearch Lab

## Concept

Autonomous AI research loop by Andrej Karpathy. An AI agent modifies neural network training code, runs 5-min experiments on local GPU, measures if the model improved, keeps wins, discards losses, repeats. Overnight, ~100 experiments run autonomously.

Original repo: https://github.com/karpathy/autoresearch
macOS fork (Apple Silicon): https://github.com/miolini/autoresearch-macos

## Hardware

- Mac Mini M4, 16GB unified memory
- GPU: Apple Silicon, 10 cores, MPS/Metal backend
- No NVIDIA/CUDA — the macOS fork replaces FlashAttention-3 with PyTorch built-in equivalents

## Key files

- `train.py` — all training code in one file. Model architecture, optimizer, training loop. This is the only file the agent modifies. ~630 lines Python.
- `program.md` — instructions for the AI agent. The "mission briefing". Tells the agent how to behave, what to try, what to avoid.
- `prepare.py` — downloads dataset (FineWeb) and trains tokenizer. Run once.
- `analysis.ipynb` — Jupyter notebook that visualizes experiment progress over time.
- `results.tsv` — auto-generated log of every experiment with scores.

## Model

- 11.5M parameters (tiny GPT)
- depth=4, n_embd=256, vocab_size=8192
- Trained on FineWeb (web text, English)
- Not a chatbot — a text predictor. Can sample semi-coherent text after training.

## Metric

`val_bpb` (validation bits per byte). Lower = smarter model. Vocabulary-independent so different architectures are fairly compared. Baseline ~0.99, improvements push it down.

## The experiment loop

1. Agent reads `program.md` and understands the codebase
2. Agent modifies `train.py` (architecture, hyperparameters, optimizer, etc.)
3. Training runs for exactly 5 minutes on local GPU
4. `val_bpb` is measured
5. If improved → git commit. If not → git checkout (revert)
6. Agent plans next experiment based on results history
7. Repeat

## M4 16GB constraints

- depth=4 is default. Going above 6-8 risks OOM.
- First run is slow (~8 min) due to PyTorch kernel compilation. Subsequent runs are faster.
- ~20-25 training steps per 5-min experiment
- ~12 experiments/hour, ~100 overnight
- If OOM: reduce DEPTH, TOTAL_BATCH_SIZE, or MAX_SEQ_LEN

## Agent

Claude Code with Opus. The agent is the researcher (reads code, thinks, decides what to change). The GPU is the lab (runs the actual training). Both are needed.
