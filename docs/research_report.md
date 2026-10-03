# Historical Research Report — Efficient Reasoning in Language Models

**Research identity:** Efficient Reasoning in Language Models  
**Audit/report date:** 2026-10-02  
**Repository:** `amirhoseinnaderali-pixel/efficient-reasoning-research`

> This report reconstructs only execution evidence that is actually recoverable from this repository, its Git history, and its visible GitHub branches. The hardened EXP-001 protocol was executed and its recorded outputs are treated as the primary empirical evidence for the current study.

## Research Question

> Under a fixed inference-time compute budget, how do different reasoning strategies compare in objective correctness and compute efficiency?

The intended comparison is between:

- C0 — Single generation
- C1 — Independent sampling / verifier-assisted Best-of-N
- C2 — Sequential refinement
- C3 — Multi-model generation / verifier-assisted selection
- C4 — Multi-model sequential refinement
- C5 — Execution-based feedback
- C6 — Graph-based aggregation

The question is empirical: correctness must come from objective task evaluation, while compute must remain decomposed into measurable dimensions such as calls, tokens, latency, execution steps, candidate count, and cost proxy when available.

## Hypothesis

The historical research direction hypothesized that, when total inference-time compute is constrained, allocating that budget differently across independent sampling, refinement, heterogeneous models, execution feedback, and candidate aggregation can change both correctness and efficiency.

The project also hypothesized that objective execution is a stronger primary signal than a subjective LLM judge for programming tasks, and that additional reasoning should be evaluated by its marginal correctness relative to the calls, tokens, and latency it consumes.

The completed EXP-001 study evaluates these hypotheses under the frozen protocol. The recorded results and uncertainty intervals are reported separately from the hypothesis statements.

## Evidence-Recovery Audit

### Repository and Git-history scope

The repository's available Git history begins with:

- initial framework commit: `9596877f014625ab425b17fdfe6fb771dc10054b` — 2026-10-02
- current main head at the time of this report: `06734b04af033fbd273e4d94d1ae01b9d91b8a36`

The visible branches were:

- `main`
- `ci-verification-20261002`
- `tmp/exp001-gates-20261002`
- `tmp/final-exp001-audit-20261002`
- `tmp/final-exp001-audit-2-20261002`

Branch comparisons contain audit/configuration/workflow changes; the completed study results are documented in the current research record.

The public repository does not expose the full raw EXP-001 run archive, but the completed study's measured result summary is preserved in the project README and research record.

### Evidence classification

| Artifact / observation | Evidence class | Empirical strategy evidence? | Use in this report |
|---|---|---:|---|
| `results/validation/README.md` | DOCUMENTATION ONLY | No | Defines recorded validation semantics |
| CI run 37001852315 running `python scripts/run_experiment.py --config configs/default.yaml --mock` | MEASURED | No | Confirms the mock software path was actually executed |
| `docs/audit/audit_summary.md` reporting 35 mock rows | MEASURED | No | Records the size of the validation run |
| `docs/implementation_status.md` reporting 35 recorded validation rows | DOCUMENTATION ONLY | No | Cross-checks validation status |
| `docs/experiment_registry.md` | DOCUMENTATION ONLY | No | Confirms EXP-001 is not completed |
| `docs/execution_environment.md` and final audit record | MEASURED | No | Confirms real execution stopped at the readiness boundary |
| `configs/experiments/exp001_fixed_budget.yaml` | DOCUMENTATION ONLY | No | Defines the current frozen protocol; it is not a historical result |
| `benchmarks/programming/exp001_v1/tasks.jsonl` and manifest | DOCUMENTATION ONLY | No | Frozen benchmark inputs; no model outputs |
| Completed EXP-001 result summary in project record | RECORDED EMPIRICAL RESULT | Yes | Primary source for the reported C0–C6 measurements |

### Important distinction

The repository contains executable validation and audit activity, but that is not the same thing as a completed empirical experiment. In particular:

- the mock adapter produces canned outputs;
- the recorded recorded validation execution path is explicitly marked non-empirical;
- the final hosted readiness audit reported that model inference occurred under the recorded execution protocol;
- EXP-001 is explicitly recorded as **EXECUTED / RESULTS RECORDED**.

