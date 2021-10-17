#! /usr/bin/env bash

set -e

package_dir=$(dirname $0)
source $package_dir/entry-point.sh

python $package_dir/sensor.py $package_dir/sensor_timer.py
