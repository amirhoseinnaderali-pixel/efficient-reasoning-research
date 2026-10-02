# Efficient Reasoning in Language Models

### Portfolio status

**REGISTERED — HISTORICAL EMPIRICAL RESULT NOT RECOVERED**

This project is retained as a research-instrument case study. The repository contains a validated C0–C6 experimental framework, but no real-model empirical result set was recoverable from the repository or visible Git history. Mock validation is not treated as empirical evidence.

Research infrastructure for studying how inference-time computational budget should be allocated across reasoning strategies.

## Research Question

> Under a fixed inference-time compute budget, how do different reasoning strategies compare in objective correctness and compute efficiency?

This is an empirical question. No strategy is assumed to be superior before controlled measurement.

---

# EXP-001 — Pre-Execution Projection

> ⚠️ **EXPECTED / PRIOR ONLY — NOT AN EMPIRICAL RESULT**
>
> **EXP-001 has not been executed.** The repository currently contains a validated research instrument, mock validation artifacts, and a frozen 100-task experimental design, but no real-model result set.
>
> Every accuracy statement, ordering, and probability in this section is a **pre-data hypothesis** recorded before execution. It must not be interpreted as measured performance, statistical significance, or an empirical ranking.

**Research identity:** Efficient Reasoning in Language Models  
**Benchmark:** 100-task HumanEval-derived benchmark (`humaneval-stratified-100-v1`)  
**Seeds:** 42, 43, 44  
**Conditions:** C0–C6  
**Projection date:** 2026-10-02

## Executive hypothesis

The central hypothesis is that **objective external feedback — especially code execution and tests — is more valuable than additional self-generated reasoning alone** under a fixed inference budget.

Expected qualitative ordering:

```text
C5 ≳ C3 ≈ C1 > C6 > C0 ≈ C2 ≳ C4
```

This is a mechanistic hypothesis, not a claim about the eventual result.

## Expected cost–correctness frontier

The intended visualization is **relative inference cost** on the horizontal axis, with **improvement over C0** on the vertical axis.

```text
Expected correctness improvement
    ^
    |                 ● C5
    |              ● C3
    |           ● C1
    |
    |                        ● C6
    |         ● C0
    |            ● C2
    |               ● C4
    +------------------------------------> Relative inference cost
          1×          2×        3×      4×
```

This is a schematic prior, not measured data.

## Projected behavior by condition

| Condition | Frozen strategy | Pre-execution expectation | Relative cost | Mechanistic rationale |
|:--|:--|:--|--:|:--|
| **C0** | Single generation | Baseline | **1×** | Reference condition |
| **C1** | Best-of-4 with visible-test selection | **Moderate to strong improvement** | **~4×** | Objective visible-test selection provides an external signal |
| **C2** | Sequential refinement, depth 3 | **Near-zero to modest / possibly negative** | **~3×** | Self-revision can propagate or introduce errors without external feedback |
| **C3** | Multi-model generation + visible-test selection | **Similar to C1, potentially slightly higher** | **~4×** | Model diversity can reduce correlated failures when the selection signal is useful |
| **C4** | Multi-model sequential chain | **Near C2, with error-propagation risk** | **~3–4×** | Later models inherit earlier mistakes without an external correctness oracle |
| **C5** | Execution feedback, up to 3 iterations | **Largest expected improvement** | **~1.5–3×** | The loop observes concrete execution failures and can continue only when useful |
| **C6** | Graph aggregation over candidate text | **Small improvement at most** | **~4× + graph overhead** | Text similarity can organize candidates but does not itself verify correctness |

Actual realized calls, tokens, latency, and execution usage must be measured from run telemetry.

## Why this projection has this shape

### External verification is the key signal

```text
Generated code
      ↓
Execution / visible tests
      ↓
Concrete failure signal
      ↓
Targeted revision
      ↓
Re-execution
```

The projection therefore expects **C5** to exploit the strongest feedback loop.

### Independent sampling has a different advantage

C1 creates multiple alternatives and chooses among them using visible objective feedback:

```text
More candidates
      ↓
Potentially less-correlated errors
      ↓
Better candidate available
      ↓
Objective selection
```

C3 adds model diversity to the same general idea.

### Text-only refinement can waste compute

C2 and C4 receive additional model calls but do not receive the same direct executable signal during the reasoning process. The prior therefore allows little improvement, no improvement, or regression when later stages damage an initially correct candidate.

### Graph aggregation is not the same as verification

C6 can expose structure among candidate texts, but it sees candidate representations rather than actual program execution outcomes. The expected result is therefore modest.

## Statistical resolution

The benchmark contains **100 tasks** and **three paired seeds**.

Near 90% correctness, a simple 100-task accuracy estimate has a standard error of roughly **3 percentage points**, so an uncertainty scale around **±6 percentage points** is plausible before accounting for pairing and other design details.

The analysis should:

- operate on task-level paired outcomes;
- treat seeds as repeated measurements rather than 300 independent tasks;
- use task-clustered bootstrap or an equivalent paired resampling scheme;
- report discordant task counts as well as percentages;
- treat differences around **4–5 percentage points or less** cautiously.

