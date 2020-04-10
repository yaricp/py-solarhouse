#!/bin/bash -e

PYTHONPATH=./solarhouse venv3/bin/pytest --doctest-modules -vv -l solarhouse/test
