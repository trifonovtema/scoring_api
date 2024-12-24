.PHONY: install format typing check test run

export PYTHONPATH := $(shell pwd)

install:
	poetry install

format:
	poetry run black src
	poetry run flake8 src
	poetry run black tests
	poetry run flake8 tests

typing:
	poetry run mypy src
	poetry run mypy tests

check:
	make format
	make typing

test:
	poetry run pytest -v --cov

run:
	poetry run python ./src/api.py