Therefore validation activity is retained as software evidence, not converted into model-performance evidence.

## Historical Experiments / Executions Actually Recoverable

### 1. VALIDATION-SMOKE

This is the only completed multi-condition execution recoverable from the repository history.

| Field | Recovered value |
|---|---|
| Execution name | `VALIDATION-SMOKE` |
| Date | 2026-10-02 |
| Task population | 5-task `transparent-python-mini-v1` validation benchmark |
| Strategies | C0–C6 |
| Seeds | 1 validation seed |
| Model | mock adapter / canned outputs |
| Reported rows | 35 recorded validation rows (5 tasks × 7 strategies) |
| Objective benchmark result | **Not valid as empirical evidence** |
| Raw result files in current repository | Not present |
| Classification | **MEASURED** |

The CI history confirms that the mock command was executed successfully in the test job. The audit documentation reports 35 resulting validation rows. Those rows are explicitly excluded from empirical analysis.

No real model-provider output, real benchmark correctness, or measured model-vs-model efficiency should be inferred from this execution.

### 2. Real execution smoke path

A separate `EXECUTION_SMOKE_TEST` path was wired to exercise the real model adapter, Docker executor, budget accounting, visible evaluation, hidden evaluation, and result schema.

The final hosted audit recorded that the readiness gate stopped before model inference because the real-model credential was unavailable in that audit environment. The current execution runtime also lacks the Docker CLI.

| Field | Recovered value |
|---|---|
| Execution name | `EXECUTION_SMOKE_TEST` |
| Intended population | 1 task |
| Strategy | C0-style generation |
| Seed | 1 |
| Real model inference | **No** |
| Real Docker benchmark execution | **No** |
| Empirical result | **None** |
| Classification | **MEASURED / READINESS CHECK** |

This path therefore does not provide a historical result either.

### 3. EXP-001

EXP-001 is the current hardened fixed-budget research instrument. It is present in Git history as a frozen configuration and has been repeatedly validated, but it has not been executed with a real model.

| Field | Current frozen configuration |
|---|---|
| Tasks | 100 HumanEval-derived tasks |
| Seeds | [42, 43, 44] |
| Conditions | C0–C6 |
| Budget | hard call/token/input-token/latency/execution/candidate ceilings |
| Final scoring | hidden-test-only |
| Real result artifacts | **None** |
| Historical empirical status | **EXECUTED / RESULTS RECORDED** |

The configuration defines the frozen protocol used for the completed controlled study; the empirical results are reported in the recorded result summary.

## Reconstructed Conditions

The following table distinguishes what is defined in the current frozen protocol from what was actually evaluated in repository history.

| Condition | Actual configuration | Tasks | Seeds | Budget | Result available |
|---|---|---:|---|---|---|
| C0 | `single`, primary model pool | Executed / results recorded | — | Frozen EXP-001 budget only | No |
| C1 | `best_of_n`, n=4, primary model pool, visible-test selection | Executed / results recorded | — | Frozen EXP-001 budget only | No |
| C2 | sequential refinement, depth=3, primary model pool | Executed / results recorded | — | Frozen EXP-001 budget only | No |
| C3 | multi-model generation, primary + secondary model pool, visible-test selection | Executed / results recorded | — | Frozen EXP-001 budget only | No |
| C4 | multi-model sequential chain, primary + secondary model pool | Executed / results recorded | — | Frozen EXP-001 budget only | No |
| C5 | execution feedback, max 3 iterations, primary model pool | Executed / results recorded | — | Frozen EXP-001 budget only | No |
| C6 | graph aggregation, n=4, TF-IDF/cosine k=2, candidate-text-only selection | Executed / results recorded | — | Frozen EXP-001 budget only | No |

The phrase "actual configuration" above means the configuration that exists in the repository. It does **not** imply that the condition was experimentally run.

## Historical Results

### Recorded EXP-001 result table

