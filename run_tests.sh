#!/bin/bash -e

export PYTHONPATH=./solarhouse
venv3/bin/pytest --doctest-modules --pep8 --collect-in-virtualenv -vv -l solarhouse

