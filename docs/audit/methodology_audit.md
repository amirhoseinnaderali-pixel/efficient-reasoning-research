# Methodology Audit

## Research question

The repository asks how a fixed inference-time budget should be allocated across C0-C6. The framing is appropriate as a hypothesis-driven comparison rather than a pre-declared ranking.

## Comparability

All conditions use the same task distribution, paired seed schedule, common final hidden evaluator, and common hard ceilings. Strategy-specific visible verification is explicit rather than hidden.

The conditions are not expected to consume identical computation. Instead, they represent distinct allocations under shared ceilings. This is appropriate for the research question, provided every consumed dimension is reported.

## Important asymmetries

| Condition | Model calls | Candidate count | Visible tests during strategy | Final hidden evaluation | Graph compute |
|---|---:|---:|---:|---:|---:|
| C0 | 1 | 1 | 0 | 1 | 0 |
| C1 | N=4 | 4 | 4 | 1 | 0 |
| C2 | depth=3 | 3 | 0 | 1 | 0 |
| C3 | one per configured model (3) | 3 | 3 | 1 | 0 |
| C4 | one per configured model (3) | 3 | 0 | 1 | 0 |
| C5 | up to 3 | up to 3 | up to 3 | 1 | 0 |
| C6 | N=4 | 4 | 0 | 1 | measured |

These asymmetries are the experimental conditions; none is hidden in the implementation.

## Remaining interpretation rule

C1 and C3 are verifier-assisted Best-of-N/selection conditions, while C6 is graph-only selection. Their performance should not be described as though the only difference were sampling count.