## Main pre-execution predictions

| Claim | Prior / expected belief |
|:--|--:|
| **C5 and C1 outperform C0** | **High** |
| **C5 and C3 are among the highest-performing conditions** | **High** |
| **C2 provides little or no gain over C0** | **Moderate to high** |
| **C4 is close to C2 or below it** | **Moderate** |
| **C6 improves only modestly over C0** | **Moderate** |
| **C1 vs. C3 is statistically unresolved** | **Moderate to high** |
| **C5 is clearly above C0** | **Expected, but not guaranteed** |
| **All conditions remain within ~2 pp of C0** | **Low-probability saturation scenario** |

These are qualitative priors, not calibrated posteriors.

## Four expected patterns

### 1. Frontier separation

The projection expects C5 and C1 to occupy a more favorable correctness–compute region than C2 and C4 because they use a useful external signal.

### 2. Diminishing returns

For C1, the first jump from one candidate to several candidates is expected to be more valuable than subsequent redundant reasoning.

### 3. Ceiling effect

If C0 is already close to the practical ceiling on the HumanEval-derived benchmark, all improvements become harder to observe.

### 4. Visible vs. hidden gap

C1, C3, and C5 use visible execution feedback during selection or refinement, while hidden evaluation is reserved for final scoring. Strong visible performance therefore does not automatically imply an equally large hidden-test gain.

## Important validity threats

- **C1 vs. C5 is not a pure sampling-vs-feedback comparison:** both can use visible execution, but C1 mainly selects among candidates while C5 iteratively revises and retries.
- **C6 does not receive objective verification:** a weak result would primarily inform graph-based organization without executable feedback.
- **Hard budget ceilings:** call, token, latency, and execution exhaustion rates should be reported separately so truncation is not mistaken for strategy weakness.
- **Benchmark contamination:** HumanEval-derived tasks can have nontrivial overlap with model training data, affecting absolute scores.
- **Limited generalization:** the experiment covers Python programming tasks, one frozen benchmark family, a fixed model pool, and one execution environment.

## What would falsify the projection?

The pre-execution hypothesis would be substantially weakened by results such as:

- **C2 significantly outperforming C0**;
- **C6 outperforming C1**;
- **C5 failing to improve on C1 despite similar effective compute**;
- **all conditions remaining within roughly ±2 percentage points of C0**.

A contradiction is a valid scientific outcome; the projection is not meant to be retrofitted after observing the data.

## Pre-Execution Scorecard

Freeze this before real execution:

- [ ] C5 is among the highest-performing conditions
- [ ] C1 clearly improves over C0
- [ ] C2 does not produce a large gain over C0
- [ ] C4 is close to or below C2
- [ ] C6 provides only a modest gain over C0
- [ ] C1 and C3 are difficult to distinguish statistically
- [ ] Execution-backed strategies occupy the favorable correctness–compute region

The scorecard records the prior and must not be edited retrospectively.

## Frozen EXP-001 Structure

| Item | Frozen value |
|:--|:--|
| Benchmark | **100-task `humaneval-stratified-100-v1`** |
| Seeds | **42, 43, 44** |
| Conditions | **C0–C6** |
| Max model calls | **8** |
| Max generated tokens | **9,600** |
| Max input tokens | **40,000** |
| Max latency | **300 s** |
| Max execution steps | **12** |
| Max candidates | **8** |
| Output-token ceiling / call | **1,200** |
| Execution backend | **Docker** |
| Network | **None** |
| Hidden scoring | **Final evaluation only** |
| Real-model execution | **Required** |
| Mock fallback | **Forbidden for EXP-001** |

Condition definitions in the frozen configuration:

```text
C0  single generation
C1  best-of-4
C2  sequential refinement, depth 3
C3  multi-model generation + selection
C4  multi-model sequential chain
C5  execution feedback, up to 3 iterations
C6  graph aggregation, n=4, TF-IDF/cosine k=2
```

The graph condition uses **candidate text only** and does not use objective execution results for its selection.

## Current empirical status

**IMPLEMENTED / SCIENTIFICALLY READY / NOT EXECUTED**

The repository currently demonstrates a validated C0–C6 research instrument, a frozen 100-task benchmark, paired seeds, explicit compute ceilings, visible-selection / hidden-final separation, Docker-based objective evaluation, and reproducibility controls.

It does **not** currently contain real EXP-001 task-level outputs, hidden-test results, measured strategy accuracy, or empirical significance tests.

Therefore this entire section remains a **pre-execution prior**.

## Reproducibility boundary

The authoritative frozen experiment definition is:

```text
configs/experiments/exp001_fixed_budget.yaml
```

The benchmark is:

```text
benchmarks/manifests/exp001_v1.json
benchmarks/programming/exp001_v1/tasks.jsonl
```

Real results should enter:

```text
results/raw/EXP-001/
```

The scientific sequence is:

```text
Pre-execution projection
        ↓
Real EXP-001 run
        ↓
Raw task-level results
        ↓
Validity / provenance audit
        ↓
Paired statistical analysis
        ↓
Empirical conclusion
```

The projection must remain unchanged after results are observed.

---

## Conditions

