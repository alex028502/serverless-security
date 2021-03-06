#! /usr/bin/env bash

set -e

./tools/test.sh

venv/bin/python misc/unit.py package/unit.py

user=$(venv/bin/python tools/service_value.py setup/sensor.service.j2 Service User)
tools/assert.sh $user == pi

venv/bin/python tools/path_compare.py $PWD $PWD
venv/bin/python tools/path_compare.py $PWD/tools ./tools
tools/expect-failure.sh venv/bin/python tools/path_compare.py $PWD ./tools
tools/expect-failure.sh venv/bin/python tools/path_compare.py $PWD
tools/expect-failure.sh venv/bin/python tools/path_compare.py

venv/bin/python tools/server-action/test.py

./tools/venv-run.sh $PWD/venv ./misc/be-quiet.sh $PWD/package/unit.py

./misc/check-ignore.sh

venv/bin/python -m pytest tests -xv
