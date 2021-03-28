#! /usr/bin/env bash

set -e

cd $(dirname $0)
source assert-env.sh

devices="${@:2}"
times=$1

function message {
  # write all messages to stderr because stdout is consumed by send.py
  echo $@ 1>&2
}

assert_env_value _SECURITY_CAMERA_DATA
ls $_SECURITY_CAMERA_DATA > /dev/null

for x in $(seq $times)
do
  for device in $devices
  do
    # raspberrypi doens't seem to have uuidgen even when you install util-linux
    # suffix=$(uuidgen | sed 's/-//g' | cut -c1-10) # will _usually_ be unique
    tstamp=$(date +%s)
    filepath=$(./filename.sh $_SECURITY_CAMERA_DATA $tstamp jpg)
    message trying to capture $filepath with $device
    fswebcam --device $device $filepath 1>&2 || message failure?
    if ls $filepath # this is the only stdout this produces
    then
      message success $filepath
    else
      message failure $filepath
    fi
  done
done

message done action script

# have to save this cool snippet somewhere this is how to prefix every line if
# we write to a log file
# set -o pipefail
# venv/bin/python action.py $@ 2>&1 | sed -e "s/^/${1}: /"
