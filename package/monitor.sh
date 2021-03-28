#! /usr/bin/env bash

set -e

package_dir=$(dirname $0)
source $package_dir/entry-point.sh
python -u $package_dir/monitor.py echo TEST
