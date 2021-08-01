#! /usr/bin/env bash

set -e

expect_failure=$(dirname $0)/expect-failure.sh
echo testing $expect_failure
# check this out - use it to test itself
$expect_failure $expect_failure echo ok
