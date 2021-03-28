#! /usr/bin/env bash

# only start sending names of full files once all previews are sent

set -e


files=""

# cool it processes stdin!
while read line
do
  preview=$line.preview.jpg
  convert $line -resize 128x128 $preview
  ls $preview
  files="$files $line"
done # < /dev/stdin makes test coverage fail

echo $files | xargs -n1 echo
