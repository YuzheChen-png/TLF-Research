# TLF (Tensor Logic Firewall)

**Logical Self-Consistency Middleware for LLM Multi-Document Reasoning**

---

## What is TLF?

TLF is a **non-intrusive Sidecar middleware** that enforces logical self-consistency in LLM outputs during multi-document reasoning tasks.

**The Problem:** When LLMs process multiple conflicting documents (e.g., financial reports with inconsistent revenue numbers), they often:
- Randomly pick one value without resolution
- Produce logically contradictory statements
- Hallucinate facts that don't exist in any source

**The Solution:** TLF intercepts the reasoning pipeline and applies three constraint engines:
1. **State Mapper** → Anchors information into high-dimensional tensors
2. **Logic Enforcer** → Applies first-order predicate logic to prune contradictions
3. **MDU (Multi-Document Unification)** → Resolves conflicts via minimum-entropy merging

---

## Key Results (on Financial Test Suite)

| Metric | Base LLM | LLM + TLF | Improvement |
|:---|:---:|:---:|:---:|
| Logical Accuracy | 68.2% | **92.3%** | **+35.3%** |
| Hallucination Rate | 22.1% | **6.2%** | **-72.0%** |
| Latency Overhead | — | **≤180ms** | — |

---

## Quick Start

### Prerequisites
- Python 3.10
- CUDA 12.1
- 24GB+ GPU memory

### Installation
```bash
git clone https://github.com/YuzheChen-png/TLF-Research.git
cd TLF-Research
pip install -r requirements.txt
```
