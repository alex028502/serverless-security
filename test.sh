#! /usr/bin/env bash

set -e

venv/bin/python unit.py

./be-quiet.sh

./check-ignore.sh

venv/bin/python -m pytest tests -xv