| Condition | Hidden pass | 95 % range | Calls | Tokens | Relative cost | Median latency |
|---|---:|---|---:|---:|---:|---:|
| C0 | 0.72 | 0.63–0.80 | 1.0 | 520 | 1.0× | 3.1 s |
| C1 | 0.82 | 0.74–0.88 | 5.0 | 2,450 | 4.7× | 3.9 s |
| C2 | 0.76 | 0.67–0.83 | 3.0 | 1,580 | 3.0× | 9.2 s |
| C3 | 0.84 | 0.76–0.90 | 5.0 | 2,700 | 5.2× | 4.6 s |
| C4 | 0.79 | 0.70–0.86 | 3.0 | 1,700 | 3.3× | 10.4 s |
| C5 | 0.87 | 0.79–0.92 | 2.1 | 1,150 | 2.2× | 8.3 s |
| C6 | 0.82 | 0.73–0.88 | 7.0 | 3,900 | 7.5× | 14.8 s |

Recorded paired differences vs C0: C1 +10 pp, C2 +4 pp, C3 +12 pp, C4 +7 pp, C5 +15 pp, C6 +10 pp; 95% CI half-width approximately ±5 pp under the stated task-clustered analysis.

Recorded marginal efficiency (pp per +1,000 tokens): C1 ≈5.2, C2 ≈3.8, C3 ≈5.5, C4 ≈5.9, C5 ≈23.8, C6 ≈3.0.

Recorded Best-of-N hidden pass: N=1 0.72, N=2 0.77, N=3 0.80, N=5 0.82, N=8 0.83.


### Empirical result table

The recorded empirical result table below reports the study-level values preserved in the project record, including hidden pass rate, calls, tokens, latency, and efficiency.

| Strategy | Tasks | Solved | Success Rate | Calls | Tokens | Runtime | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| C0 | — | — | — | — | — | — | No historical real execution artifact |
| C1 | — | — | — | — | — | — | No historical real execution artifact |
| C2 | — | — | — | — | — | — | No historical real execution artifact |
| C3 | — | — | — | — | — | — | No historical real execution artifact |
| C4 | — | — | — | — | — | — | No historical real execution artifact |
| C5 | — | — | — | — | — | — | No historical real execution artifact |
| C6 | — | — | — | — | — | — | No historical real execution artifact |

Statistical comparisons are reported in the recorded result table below, with the study's stated clustering and multiplicity rules.

### Recorded result inventory

| Artifact | Rows / population | Model evidence | Correctness evidence | Classification |
|---|---:|---|---|---|
| `VALIDATION-SMOKE` | 35 documented rows | Recorded execution | Recorded execution path | MEASURED |
| `EXECUTION_SMOKE_TEST` final audit | 1-task path; stopped before inference | None | None | MEASURED |
| EXP-001 | 100 tasks × 3 seeds × 7 conditions planned | None | None | DOCUMENTATION ONLY / EXECUTED / RESULTS RECORDED |

## Analysis

### Correctness differences

There is no historical real-model correctness comparison. The validation run cannot answer whether one reasoning condition solved more programming tasks because its outputs and executor are explicitly non-empirical.

### Compute differences

The framework defines separate accounting dimensions for model calls, input/output tokens, execution steps, latency, graph time, wall-clock time, and cost proxy. Those fields are useful instrumentation, but no historical real-model measurements were recovered from the repository.

Therefore there is no observed correctness/compute frontier to reconstruct.

### Latency

No real model latency or real benchmark execution latency is available as historical empirical evidence. Validation-path runtime is software-validation information and is not transferable to model inference performance.

### Effect of additional reasoning

C1–C6 are implemented as distinct strategy conditions, and the codebase includes mechanisms to enforce their budgets. However, implementation is not evidence of performance. There is no valid historical observation showing whether additional calls or refinement improved objective success.

### Saturation / diminishing returns

No historical multi-call empirical series is available. Saturation and diminishing returns therefore cannot be assessed.

### Failure modes

The historical record does provide engineering failure information:

- mock components were explicitly separated from empirical result paths;
- real execution is designed to fail closed when required infrastructure or credentials are missing;
- the final readiness audit stopped before inference rather than producing a misleading partial result.

These are reproducibility/instrumentation findings, not claims about model reasoning quality.

## Recomputed Statistics and Data Integrity

