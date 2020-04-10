#!/bin/bash -e

export PYTHONPATH=./solarhouse
venv3/bin/pytest --collect-in-virtualenv -vv -l solarhouse/test
