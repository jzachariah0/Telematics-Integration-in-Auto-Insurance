# Makefile for InsurityAI-Project

# Default target
.DEFAULT_GOAL := help

# Docker & environment
up: ## Start docker-compose services
	docker-compose up -d

down: ## Stop docker-compose services
	docker-compose down

build: ## Rebuild docker images
	docker-compose build

# Data
ingest: ## Run data ingest pipeline
	python src/ingest/run_ingest.py --input ./data/synthetic_samples --output db

features: ## Generate features
	python src/features/build_features.py --input db --output db

# Modeling
train: ## Train models
	python src/models/train.py --features db --output ./models

backtest: ## Run backtest and export metrics
	jupyter nbconvert --to notebook --execute experiments/backtest.ipynb --output docs/metrics/backtest_results.ipynb

# Pricing
price: ## Run pricing engine on sample users
	python src/pricing/run_pricing.py --features db --models ./models --output ./data/pricing_results.json

# Demo
demo: ## End-to-end demo: ingest → features → train → price
	make ingest
	make features
	make train
	make price

# Clean
clean: ## Remove generated files
	rm -rf __pycache__ .pytest_cache .mypy_cache db/* models/* data/pricing_results.json

# Utilities
lint: ## Run lint checks
	flake8 src

test: ## Run unit tests
	pytest -q

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}'
	