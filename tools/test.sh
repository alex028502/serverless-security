#! /usr/bin/env bash

set -e

echo tool tests:
expect_failure=$(dirname $0)/expect-failure.sh
assert=$(dirname $0)/assert.sh
echo testing $expect_failure
# check this out - use it to test itself
$expect_failure $expect_failure echo ok

echo testing $assert
$expect_failure $assert 1 == 2
$expect_failure $assert 1 != 1
echo tool tests pass
