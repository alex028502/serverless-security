#! /usr/bin/env bash

set -e

# there was no uuidgen on my rapsberry pi even when I installed util-linux so
# I did this instead - a single random number would have worked almost all the
# time

directory=$1
name=$2
extension=$3

# the first attempt is not random - this solves two problems
# - not so elegant if you have repeat the line at the start of the loop and
# inside the loop since I don't know how to `while file_exists(name=...)`
# in bash
# makes it a little more testable since we can always create a repeat by
# running it twice
path=$directory/$name.00000.$extension
while ls $path > /dev/null 2>&1
do
  path=$directory/$name.$RANDOM.$extension
done
# so if you ever have three in the same second, don't expect them to be in
# chronological order
echo $path
