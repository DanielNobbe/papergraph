#!/bin/bash

echo "Running Ruff..."
poetry run ruff check .

echo "Running Flake8..."
poetry run flake8 .

echo "Running Black..."
poetry run black --check .

echo "Running Pylint..."
poetry run pylint .
