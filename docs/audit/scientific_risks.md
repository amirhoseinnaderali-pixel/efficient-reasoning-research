# Scientific Risks

## High priority

1. **Small benchmark:** five tasks can produce unstable or saturated estimates. This is the main remaining methodological blocker for substantive claims.
2. **Heterogeneous model compute:** C3/C4 compare multi-model collaboration, but raw model-call counts are not equivalent computational units across providers/models. Report model identity, tokens, latency, and cost separately.
3. **Provider usage fidelity:** token/cost accounting depends on provider metadata. Missing usage should make a run ineligible, not silently imputed.

## Medium priority

4. **Sandbox image reproducibility:** tags can move; pin a digest before final runs.
5. **Programming-task scope:** current tasks emphasize straightforward function generation and may not stress the intended reasoning mechanisms.
6. **Bootstrap uncertainty:** with very small task counts, confidence intervals are descriptive rather than strong evidence of generalization.

## Low priority

7. Human-readable analysis remains intentionally limited; machine-readable artifacts are the source of truth.
