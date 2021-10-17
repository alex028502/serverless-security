#! /usr/bin/env bash

set -e

# - check that local installation has been done correctly


set -o pipefail

# make sure that our requirements file matches what we have installed
# if this fails maybe delete venv and try again
# I think it might happen if dependencies get removed
./tools/venv-run.sh venv ./tools/pip-freeze.sh | diff - requirements.txt
