#!/bin/bash

work_dir=$(dirname "${BASH_SOURCE[0]}")
root_dir=$(readlink -f "${work_dir}/..")

BOTCMD=("$root_dir/venv3/bin/python3" "${work_dir}/main.py")

PYTHONPATH="$root_dir/src" "${BOTCMD[@]}"
