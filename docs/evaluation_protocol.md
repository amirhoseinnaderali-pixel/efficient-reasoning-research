# Evaluation Protocol

1. Give the model only the problem and strategy context.
2. Parse candidate code without changing benchmark labels/tests.
3. Use visible tests only for selection/feedback.
4. Report final correctness on hidden tests.
5. Real execution uses Docker with no network, bounded CPU/memory, read-only root, isolated `/tmp`, timeout, and process cleanup.

LLM judges are not primary EXP-001 evidence.