- **C0** — Single generation
- **C1** — Independent sampling / verifier-assisted Best-of-N
- **C2** — Sequential refinement
- **C3** — Multi-model generation / verifier-assisted selection
- **C4** — Multi-model sequential refinement
- **C5** — Execution-based feedback
- **C6** — Graph-based aggregation

## Historical empirical evidence

The repository history was audited for committed raw runs, JSON/JSONL outputs, CSV tables, logs, plots, experiment configs, and execution records.

**Historical empirical result: none recovered.**

The only completed multi-condition execution recoverable from the repository is the **mock validation path**:

- 5-task validation benchmark
- C0–C6
- 1 validation seed
- mock/canned outputs
- 35 documented validation-only rows

Those rows are **software-validation artifacts, not model or benchmark evidence**. No real-model correctness, token usage, latency, or strategy comparison is claimed from them.

A separate real `EXECUTION_SMOKE_TEST` path was audited, but the final run stopped fail-closed before model inference because the real-model credential was unavailable in the hosted audit; the current execution runtime also lacks Docker CLI access.

See the full evidence audit and traceability record in [`docs/research_report.md`](docs/research_report.md).

## EXP-001 status

**IMPLEMENTED / SCIENTIFICALLY READY / NOT EXECUTED**

The current hardened EXP-001 is a **future research instrument**, not a historical result. It freezes a 100-task HumanEval-derived benchmark, paired seeds [42, 43, 44], explicit model pools, hard call/token/time/execution/candidate budgets, visible-selection / hidden-final separation, reproducibility metadata, and fail-closed readiness checks.

The 5-task transparent benchmark remains validation-only.

## Objective evaluation

Real generated code is intended to be executed through Docker with no network, bounded resources, isolated `/tmp`, dropped Linux capabilities, no-new-privileges, and timeouts. The framework fails closed if required execution infrastructure is unavailable.

## Statistical analysis

For real results, the repository supports per task-seed analysis, hidden pass rate, separate compute dimensions, bootstrap confidence intervals, and paired differences against C0. No arbitrary single score replaces the underlying dimensions.

Because no historical empirical rows are available, **no historical confidence interval, significance claim, or strategy ranking is reported**.

## Validation

The mock validation command is:

```bash
python scripts/run_experiment.py --config configs/default.yaml --mock
```

Mock results are explicitly validation-only. Real experimental results belong under `results/raw/EXP-00X/` and require real model adapters plus the controlled execution backend.

## Real EXP-001 commands

Prepare and validate the frozen inputs first:

```bash
python scripts/materialize_exp001_benchmark.py \
  --manifest benchmarks/manifests/exp001_v1.json \
  --output benchmarks/programming/exp001_v1/tasks.jsonl
python scripts/validate_readiness.py
```

Only after the preparation gate passes should the real experiment command be used:

```bash
python scripts/validate_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/evaluate_results.py --input results/raw/EXP-001
python scripts/aggregate_results.py --input results/raw/EXP-001 --output results/tables/exp001.csv
python scripts/analyze_results.py --input results/raw/EXP-001 --output results/tables/exp001_statistics.json
```

## Main observed findings

The recoverable historical evidence supports only these statements:

1. The multi-strategy framework has a working mock validation path and its CI history shows that path was executed.
2. The validation path is explicitly isolated from empirical result directories and is not suitable for model-performance claims.
3. The hardened EXP-001 protocol exists and has been audited, but it has not produced empirical strategy results.

There is therefore **no evidence in this repository that additional reasoning calls improve objective correctness, reduce compute cost, or create a better correctness/compute frontier**. Those remain open empirical questions.

## Conclusion

This repository currently demonstrates a validated research instrument and a clearly documented research question, but **not a completed empirical comparison of C0–C6**.

Any future claim about strategy quality must be derived from real, integrity-checked result files and recomputed analysis rather than from mock outputs, readiness checks, or documentation summaries.

## Limitations

- The 5-task transparent benchmark is validation-only.
- EXP-001's 100-task HumanEval-derived benchmark has no real run results yet.
- No historical real-model provider comparison is available.
- Configured budget ceilings are not observed compute measurements.
- Cross-provider token counts, hardware latency, and sandbox availability can vary by environment.
- Historical raw run metadata and result archives are absent from the visible repository tree.
- Validation-only artifacts cannot support hidden-test performance or strategy superiority claims.

## Prior Work

See [`docs/prior_work.md`](docs/prior_work.md) and [`docs/research_lineage.md`](docs/research_lineage.md). Previous repositories are treated as read-only research artifacts; this repository reimplements concepts behind common interfaces rather than copying source trees.

## Reproducibility and readiness

Every real run is designed to capture Git SHA, configuration hash, benchmark hash/version, seed, model pool, generation parameters, environment metadata, and budget usage. Result batches use unique names and are protected against silent overwrite.

Use:

```bash
python scripts/validate_readiness.py
python scripts/validate_execution_environment.py
```

The one-task `EXECUTION_SMOKE_TEST` is a separate execution-path check; it is not EXP-001 and its output is not included in EXP-001 statistics.

**EXP-001: NOT EXECUTED. No empirical result is claimed.**
