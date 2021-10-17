#! /usr/bin/env bash

set -e

function message {
  echo checking for accidental ignores in $@
}

set -o pipefail

message flake8
find $(venv/bin/python misc/check_ignore.py flake8) -type f | ./misc/no-unignored.sh
message black
find . -type f | venv/bin/python misc/check_ignore.py black | ./misc/no-unignored.sh
message bash-coverage
find $(venv/bin/python misc/check_ignore.py bash-coverage) -type f | ./misc/no-unignored.sh
message nyc
find $(venv/bin/python misc/check_ignore.py nyc) -type f | ./misc/no-unignored.sh

echo now show that this check will fail when it should:
! ls | ./misc/no-unignored.sh || exit 1
echo great!
