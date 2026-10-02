# Efficient Reasoning in Language Models

**A controlled study of how a fixed inference-time compute budget should be allocated across reasoning strategies for code generation.**

![status](https://img.shields.io/badge/EXP--001-pre--registered%20%7C%20not%20executed-orange)

![license](https://img.shields.io/badge/license-MIT-blue)

![benchmark](https://img.shields.io/badge/benchmark-100%20tasks%20(HumanEval--derived)-informational)

> **Integrity notice.** Every number in the tables marked **E[·]** is a **pre-registered expectation (a prior)** derived from the published scaling behaviour of test-time-compute methods. None is a measurement. EXP-001 has **not been executed**. These values exist so that results can later be judged against hypotheses fixed *before* seeing data. They must never be cited as findings.

---

## 1. Abstract

Test-time compute (repeated sampling, verification, refinement, execution feedback, aggregation) often improves correctness, but the gains are rarely compared under one **hard, shared budget** with objective grading. We study seven strategies (C0–C6) on a frozen 100-task, HumanEval-derived benchmark, with paired seeds, visible-test selection separated from hidden-test grading, and fail-closed sandboxed execution.

**Primary hypothesis (H1).** Strategies that use **external, objective signal** (execution feedback, test-based selection) dominate the correctness/compute frontier over strategies that use only **model self-assessment**.

**Expected outcome (prior).** Execution-based feedback (C5) is expected to reach ≈ +15 pp hidden pass rate over single generation at ≈ 2.2× tokens, whereas graph aggregation (C6) is expected to cost ≈ 7.5× tokens for a smaller gain than C5.

## 2. Research question

> Under a fixed inference-time compute budget, how do different reasoning strategies compare in objective correctness and compute efficiency?

No strategy is assumed superior. The priors below only fix what we **expect**, so that deviations are interpretable.

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

## 5. Pre-registered expected outcomes

**Assumed regime:** a mid-capability instruction-tuned code model pool where C0 sits at ≈ 70–75 % hidden pass rate on this benchmark. If the realised C0 is outside 60–85 %, all absolute priors below should be re-centred (headroom effects dominate), and only the **ordering** hypotheses remain meaningful.

### 5.1 Expected correctness and compute — E[·]

| Cond. | E[hidden pass] | Plausible 95 % range | E[visible pass] | E[calls] | E[tokens] | E[rel. cost] | E[median latency] |
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
- **C5 calls < configured ceiling** because early stopping on a passing visible run is expected on roughly half of tasks.
- **Visible pass** for selection-based strategies (C1, C3) is expected to exceed hidden pass because candidates are **selected on** the visible tests.

### 5.2 Expected paired differences vs C0 (percentage points)

| Cond. | E[Δ hidden pass] | Expected 95 % CI half-width | Expected verdict |
|-------|------------------|------------------------------|------------------|
| C1 | +10 | ± 5 | supported |
| C2 | +4 | ± 5 | **not** supported (CI likely spans 0) |
| C3 | +12 | ± 5 | supported |
| C4 | +7 | ± 5 | borderline |
| C5 | +15 | ± 5 | supported |
| C6 | +10 | ± 5 | supported |

CI half-width is calibrated to n = 100 tasks × 3 seeds with task-level clustering (seeds are not independent replications of tasks). Effective sample size is closer to 100 than 300, so effects below ≈ 5 pp are expected to be statistically indistinguishable from zero.

### 5.3 Expected efficiency (marginal gain per +1 000 tokens vs C0)

| Cond. | E[Δ pass (pp)] | E[Δ tokens] | E[pp per +1 000 tokens] |
|-------|----------------|-------------|--------------------------|
| C5 | +15 | +630 | ≈ 23.8 |
| C4 | +7 | +1 180 | ≈ 5.9 |
| C2 | +4 | +1 060 | ≈ 3.8 |
| C1 | +10 | +1 930 | ≈ 5.2 |
| C3 | +12 | +2 180 | ≈ 5.5 |
| C6 | +10 | +3 380 | ≈ 3.0 |

**Expected Pareto frontier (correctness vs tokens):** {C0, C5, C3}. C1 is near-frontier; C2, C4, C6 are expected to be dominated.

### 5.4 Expected scaling with budget (secondary analysis)

For Best-of-N (C1) with a test-based selector, hidden pass rate is expected to follow diminishing returns:

| N | 1 | 2 | 3 | 5 | 8 |
|---|---|---|---|---|---|
| E[hidden pass] | 0.72 | 0.77 | 0.80 | 0.82 | 0.83 |

Most of the gain is expected by N ≈ 3–5; beyond that, the gap to the oracle pass@N is expected to be governed by **selector quality**, not by candidate diversity.

## 6. Hypotheses and falsification criteria

| ID | Hypothesis | Falsified if |
|----|------------|--------------|
| H1 | Objective-signal strategies (C1, C3, C5) beat self-assessment-only strategies (C2, C4) in hidden pass rate | Mean of (C1, C3, C5) − mean of (C2, C4) has a corrected CI including 0 or negative |
| H2 | C5 has the best marginal efficiency | Another condition exceeds C5 in pp per 1 000 tokens with non-overlapping CI |
| H3 | Self-refinement without external signal (C2) yields ≤ 5 pp gain | C2 − C0 ≥ +8 pp with corrected CI excluding 0 |
| H4 | Multi-model pools help only when members have **complementary** errors (C3 > C1 by 1–4 pp) | C3 − C1 outside [−1, +6] pp or CI excludes that range |
| H5 | Selection on visible tests inflates visible pass over hidden pass by ≥ 5 pp for C1 and C3 | Visible–hidden gap < 3 pp for both |
| H6 | Graph aggregation (C6) is Pareto-dominated by C1 or C3 | C6 lies on the empirical frontier |

Any outcome contradicting a prior is a valid result and will be reported as such.

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
| C0–C6 framework | implemented, validation-executed |
| EXP-001 protocol (100 tasks, seeds 42–44, budgets) | implemented, readiness-checked |
| Real model runs | **not executed** |
| Sandboxed execution backend | requires Docker CLI + real-model credentials |
| Empirical results | **none** |

## 9. Reproduction

```bash
# Recorded validation execution
python scripts/run_experiment.py --config configs/default.yaml --mock

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

After execution, this README's **§5 will be kept unchanged** and a new **§5-R (Realised results)** added beside it, with a prior-vs-observed table. Priors are never edited retroactively.

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
