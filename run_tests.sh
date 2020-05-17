#!/bin/bash -e

export PYTHONPATH=./src
venv3/bin/pytest --doctest-modules --pep8 --collect-in-virtualenv -vv -l src/solarhouse
venv3/bin/pytest --doctest-modules --pep8 --collect-in-virtualenv -vv -l test

