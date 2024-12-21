.PHONY: install format typing test run

export PYTHONPATH := $(shell pwd)

install:
	poetry install

format:
	poetry run black src
	poetry run flake8 src

typing:
	poetry run mypy src

test:
	poetry run python -m unittest -b ./tests/test.py

run:
	poetry run python ./src/api.py


