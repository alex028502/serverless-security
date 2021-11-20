#! /usr/bin/env bash

set -e

# there was no uuidgen on my rapsberry pi even when I installed util-linux so
# I did this instead - a single random number would have worked almost all the
# time

directory=$1
name=$2
extension=$3



# the number at the end is just the number of repeats that second which
# makes it a little more testable since we can always create a repeat by
# running it twice

# padding the filenames with lots of digits even though we only allow
# ten per series - to make it possible to test this
for i in $(seq -f '%00005.0f' 0 9)
do
  path=$directory/$name.$i.$extension
  if ! ls $path > /dev/null 2>&1
  then
    echo $path
    exit 0
  fi
done

echo 1>&2 no filenames left
exit 1
