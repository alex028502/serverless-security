#! /usr/bin/env bash

set -e

# a few little things that are easier to test straight in bash

source venv/bin/activate

set -o pipefail
# make sure this program succeeds and has no output and test coverage should
# take care of the rest
venv/bin/python -u be_quiet.py 2>&1 | diff - /dev/null
