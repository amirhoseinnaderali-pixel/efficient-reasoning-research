# Evaluation Protocol

1. Every strategy receives the same underlying task object and the same problem statement.
2. Generated candidates are parsed without altering benchmark labels or tests.
3. Visible tests are an optional **strategy-side resource** only for C1/C3 selection and C5 feedback. They are never exposed to generation for C0/C2/C4/C6.
4. C6 graph selection occurs before any objective test result is observed.
5. Final objective scoring uses **only the hidden suite** through the common evaluator.
6. Hidden labels are not passed to any strategy method.
7. Generated code executes only through the Docker sandbox for real experiments.
8. Docker execution uses no network, bounded CPU/memory, a read-only root filesystem, isolated `/tmp`, dropped capabilities, no-new-privileges, a PID limit, and a timeout.
9. If Docker is unavailable, the real execution path fails closed. The mock executor is validation-only.
10. Model calls, tokens, execution steps, model latency, execution latency, graph latency, and total wall-clock time are reported separately.

## Benchmark leakage controls

The current transparent benchmark stores visible and hidden suites separately. Strategy code receives only `problem`, `entry_point`, and its own prior candidate/visible feedback where the condition permits it. The hidden suite is accessed only by final evaluation.

## Statistical unit

The analysis unit is the task-seed pair. Strategies should be compared on the same task-seed pairs, enabling paired comparisons and bootstrap confidence intervals over paired differences.
