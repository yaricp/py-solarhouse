#!/bin/bash -e

export PYTHONPATH=.
venv3/bin/pytest --doctest-modules --pep8 --collect-in-virtualenv -vv -l solarhouse
venv3/bin/pytest --doctest-modules --pep8 --collect-in-virtualenv -vv -l test

