# Evaluation and Leakage Audit

## Leakage findings

### Fixed

- Hidden tests are accessed only by final evaluation.
- C6 no longer calls the verifier before graph selection.
- Final scoring no longer reruns visible tests.
- Mock validation cannot enter real EXP-001 configuration validation.
- Benchmark loader validates visible/hidden suite structure and duplicate task IDs.

### Intentional, documented use of visible labels

- C1 uses visible tests to choose among independent candidates.
- C3 uses visible tests to select among model outputs.
- C5 uses visible tests as execution feedback.

These are explicit strategy resources, not hidden implementation shortcuts.

## Verifier audit

The real evaluator uses Docker only, with no network, bounded CPU and memory, timeout, PID limit, read-only root, isolated writable `/tmp`, dropped capabilities, and no-new-privileges. Docker absence raises a hard error rather than silently falling back to host execution.

The runner also redirects generated-code stdout/stderr away from host-captured logs and keeps the final machine-readable pass/fail record controlled by the harness.
