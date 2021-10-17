#! /usr/bin/env bash

set -e

./tools/test.sh

venv/bin/python unit.py
GPIOZERO_PIN_FACTORY=mock venv/bin/python package/sensor.py misc/sensor_timer.py

venv/bin/python tools/path_compare.py $PWD $PWD
venv/bin/python tools/path_compare.py $PWD/tools ./tools
tools/expect-failure.sh venv/bin/python tools/path_compare.py $PWD ./tools
tools/expect-failure.sh venv/bin/python tools/path_compare.py $PWD
tools/expect-failure.sh venv/bin/python tools/path_compare.py

venv/bin/python tools/server-action/test.py

source venv/bin/activate
./misc/be-quiet.sh $PWD/package/unit.py
deactivate

./check-ignore.sh

venv/bin/python -m pytest tests -xv
