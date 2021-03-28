#! /usr/bin/env bash

set -e

dir=$(dirname $0)

mode=$1

heartbeat=heartbeat
motion=motion

function usage {
  echo usage: ./batch.sh \[$heartbeat\|$motion\] \[DEVICES\]... 1>&2
  # we also might want to do something like this, but it seems like this is
  # something that should not change at runtime so maybe just an error message
  # is enough
  # echo configuration error | $dir/send.py error
  exit 1
}

if [[ "$mode" != $heartbeat ]] && [[ "$mode" != $motion ]] 
then
  usage
fi

shift

if [[ "$1" == "" ]]
then
  usage
fi

send_command="python -u $dir/send.py $mode"

set -o pipefail

if [[ "$mode" == $motion ]]
then
  # action.sh pipes all the filenames to the sender program
  # always send text security alert first
  # send the previews as soon as they are ready and then
  # start sending full sized images
  $dir/action.sh 2 $@ | $dir/shrink.sh | cat $dir/alert.txt - | $send_command
else
  # to be used with cronjob mainly
  # to send a reassuring picture every half hour
  # from one of the devices
  $dir/action.sh 1 $@ | $send_command
fi
