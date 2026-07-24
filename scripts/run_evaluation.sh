#!/usr/bin/env bash
set -euo pipefail

# Example reproducibility wrapper. Edit variables below before running.
DATASET=data/financial_test_suite.jsonl
OUTPUT_DIR=eval/results
MODEL=gpt4-mock
NUM_WORKERS=1
SEED=42

mkdir -p "${OUTPUT_DIR}"
python -m eval.run_eval \
  --dataset "${DATASET}" \
  --model "${MODEL}" \
  --output "${OUTPUT_DIR}/test.run1.jsonl" \
  --num-workers "${NUM_WORKERS}" \
  --seed "${SEED}"
# Add post-processing / metric computation commands here
