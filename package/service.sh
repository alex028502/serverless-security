#! /usr/bin/env bash

set -e

package_dir=$(dirname $0) # never cd; messes with py coverage
source $package_dir/entry-point.sh
python $package_dir/monitor.py $package_dir/batch.sh motion $devices
