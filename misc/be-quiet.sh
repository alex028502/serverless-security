#! /usr/bin/env bash

set -e

p=$(dirname $0)

set -o pipefail
# make sure this program succeeds and has no output and test coverage should
# take care of the rest
python -u $p/be_quiet.py $1 2>&1 | diff - /dev/null
