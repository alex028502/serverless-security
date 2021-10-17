#! /usr/bin/env bash

set -e

# wrapper for pip freeze that fixes a couple issues

pip freeze | grep -v pkg-resources |
  sed 's|PyAC.*|git+https://github.com/juga0/pyac@4dbe66dea1aed68966c0a4271167a434bc235e11#egg=PyAC|'
