#! /usr/bin/env bash

set -e

# so far this script is only to get a relative path into the configuration

if [[ "$1" == "--list" ]]
then
  echo '{"default": ["test"]}'
  exit 0
fi

interpreter=$(which python3)

cat <<EOF
{
  "ansible_connection": "local",
  "security_camera_home": "$PWD/.target",
  "security_camera_tuning": "8:8:1",
  "ansible_python_interpreter": "$interpreter"
}
EOF

# we don't have to worry about what is in the host
# argument - we only have one for now
