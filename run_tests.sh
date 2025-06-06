#!/bin/bash

export PYTHONPATH=.

for test in tests/test_*.py; do
    uv run python "$test"
done
