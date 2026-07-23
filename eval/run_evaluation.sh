#!/usr/bin/env bash
# eval/run_evaluation.sh
# Reproducible evaluation script skeleton for TLF-Research
# Usage: bash eval/run_evaluation.sh [options]

set -euo pipefail

# Default configuration - change as needed
DATASET_PATH="data/financial_test_suite.jsonl"
OUTPUT_DIR="eval/results"
MODEL_BASE="gpt-4-base"         # placeholder name for base LLM
MODEL_TLF="gpt-4-base+tlf"     # placeholder name for LLM with TLF
RUNS=3                           # number of runs to average
SEED=42
BATCH_SIZE=8
NUM_WORKERS=4
PYTHON=python3

mkdir -p "$OUTPUT_DIR"

echo "Starting evaluation"
echo "Dataset: $DATASET_PATH"
echo "Output dir: $OUTPUT_DIR"

echo "Preparing environment variables..."
export TLF_EVAL_SEED=$SEED

# Function to run a single experiment configuration
run_experiment() {
  local model="$1"
  local run_id="$2"
  local suffix="$3"
  local out_file="$OUTPUT_DIR/${model//\//_}.run${run_id}${suffix}.jsonl"

  echo "Running model=$model run=$run_id -> $out_file"

  # Placeholder command: replace with your actual evaluation entrypoint
  # Example: the eval.run_eval module should accept dataset, model, output, seed, batch size
  $PYTHON -m eval.run_eval \
    --dataset "$DATASET_PATH" \
    --model "$model" \
    --output "$out_file" \
    --seed "$SEED" \
    --batch-size "$BATCH_SIZE" \
    --num-workers "$NUM_WORKERS"

  echo "Finished $out_file"
}

# Run baseline (no TLF)
for ((i=1;i<=RUNS;i++)); do
  run_experiment "$MODEL_BASE" "$i" ""
done

# Run with TLF enabled
for ((i=1;i<=RUNS;i++)); do
  run_experiment "$MODEL_TLF" "$i" ".tlf"
done

# Aggregate results
AGG_FILE="$OUTPUT_DIR/aggregated_metrics.json"
echo "Aggregating results to $AGG_FILE"

# Placeholder aggregation step: adjust to the format produced by eval.run_eval
# The aggregation script should compute mean/std or confidence intervals for metrics
if command -v $PYTHON >/dev/null 2>&1; then
  $PYTHON - <<'PY'
import json,glob,sys,os
from statistics import mean,stdev

out_dir = os.environ.get('OUTPUT_DIR', 'eval/results')
files = sorted(glob.glob(out_dir + '/*.jsonl'))
metrics = {}

for f in files:
    name = os.path.basename(f)
    # Expect each jsonl to have one JSON object per example with a top-level 'metrics' dict
    vals = []
    with open(f) as fh:
        for line in fh:
            obj = json.loads(line)
            if 'metrics' in obj:
                vals.append(obj['metrics'])
    if not vals:
        continue
    # compute simple averages per-file
    avg = {}
    keys = set().union(*(v.keys() for v in vals))
    for k in keys:
        arr = [v.get(k) for v in vals if v.get(k) is not None]
        if not arr:
            continue
        try:
            avg[k] = {
                'mean': sum(arr)/len(arr),
                'std': (stdev(arr) if len(arr) > 1 else 0.0),
                'n': len(arr)
            }
        except Exception:
            avg[k] = {'example_values': arr[:5]}
    metrics[name] = avg

with open(os.path.join(out_dir,'aggregated_metrics.json'),'w') as fo:
    json.dump(metrics,fo,indent=2)
print('Aggregation written to', os.path.join(out_dir,'aggregated_metrics.json'))
PY
else
  echo "Python not found; please run aggregation manually."
fi

echo "Evaluation complete. Results are in $OUTPUT_DIR"

echo "Next steps suggestions:"
echo " - Add eval/run_eval.py entrypoint that runs model inference and emits one JSON object per input with a 'metrics' dict."
echo " - Upload raw outputs and logs to eval/outputs or a cloud storage for reproducibility."

echo "Done."
