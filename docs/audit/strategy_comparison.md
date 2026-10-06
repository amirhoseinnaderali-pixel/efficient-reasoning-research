# Strategy Comparison Audit

| Condition | Generation path | Selection | Objective verifier before selection | Final score | Main measured compute |
|---|---|---|---|---|---|
| C0 | 1 primary-model call | none | No | hidden-only | call/tokens/latency |
| C1 | 4 primary-model calls | visible-test pass count | Yes | hidden-only | calls/tokens + verifier |
| C2 | 3 sequential primary-model calls | final chain member | No | hidden-only | calls/tokens/latency |
| C3 | one call per configured model | visible-test pass count | Yes | hidden-only | heterogeneous calls/tokens + verifier |
| C4 | sequential heterogeneous calls | final chain member | No | hidden-only | heterogeneous calls/tokens/latency |
| C5 | up to 3 primary-model calls | adaptive stop from visible tests | Yes | hidden-only | calls/tokens + verifier |
| C6 | 4 primary-model calls | TF-IDF/cosine graph degree | No | hidden-only | calls/tokens + graph CPU time |

No condition receives hidden labels during strategy execution.
