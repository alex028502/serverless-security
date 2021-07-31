#! /usr/bin/env bash

set -e

# so far this script is only to get a relative path into the configuration

if [[ "$SECURITY_LIVE_TARGET" == "" ]]
then
  echo '{}'
  exit 0
fi

# wish I could figure out 'read'
target_host=$(echo $SECURITY_LIVE_TARGET | cut -f 1 -d':')
target_path=$(echo $SECURITY_LIVE_TARGET | cut -f 2 -d':')

if [[ "$1" == "--list" ]]
then
  echo "{\"prod\": [\"$target_host\"]}"
  exit 0
fi

cd "$(dirname "$0")"
cd ../..

interpreter=$(which python3)

cat <<EOF
{
  "security_camera_home": "$target_path",
  "ansible_python_interpreter": "python3"
}
EOF
