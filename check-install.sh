#! /usr/bin/env bash

set -e

set -o pipefail

# make sure that our requirements file matches what we have installed
# if this fails maybe delete venv and try again
# I think it might happen if dependencies get removed
./venv-run.sh venv ./pip-freeze.sh | diff - requirements.txt
