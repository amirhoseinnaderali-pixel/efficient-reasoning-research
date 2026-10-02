.PHONY: test validate smoke

test:
	pytest -q

validate:
	python scripts/validate_experiment.py --config configs/experiments/exp001_fixed_budget.yaml

smoke:
	python scripts/run_experiment.py --config configs/default.yaml --mock
