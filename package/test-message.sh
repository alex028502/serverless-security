#! /usr/bin/env bash

set -e

# action that can be triggered by monitor
# needs to take a few seconds

pause=$1
shift

echo start $@
sleep $pause
echo done $@

