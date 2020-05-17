#!/bin/bash

work_dir=$PWD
BOTCMD=("${work_dir}/venv3/bin/python3" "${work_dir}/demos/main.py")

PYTHONPATH=. "${BOTCMD[@]}"
