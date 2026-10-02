# Compute Budget

EXP-001 keeps compute dimensions separate rather than collapsing them into one score.

| Dimension | Accounting | Hard constraint | Notes |
|---|---|---|---|
| Model calls | `model_calls` | yes | Failed API/model attempts count as calls. |
| Input tokens | `input_tokens` | yes when configured | Provider-reported usage is recorded; cross-provider tokenizers are not assumed equivalent. |
| Output tokens | `output_tokens` / `total_generated_tokens` | yes | Per-call generation cap is reduced to remaining budget before a request. Provider over-reporting invalidates the run. |
| Model latency | `model_latency_seconds` | tracked | Provider/network time only. |
| Execution latency | `execution_latency_seconds` | tracked | Sandbox/verifier time. |
| Graph latency | `graph_latency_seconds` | tracked | C6 graph construction/selection time. |
| Strategy wall clock | `strategy_wall_clock_seconds` | yes | Covers all work inside the strategy plus final evaluation. |
| Execution steps | `execution_steps` | yes | Each visible/hidden sandbox invocation is one step. |
| Cost proxy | `cost_proxy` + `cost_proxy_status` | tracked | `available` means every recorded model call supplied a measurable monetary proxy; `unavailable` is preserved explicitly rather than encoded as zero. |

## Comparability rules

The same budget ceilings are applied independently to every task/seed/strategy run. A strategy may use less than the ceiling; that difference is itself an empirical outcome and is reported rather than hidden.

C1 and C3 are explicitly **verifier-assisted** conditions: visible tests may be used for candidate selection. C5 uses visible execution for iterative feedback. C6 graph selection is prohibited from using objective test results before selection.

A run that crosses a hard budget is marked `ineligible_budget`; it must not be treated as a valid point on a correctness/compute frontier.

A mixed or missing monetary cost proxy is never silently treated as zero. Cost-based analysis must use only rows with `cost_proxy_status=available` and must not be used when coverage is incomplete.