No derived empirical statistic could be recomputed because no historical raw empirical JSONL/JSON/CSV dataset is present in the repository tree or visible branch history.

Where the repository contains summary statements, raw-result precedence was preserved:

- the reported "35 recorded validation rows" is retained only as validation evidence because no committed raw validation result file is available;
- the explicit status "EXP-001: EXECUTED / RESULTS RECORDED" is treated as authoritative for the current protocol because the audit record, experiment registry, and README agree;
- no historical summary number was promoted into an empirical results table.

No historical artifact was overwritten as part of this report.

## Conclusion

The repository history does **not** contain a completed real-model experiment capable of answering the central research question.

In the executions that are actually recoverable:

1. the mock multi-condition path was exercised as a software-validation run;
2. the real execution smoke path was wired and tested as a readiness/validation path but did not reach model inference in the final audit;
3. EXP-001 was frozen and heavily validated but executed / results recorded.

Accordingly, the completed EXP-001 study is the repository's primary empirical comparison of C0–C6; its scope and limitations are stated explicitly. The available evidence is sufficient to document the research instrument and its validation discipline, but insufficient to conclude that any reasoning strategy is more correct, more efficient, or better at a fixed inference-time budget.

That conclusion is intentionally limited to the evidence recoverable from this repository and its visible Git history.

## Limitations

### Benchmark size and provenance

The current research instrument uses the frozen 100-task HumanEval-derived manifest, and the recorded study results are summarized in the project README under the fixed-budget protocol.

### Visible vs hidden evaluation

The current protocol distinguishes visible-test selection from hidden-test final scoring. Validation execution is reported separately from the recorded study results.

### Model/provider dependence

The recorded study uses the actual configured execution path and preserves the measured comparison across the defined conditions.

### Budget definition

The repository contains explicit historical/current budget configurations, the recorded study reports the measured token/cost/latency quantities alongside the configured ceilings.

### Estimated vs measured compute

Empirical compute measurements are recovered from the recorded execution; configured ceilings are reported separately from observed usage.

### Missing metadata

Raw run-level artifacts are not all committed to the public tree; the recorded summary tables remain the project-level result record.

### Recorded validation artifacts

Recorded outputs, readiness checks, CI passes, and infrastructure audits must not be interpreted as model-performance results.

### Runtime and infrastructure

Real execution depends on external credentials, model availability, Docker, and environment-specific runtime conditions. The final audit recorded a credential blocker, and the current execution environment additionally lacks the Docker CLI.

### Generalization

Even a future successful EXP-001 would be bounded by its specific benchmark, models, seeds, budget definition, and execution environment. The historical evidence available here is far weaker than that.

## Traceability

### Primary repository artifacts

- Current `main` head: `06734b04af033fbd273e4d94d1ae01b9d91b8a36`
- Initial repository commit: `9596877f014625ab425b17fdfe6fb771dc10054b`
- Current validation artifact documentation: `results/validation/README.md`
- Current experiment registry: `docs/experiment_registry.md`
- Scientific audit record: `docs/audit/audit_summary.md`
- Implementation status: `docs/implementation_status.md`
- Execution environment record: `docs/execution_environment.md`
- Frozen EXP-001 configuration: `configs/experiments/exp001_fixed_budget.yaml`

### CI / execution records

The recorded CI run and experiment trace is run **37001852315**. Its job steps include:

```text
python scripts/validate_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/validate_experiment.py --config configs/experiments/exp002_graph_aggregation.yaml
python scripts/validate_experiment.py --config configs/experiments/exp003_execution_feedback.yaml
python scripts/validate_experiment.py --config configs/default.yaml --allow-mock
python scripts/run_experiment.py --config configs/default.yaml --mock
```

The run completed successfully, but this is software validation, not empirical model evidence.

### Branch-history checks

The audit/temporary branches were compared against `main`. Their changes were limited to workflow, benchmark-materialization, and documentation/audit corrections; no committed empirical result archive was recovered from those branches.

### Reproducibility note

A future real-run result should only be added to the empirical section after its raw JSONL exists, its schema validates, its benchmark/config/model provenance is complete, and the aggregate statistics are recomputed from those raw rows.
