#! /usr/bin/env bash

set -e

package_dir=$(dirname $0)
source $package_dir/entry-point.sh
assert_env_value 1 # if this fails, it'll be a strange message
device_idx=$1

awker="{ print \$${device_idx} }"
device=$(echo $devices | awk "$awker")
$package_dir/batch.sh heartbeat $device
