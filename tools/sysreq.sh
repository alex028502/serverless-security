#! /usr/bin/env bash

set -e

# before I could measure test coverage in bash, I would have written this
# totally differently, and just allowed which to fail, in order to avoid having
# a bunch of if conditions that are only executed on failure and then don't
# work how they are supposed to when they are finally executed... but now I can
# just test this and make sure I have pretty much tried everything
# in fact now more ifs is better because it helps the coverage tool check that
# the failures have been tested

if [[ "$1" == "" ]]
then
  echo requirements list empty!
  exit 1
fi

for sysdep in $@
do
  if ! which $sysdep > /dev/null
  then
    if [[ "$missing" == "" ]]
    then
      missing=$sysdep
    else
      missing="$missing $sysdep"
    fi
  fi
done

if [[ "$missing" != "" ]]
then
  echo please install $missing 1>&2
  exit 1
fi
