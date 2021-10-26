#! /usr/bin/env bash

set -e

# wrapper for pip freeze that fixes a couple issues
# some versions put pkg-resources==0.0.0 and that breaks other versions
# also pip freeze doesn't put the stuff from github in

pip freeze | grep -v pkg-resources |
  sed 's|PyAC.*|git+https://github.com/juga0/pyac@4dbe66dea1aed68966c0a4271167a434bc235e11#egg=PyAC|'
