#!/bin/bash -e

export PYTHONPATH=./solarhouse
venv3/bin/pytest --doctest-modules --collect-in-virtualenv -vv -l solarhouse

