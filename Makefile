.DEFAULT_GOAL := help

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install       Install dependencies"
	@echo "  test          Run tests"
	@echo "  format        Run formatters"
	@echo "  help          Show this help message"

install:
	poetry install

test:
	poetry run pytest

format:
	poetry run ruff format .
	poetry run ruff check . --fix
