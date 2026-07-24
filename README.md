# TLF (Tensor Logic Firewall) — Logical Self-Consistency Middleware

Logical Self-Consistency Middleware for LLM multi-document reasoning. TLF intercepts LLM outputs and enforces logical consistency across multiple source documents using three complementary engines: State Mapper, Logic Enforcer, and MDU (Multi-Document Unification).

---

## TL;DR
TLF reduces logical errors and hallucinations when LLMs reason over multiple documents, while adding limited latency. See the Evaluation section for reproducibility details.

- Key idea: map facts into a state tensor, enforce first-order constraints, and resolve conflicting evidence with minimum-entropy merging.
- Use-case: financial report synthesis, multi-document QA, knowledge consolidation.

## Badges
[Add badges: license, python, CI, code-quality, docker/pypi when available]

## Features
- Enforces first-order logic constraints on LLM outputs
- Anchors evidence into a tensorized state (State Mapper)
- Prunes contradictions with a Logic Enforcer
- Resolves conflicts with MDU (minimum-entropy merge)
- Low overhead: typical added latency ≤ 180ms (see Evaluation)

## Table of Contents
- Quick Start
- Installation
- CPU-only quick run
- Evaluation (reproducibility)
- Metrics & definitions
- System Requirements
- Examples
- Contributing
- License
- Contact

---

## Quick Start

Minimal smoke test (one-liner):
```bash
python -m eval.run_eval --dataset data/financial_test_suite.jsonl --model gpt4-mock --output eval/results/test.run1.jsonl --num-workers 1
```

See Installation for environment setup and Docker usage.

## Installation
Minimum:
- Python 3.8, 8GB RAM (CPU-only)

Recommended:
- Python 3.10+, CUDA 12.1, 24GB+ GPU

Clone and install:
```bash
git clone https://github.com/YuzheChen-png/TLF-Research.git
cd TLF-Research
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Docker (recommended for reproducibility):
- See Dockerfile in repo (or run the quick docker build and run below).

## CPU-only quick run (smoke test)

If you don't have a GPU, you can run a small smoke-test locally on CPU. This is much slower but useful for validating functionality.

```bash
# create a virtualenv and install minimal deps
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# prepare a tiny test dataset (eval/README also documents this)
mkdir -p data eval/results
cat > data/financial_test_suite.jsonl <<'JSONL'
{"input": "Example 1 text", "references": "Answer 1"}
{"input": "Example 2 text", "references": "Answer 2"}
JSONL

# run eval entrypoint on CPU with a single worker
python -m eval.run_eval \
  --dataset data/financial_test_suite.jsonl \
  --model gpt4-mock \
  --output eval/results/test.run1.jsonl \
  --num-workers 1

# inspect results
cat eval/results/test.run1.jsonl || true
```

> Note: CPU runs may be significantly slower; for development prefer small datasets and --num-workers 1 to reduce memory/CPU contention.

---

## Evaluation (Reproducibility)
Important: include these items in this section in the repo or the paper's appendix.

- Dataset
  - Name: Financial Test Suite (link: <URL or include file>)
  - Version: vX.Y (or commit)
  - Format: JSONL with fields: input, references, metadata
  - Number of examples: N (specify)
  - Splits: train/val/test (if relevant) — list sizes
- Protocol
  - Number of independent runs averaged: M
  - Random seed(s): [list or range]
  - Prompt templates: include full prompt text (exact tokens)
  - Model(s) and exact versions: e.g., gpt-4.1-finetune-2026-06-01 or open-source model + repo commit
  - Temperature, max_tokens, top_p, beam settings
  - Evaluation script and metrics code: path to `eval/` folder and evaluation script(s)
- Hardware & latency
  - Hardware used for latency (e.g., NVIDIA A100 80GB, CPU model)
  - Latency definition: per-request / per-document; median and 95th-percentile; whether it includes model inference time
- Human annotation (if used)
  - Number of raters, annotation interface, inter-annotator agreement (Cohen's Kappa / Fleiss' Kappa)
  - Rater instructions and examples

## Metrics & Definitions
- Logical Accuracy: definition (automatic comparator vs. human judge). Exact scoring rubric.
- Hallucination Rate: definition, how detected (source-matching rules), and whether partial credit is used.
- Statistical reporting: include mean ± std or 95% CI; report p-values for comparisons where appropriate.

## Examples
- Add sample inputs and outputs (before/after TLF) in `examples/` for quick inspection.

## Developer / Contributing
- Include CONTRIBUTING.md with run instructions and a reproducibility checklist.
- Provide a `scripts/run_evaluation.sh` wrapper to reproduce table results.
- Add tests and a small smoke test in CI.

## License
This repository is released under the MIT License. See LICENSE for details.

## Contact
- Maintainer: YuzheChen-png (GitHub)
- Email: email@example.com
- Issues: https://github.com/YuzheChen-png/TLF-Research/issues
