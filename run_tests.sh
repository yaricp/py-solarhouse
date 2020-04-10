#!/bin/bash -e

export PYTHONPATH=./solarhouse
pytest --doctest-modules --collect-in-virtualenv -vv -l solarhouse

