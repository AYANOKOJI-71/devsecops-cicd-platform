.PHONY: install test lint validate run build

install:
	python3 -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check .

validate:
	python3 scripts/validate_configuration.py

run:
	uvicorn app.main:app --host 0.0.0.0 --port $${PORT:-8080}

build:
	docker build --tag devsecops-cicd-platform:local .
