#! /usr/bin/env bash

set -e

./tools/test.sh

venv/bin/python unit.py

venv/bin/python tools/server-action/test.py

./be-quiet.sh

./check-ignore.sh

venv/bin/python -m pytest tests -xv
