#! /usr/bin/env bash

set -e

venv/bin/python unit.py

./check-ignore.sh

venv/bin/python -m pytest tests -xv

./more-test.sh
