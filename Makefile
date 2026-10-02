.PHONY: test validate validate-all smoke compile

test:
	pytest -q

compile:
	python -m compileall -q src scripts

validate:
	python scripts/validate_experiment.py --config configs/experiments/exp001_fixed_budget.yaml

validate-all:
	$(MAKE) validate
	python scripts/validate_experiment.py --config configs/experiments/exp002_graph_aggregation.yaml
	python scripts/validate_experiment.py --config configs/experiments/exp003_execution_feedback.yaml
	python scripts/validate_experiment.py --config configs/default.yaml --allow-mock

smoke:
	python scripts/run_experiment.py --config configs/default.yaml --mock
