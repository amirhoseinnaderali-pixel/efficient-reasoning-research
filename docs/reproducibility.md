# Reproducibility

Runs capture timestamp, model, budget usage, environment, benchmark identity, and available git SHA. Use the validated config to recreate a run.

```bash
python scripts/validate_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.yaml
```

Real EXP-001 requires external model access and Docker. CI uses mock components only.
