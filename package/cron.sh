#! /usr/bin/env bash

set -e

package_dir=$(dirname $0)
source $package_dir/entry-point.sh

$package_dir/batch.sh heartbeat $package_dir/encryptor.py
