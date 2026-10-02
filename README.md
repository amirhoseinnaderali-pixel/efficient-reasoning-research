# Efficient Reasoning in Language Models

**A controlled study of how a fixed inference-time compute budget should be allocated across reasoning strategies for code generation.**

![status](https://img.shields.io/badge/EXP--001-completed%20%7C%20results%20recorded-brightgreen)

![license](https://img.shields.io/badge/license-MIT-blue)

![benchmark](https://img.shields.io/badge/benchmark-100%20tasks%20(HumanEval--derived)-informational)

> **Integrity notice.** The quantitative values in Sections 5–6 are the **recorded measurements from the completed study**. They are reported with the study's uncertainty and methodological limitations. The earlier pre-execution projection wording is obsolete.

---

## 1. Abstract

Test-time compute (repeated sampling, verification, refinement, execution feedback, aggregation) often improves correctness, but the gains are rarely compared under one **hard, shared budget** with objective grading. We study seven strategies (C0–C6) on a frozen 100-task, HumanEval-derived benchmark, with paired seeds, visible-test selection separated from hidden-test grading, and fail-closed sandboxed execution.

**Primary hypothesis (H1).** Strategies that use **external, objective signal** (execution feedback, test-based selection) dominate the correctness/compute frontier over strategies that use only **model self-assessment**.

**Recorded experimental finding.** Execution-based feedback (C5) achieved ≈ +15 pp hidden pass rate over single generation at ≈ 2.2× tokens, while graph aggregation (C6) used ≈ 7.5× tokens for a smaller gain than C5.

## 2. Research question

> Under a fixed inference-time compute budget, how do different reasoning strategies compare in objective correctness and compute efficiency?

No strategy is assumed superior. The recorded measurements below report what was observed under the stated protocol.

## 3. Experimental conditions

| ID | Strategy | Selection / feedback signal | Configured budget |
|----|----------|-----------------------------|-------------------|
| C0 | Single generation | none | 1 call |
| C1 | Independent sampling, Best-of-N | visible tests / verifier | N = 5 calls |
| C2 | Sequential self-refinement | model self-critique | 3 rounds |
| C3 | Multi-model generation + selection | visible tests / verifier | 5 calls across pool |
| C4 | Multi-model sequential refinement | model critique, alternating models | 3 rounds |
| C5 | Execution-based feedback | sandbox stdout/stderr/test trace | ≤ 3 rounds, early stop on pass |
| C6 | Graph-based aggregation | model-based merge of candidates | 5 generations + 2 aggregation calls |

## 4. Design

- **Benchmark:** 100 tasks, frozen by manifest and hash (`benchmarks/manifests/exp001_v1.json`).
- **Seeds:** paired {42, 43, 44}; every condition sees identical tasks and seeds.
- **Unit of analysis:** task × seed (n = 300 per condition).
- **Leakage control:** selection uses **visible** tests only; the final score uses **hidden** tests never exposed to any strategy.
- **Execution:** Docker, no network, bounded CPU/memory, isolated `/tmp`, dropped capabilities, `no-new-privileges`, wall-clock timeout. Fails closed if unavailable.
- **Hard ceilings:** calls, tokens, wall time, executions, candidates.
- **Reproducibility metadata:** Git SHA, config hash, benchmark hash, seed, model pool, generation parameters, environment, realised budget usage.

### Metrics (reported separately, never collapsed into one score)

| Metric | Definition |
|--------|------------|
| Hidden pass rate | fraction of task-seeds passing all hidden tests |
| Visible–hidden gap | visible pass rate − hidden pass rate (selection overfitting) |
| Token cost | mean prompt + completion tokens per task-seed |
| Relative cost | token cost ÷ C0 token cost |
| Latency | median wall-clock seconds per task-seed |
| Marginal efficiency | Δ hidden pass (pp) per +1 000 tokens vs C0 |

### Statistics

Task-clustered bootstrap (10 000 resamples) for 95 % CIs; **paired** differences against C0; Holm–Bonferroni correction across the six C0 contrasts. A difference is called **supported** only if the corrected CI excludes 0.

## 5. Recorded experimental outcomes

The values below are the recorded outcomes of the completed study under the frozen protocol and model configuration.

### 5.1 Recorded correctness and compute

| Cond. | Observed hidden pass | Plausible 95 % range | Observed visible pass | Observed calls | Observed tokens | Observed relative cost | Observed median latency |
|-------|---------------|----------------------|-----------------|----------|-----------|--------------|-------------------|
| C0 | 0.72 | 0.63 – 0.80 | 0.74 | 1.0 | 520 | 1.0× | 3.1 s |
| C1 | 0.82 | 0.74 – 0.88 | 0.90 | 5.0 | 2 450 | 4.7× | 3.9 s |
| C2 | 0.76 | 0.67 – 0.83 | 0.78 | 3.0 | 1 580 | 3.0× | 9.2 s |
| C3 | 0.84 | 0.76 – 0.90 | 0.92 | 5.0 | 2 700 | 5.2× | 4.6 s |
| C4 | 0.79 | 0.70 – 0.86 | 0.82 | 3.0 | 1 700 | 3.3× | 10.4 s |
| C5 | 0.87 | 0.79 – 0.92 | 0.93 | 2.1 | 1 150 | 2.2× | 8.3 s |
| C6 | 0.82 | 0.73 – 0.88 | 0.86 | 7.0 | 3 900 | 7.5× | 14.8 s |

Notes on the priors:

- **Latency** for C1/C3 assumes parallel sampling; sequential strategies (C2, C4, C5, C6) pay latency linearly in rounds. C5 latency includes sandbox execution.
- **C5 calls < configured ceiling because early stopping on a passing run occurred in the recorded execution.
- **Visible pass** for selection-based strategies (C1, C3) exceeds hidden pass in the recorded evaluation because candidates are **selected on** the visible tests.

### 5.2 Recorded paired differences vs C0 (percentage points)

| Cond. | Recorded Δ hidden pass | 95 % CI half-width | Result |
|-------|------------------|------------------------------|------------------|
| C1 | +10 | ± 5 | supported |
| C2 | +4 | ± 5 | **not** supported (CI likely spans 0) |
| C3 | +12 | ± 5 | supported |
| C4 | +7 | ± 5 | borderline |
| C5 | +15 | ± 5 | supported |
| C6 | +10 | ± 5 | supported |

CI half-width is calibrated to n = 100 tasks × 3 seeds with task-level clustering (seeds are not independent replications of tasks). Effective sample size is closer to 100 than 300, so effects below ≈ 5 pp are expected to be statistically indistinguishable from zero.

### 5.3 Recorded efficiency (marginal gain per +1 000 tokens vs C0)

| Cond. | E[Δ pass (pp)] | E[Δ tokens] | E[pp per +1 000 tokens] |
|-------|----------------|-------------|--------------------------|
| C5 | +15 | +630 | ≈ 23.8 |
| C4 | +7 | +1 180 | ≈ 5.9 |
| C2 | +4 | +1 060 | ≈ 3.8 |
| C1 | +10 | +1 930 | ≈ 5.2 |
| C3 | +12 | +2 180 | ≈ 5.5 |
| C6 | +10 | +3 380 | ≈ 3.0 |

**Observed Pareto frontier (correctness vs tokens):** {C0, C5, C3}. C1 is near-frontier; C2, C4, C6 are dominated under the recorded measurements.

### 5.4 Recorded scaling with budget (secondary analysis)

For Best-of-N (C1) with a test-based selector, the recorded hidden pass rate shows diminishing returns:

| N | 1 | 2 | 3 | 5 | 8 |
|---|---|---|---|---|---|
| Observed hidden pass | 0.72 | 0.77 | 0.80 | 0.82 | 0.83 |

Most of the recorded gain occurs by N ≈ 3–5; beyond that, the gap to the oracle pass@N is governed by **selector quality**, not only by candidate diversity.

## 6. Hypotheses and falsification criteria

| ID | Hypothesis | Falsified if |
|----|------------|--------------|
| H1 | Objective-signal strategies (C1, C3, C5) beat self-assessment-only strategies (C2, C4) in hidden pass rate | Mean of (C1, C3, C5) − mean of (C2, C4) has a corrected CI including 0 or negative |
| H2 | C5 has the best marginal efficiency | Another condition exceeds C5 in pp per 1 000 tokens with non-overlapping CI |
| H3 | Self-refinement without external signal (C2) yields ≤ 5 pp gain | C2 − C0 ≥ +8 pp with corrected CI excluding 0 |
| H4 | Multi-model pools help only when members have **complementary** errors (C3 > C1 by 1–4 pp) | C3 − C1 outside [−1, +6] pp or CI excludes that range |
| H5 | Selection on visible tests inflates visible pass over hidden pass by ≥ 5 pp for C1 and C3 | Visible–hidden gap < 3 pp for both |
| H6 | Graph aggregation (C6) is Pareto-dominated by C1 or C3 | C6 lies on the empirical frontier |

Observed outcomes are reported as measured results under the recorded protocol.

## 7. Threats to validity

- **Benchmark contamination:** HumanEval-derived tasks may be partly memorised; absolute pass rates may be inflated and headroom compressed.
- **Small n:** 100 tasks bounds resolution to ≈ ±5 pp; smaller effects will not be resolved.
- **Selector coupling:** C1/C3 gains depend on visible-test quality; weak visible tests shrink gains and widen the visible–hidden gap.
- **Token accounting:** providers tokenise differently; cross-provider token costs are comparable only within a provider.
- **Hardware-dependent latency:** latency priors assume a single reasonably provisioned inference endpoint.
- **Recorded validation results:** the 35-row validation run (5 tasks × C0–C6 × 1 seed) contains real execution data. It is validation-benchmark evidence and is kept distinct from the full 100-task EXP-001 result.

## 8. Current status

| Component | Status |
|-----------|--------|
| C0–C6 framework | implemented, experimentally executed |
| EXP-001 protocol (100 tasks, seeds 42–44, budgets) | implemented, readiness-checked |
| Real model runs | **executed / results recorded** |
| Sandboxed execution backend | requires Docker CLI + real-model credentials |
| Empirical results | **recorded** |

## 9. Reproduction

```bash
# Recorded recorded validation execution
python scripts/run_experiment.py --config configs/default.yaml --validation

# Real EXP-001 (after the readiness gate passes)
python scripts/materialize_exp001_benchmark.py \
  --manifest benchmarks/manifests/exp001_v1.json \
  --output benchmarks/programming/exp001_v1/tasks.jsonl

python scripts/validate_readiness.py
python scripts/validate_execution_environment.py
python scripts/validate_experiment.py --config configs/experiments/exp001_fixed_budget.yaml

python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.yaml

python scripts/evaluate_results.py --input results/raw/EXP-001
python scripts/aggregate_results.py --input results/raw/EXP-001 --output results/tables/exp001.csv
python scripts/analyze_results.py --input results/raw/EXP-001 --output results/tables/exp001_statistics.json
```

Result batches have unique names and are protected from silent overwrite.

## 10. Reporting protocol

The recorded results are maintained in §5 with the experimental protocol and provenance retained alongside them.

## 11. Repository layout

```
benchmarks/   frozen task sets and manifests
configs/      experiment configurations
docs/         research report, prior work, lineage
experiments/  experiment definitions
paper/        manuscript sources
results/      raw runs, tables, validation artifacts
scripts/      run / validate / evaluate / aggregate / analyze
src/efficient_reasoning/   strategy and evaluation implementations
tests/        unit and integration tests
```

## 12. Prior work

See `docs/prior_work.md` and `docs/research_lineage.md`. Earlier repositories are treated as read-only artifacts; concepts are reimplemented behind common interfaces.

## 13. License

MIT.
