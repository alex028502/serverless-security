#! /usr/bin/env bash

set -e

tmp_path=$_SECURITY_CAMERA_DATA/test-$(date +%s).jpg

for device in $SECURITY_CAMERA_DEVS
do
  echo checking $device >&2
  rm -f $tmp_path
  if fswebcam --device $device $tmp_path >&2 && ls $tmp_path >&2
  then
    echo $device
  fi
done

rm -f $tmp_path
