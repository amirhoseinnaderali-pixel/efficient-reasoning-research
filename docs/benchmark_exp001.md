# EXP-001 Benchmark Specification

## Frozen source

- Canonical source: `openai/human-eval`
- Source file: `data/HumanEval.jsonl.gz`
- Source commit: `6d43fb980f9fee3c892a914eda09951f772ad10d`
- Canonical archive SHA-256: `b796127e635a67f93fb35c04f4cb03cf06f38c8072ee7cee8833d7bee06979ef`
- Source task count: 164

## Selection

The EXP-001 subset contains exactly 100 source tasks selected deterministically in source order within a declared category quota. Tasks with fewer than two top-level assertions are excluded because the experiment requires a deterministic visible/hidden assertion split.

The difficulty field is `unlabeled_source`; the source does not provide a defensible difficulty label and no model-created difficulty label is used.

## Distribution

| Category | Count |
|---|---:|
| arrays_lists | 26 |
| strings | 26 |
| arithmetic | 12 |
| sorting | 12 |
| parsing | 6 |
| dynamic_programming | 4 |
| general | 3 |
| recursion | 3 |
| graph | 3 |
| hash_maps | 3 |
| greedy | 1 |
| searching | 1 |
| **Total** | **100** |

## Evaluation split

For every task with `n` top-level assertions:

- visible suite = first `ceil(n/2)` assertions;
- hidden suite = remaining assertions;
- hidden suite is used only for final objective evaluation;
- no strategy or graph selector receives hidden results;
- C1/C3/C5 may use visible execution feedback only because their strategy definitions explicitly permit it.

## Leakage prevention

The model-facing prompt is derived using `strip_doctest_examples_v1`, which removes interactive examples beginning with `>>>` and their immediate expected-output lines. The source oracle is not modified. Real execution verifies source and test hashes before materialization.
