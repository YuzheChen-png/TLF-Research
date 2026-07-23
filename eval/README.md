# eval — Reproducibility & Local Testing

This directory contains evaluation helpers for reproducing the results in this repo.

This README documents how to run the local smoke tests and full evaluation scripts (for development and CI).

## Quick local test (step-by-step)

1. Pull latest code

```bash
git pull origin main
cd TLF-Research
```

2. Create a Python virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

(If your project does not have requirements.txt yet, install only what you need for testing: e.g., numpy.)

3. Prepare a tiny test dataset

Create `data/financial_test_suite.jsonl` with a couple of sample lines:

```jsonl
{"input": "Example 1 text", "references": "Answer 1"}
{"input": "Example 2 text", "references": "Answer 2"}
```

4. Run the eval entrypoint directly (fast single-run)

```bash
python -m eval.run_eval \
  --dataset data/financial_test_suite.jsonl \
  --model gpt4-mock \
  --output eval/results/test.run1.jsonl \
  --num-workers 2
```

Expected: `eval/results/test.run1.jsonl` is created and contains one JSON object per input. Each object includes at least:
- `id` (string)
- `input` (string)
- `prediction` (string)
- `metrics` (object with numeric fields, e.g., `logical_accuracy`, `hallucination`)

5. Run the full evaluation harness (baseline + TLF runs + aggregation)

```bash
bash eval/run_evaluation.sh
```

This creates per-run outputs under `eval/results/` and writes `eval/results/aggregated_metrics.json`.

## Notes / Troubleshooting

- If `python -m eval.run_eval` fails with `ModuleNotFoundError`, ensure you run it from the repository root and the `eval` package/module is discoverable (i.e., `eval/run_eval.py` exists and you are executing with the repository root on PYTHONPATH).
- The provided `inference_for_example()` in `eval/run_eval.py` is a placeholder. Replace it with calls to your real model or SDK.
- `eval/run_evaluation.sh` expects `eval/run_eval.py` to exist and accept the CLI arguments shown. Adjust `MODEL_BASE` and `MODEL_TLF` variables inside the script to match your actual model identifiers.
- For large-scale runs, prefer limiting the concurrency or using a backend queue to avoid rate-limiting from remote model APIs.

## Recommended next steps

- Add a `requirements.dev.txt` or update `requirements.txt` to list any evaluation dependencies (e.g., numpy, tqdm).
- Add a Dockerfile for a fully pinned evaluation environment.
- Add a small GitHub Actions workflow that runs the smoke test on push or PR.

If you want, I can create the Dockerfile or the GitHub Actions workflow next.