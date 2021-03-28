#! /usr/bin/env bash

set -e

# make does this really well; you can just put ! at the beginning of the line
# and check that a test fails, except that I dicovered that bashcov gets
# confused by make commands... so make can only be used at the top level

if $@ 2> /dev/null > /dev/null
then
  echo expecting the following command to fail: 1>&2
  echo $@ 1>&2
  exit 1
fi
