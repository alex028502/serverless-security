#! /usr/bin/env bash

set -e

# this might have more tests in it one day, but is mainly needed because bashcov
# needs a bash file for an entry point

venv/bin/python tools/check_inventory.py $1
