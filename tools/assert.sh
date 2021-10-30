#! /usr/bin/env bash

set -e

# just like [ ] but prints a nice message when it fails and because you don't
# need the closing bracket, it might work nicely with xargs
# [[ ]] doesn't work - something to do with built in acting differently maybe
if [ "$@" ]
then
  exit 0
fi

echo assertion failure $@
exit 1
