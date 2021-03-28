#! /usr/bin/env bash

set -e

venv/bin/python tools/check_inventory.py $1
