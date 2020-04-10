#!/bin/bash -e

export PYTHONPATH=./solarhouse
venv3/bin/pytest --collect-in-virtualenv -vv -l solarhouse/test
echo "DOCTEST"
venv3/bin/python solarhouse/thermoelement.py
