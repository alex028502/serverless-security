#! /usr/bin/env bash

set -e

if [[ "$1" == "" ]] || [[ "$2" != "" ]]
then
  echo must have exactly one argument 1>&2
  exit 1
fi

ls $1 > /dev/null

cut -f1 -d"#" $1
