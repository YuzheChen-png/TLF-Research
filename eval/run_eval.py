"""eval/run_eval.py

Simple eval entrypoint for TLF-Research.

This script is a reproducible, dependency-light skeleton you can extend to
plug into your real model / inference code. It reads a JSONL dataset, runs
inference for each example, and writes one JSON object per input to the
specified output JSONL file. Each output object contains a top-level
"metrics" dict so `eval/run_evaluation.sh` can aggregate results.

Usage (example):
  python -m eval.run_eval \
    --dataset data/financial_test_suite.jsonl \
    --model gpt-4-base \
    --output eval/results/gpt4_baseline.run1.jsonl \
    --seed 42 --batch-size 8 --num-workers 4

Notes:
- The file contains a lightweight "mock" backend so it runs without an LLM.
  Replace `inference_for_example()` with calls to your actual model or
  provider SDK.
- Expected dataset format (JSONL): each line is a JSON object. Typical keys:
  - id        : unique id for the example (optional, will use line number)
  - input     : text prompt or combined documents to feed the model
  - references: (optional) ground-truth answers / labels for metric computation

Output format (JSONL): each line is a JSON object with at least the fields:
  - id
  - input
  - prediction
  - metrics: { logical_accuracy: float, hallucination: float, ... }

"""

import argparse
import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional

try:
    import numpy as np
except Exception:
    np = None


def set_seed(seed: int) -> None:
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)


def read_jsonl(path: str):
    with open(path, 'r', encoding='utf-8') as fh:
        for i, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # Skip or raise depending on strictness
                raise
            # Ensure there's an id
            if 'id' not in obj:
                obj['id'] = f'line-{i}'
            yield obj


def inference_for_example(example: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    """Replace this function with your real inference logic.

    The current implementation is a deterministic, dependency-free fallback:
    - If example has 'references' (string or list), returns the first reference as the prediction.
    - Otherwise returns a short mock answer based on the input length.
    - If model_name contains '+tlf', appends a marker to indicate TLF was applied.
    """
    inp = example.get('input') or example.get('prompt') or ''
    refs = example.get('references')

    # Derive a mock prediction
    if refs:
        if isinstance(refs, list) and len(refs) > 0:
            pred = refs[0]
        elif isinstance(refs, str):
            pred = refs
        else:
            pred = 'mock_answer'
    else:
        # Create a deterministic mock from the input
        snippet = (inp.strip().split('\n', 1)[0])[:80]
        pred = f'MOCK_ANSWER[{len(inp)}]_for:"{snippet}"'

    # If model_name indicates TLF, pretend we adjusted the prediction
    if '+tlf' in model_name:
        pred = f"{pred} [TLF_ADJUSTED]"

    # Simple confidence heuristic
    confidence = 0.9 if '+tlf' in model_name else 0.6

    return {
        'prediction': pred,
        'confidence': confidence,
    }


def compute_simple_metrics(example: Dict[str, Any], prediction: str) -> Dict[str, float]:
    """Compute simple placeholder metrics.

    - logical_accuracy: 1.0 if prediction equals first reference exactly, else 0.0
    - hallucination: 0.0 if prediction tokens overlap with any reference tokens, else 1.0

    Replace these with task-appropriate automatic metrics or human-annotation hooks.
    """
    refs = example.get('references')
    if refs:
        if isinstance(refs, list):
            first_ref = refs[0] if refs else ''
        elif isinstance(refs, str):
            first_ref = refs
        else:
            first_ref = ''
    else:
        first_ref = ''

    logical_accuracy = 0.0
    hallucination = 1.0

    try:
        if first_ref and prediction.strip() == first_ref.strip():
            logical_accuracy = 1.0
        # token overlap heuristic
        ref_tokens = set(first_ref.split()) if first_ref else set()
        pred_tokens = set(prediction.split())
        if ref_tokens and pred_tokens & ref_tokens:
            hallucination = 0.0
    except Exception:
        # keep defaults on any error
        pass

    return {
        'logical_accuracy': float(logical_accuracy),
        'hallucination': float(hallucination),
    }


def worker_process(example: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    result = {
        'id': example.get('id'),
        'input': example.get('input') or example.get('prompt') or '',
    }

    inf = inference_for_example(example, model_name)
    pred = inf.get('prediction')
    result['prediction'] = pred

    # attach any inference-provided fields (confidence, etc.)
    if 'confidence' in inf:
        result['confidence'] = float(inf['confidence'])

    # compute metrics (placeholder)
    metrics = compute_simple_metrics(example, pred)
    result['metrics'] = metrics

    # include any metadata from example if present
    if 'meta' in example:
        result['meta'] = example['meta']

    return result


def write_jsonl(path: str, objects):
    with open(path, 'w', encoding='utf-8') as fh:
        for obj in objects:
            fh.write(json.dumps(obj, ensure_ascii=False) + '\n')


def parse_args(argv=None):
    p = argparse.ArgumentParser(description='Run evaluation for TLF-Research')
    p.add_argument('--dataset', required=True, help='Path to dataset JSONL')
    p.add_argument('--model', required=True, help='Model identifier (string)')
    p.add_argument('--output', required=True, help='Path to write JSONL outputs')
    p.add_argument('--seed', type=int, default=42, help='Random seed')
    p.add_argument('--batch-size', type=int, default=8)
    p.add_argument('--num-workers', type=int, default=1)
    p.add_argument('--max-examples', type=int, default=None, help='Limit number of examples (for quick tests)')
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    set_seed(args.seed)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    examples = list(read_jsonl(args.dataset))
    if args.max_examples:
        examples = examples[: args.max_examples]

    results = []

    if args.num_workers and args.num_workers > 1:
        with ThreadPoolExecutor(max_workers=args.num_workers) as ex:
            futures = {ex.submit(worker_process, examp, args.model): examp for examp in examples}
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    results.append(res)
                except Exception as e:
                    # on worker error, write a minimal error object
                    examp = futures[fut]
                    results.append({'id': examp.get('id'), 'error': str(e)})
    else:
        for examp in examples:
            try:
                res = worker_process(examp, args.model)
                results.append(res)
            except Exception as e:
                results.append({'id': examp.get('id'), 'error': str(e)})

    write_jsonl(args.output, results)
    print(f'Wrote {len(results)} results to {args.output}', file=sys.stderr)


if __name__ == '__main__':
    main()
