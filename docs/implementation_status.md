# Implementation Status

## Built
- New modular research framework and common strategy interface.
- C0–C6 reasoning strategies.
- Mock, Ollama, OpenAI-compatible, and Google adapters.
- Explicit budgets for calls/tokens/latency/execution/candidates.
- Objective evaluation and Docker sandbox interface.
- Transparent deterministic programming benchmark.
- Graph aggregation baseline.
- JSONL results + analysis scripts.
- EXP-002/EXP-003 config stubs.
- Unit tests and GitHub Actions CI.
- Paper/lineage/reproducibility documentation.

## Reused Concepts
Sequential refinement ← `LLM_reasoning_solve_NQueen_with_no_code` / `codechain`.
Execution feedback ← `Reasoning-Is-All-You-Need` / `multi-agent-react-sandbox`.
Graph aggregation ← `graph_reasoning`.
Benchmark accounting discipline ← DPO benchmark lineage.

## Not Yet Executed
- Real-model EXP-001.
- EXP-002.
- EXP-003.

## Evidence Available
Software tests + mock smoke test only; historical repositories as prior-work artifacts.

## Unsupported Claims
No superiority, SOTA, significance, or benchmark ranking is claimed.

## Next Experiment
After a valid EXP-001 run and replication: graph construction/aggregation ablations under matched budgets.
