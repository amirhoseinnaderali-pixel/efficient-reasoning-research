# Budget Audit

## Previous defects

- Per-call generation did not cap to the remaining global output-token budget.
- Wall-clock checks were post-hoc and model latency was conflated with total run latency.
- Cost accounting was collected only indirectly from candidate objects.
- Failed model calls were not explicitly represented.

## Current controls

- `Budget.reserve_call()` checks the call and wall-clock ceilings before each request.
- `_generate()` uses remaining output-token and remaining wall-clock budgets to bound each request.
- `record_generation()` checks actual provider usage and invalidates a run on provider overrun.
- Failed calls are counted and their latency recorded.
- Execution, graph, and model latency are separated.
- Candidate and execution-step ceilings are enforced.
- No automatic retries are enabled (`max_retries: 0`).

## Tests

Budget tests now cover call/token/input-token separation, overrun detection, and independent accounting dimensions.
