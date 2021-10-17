import sys
import importlib

# in the dev venv it works without import importlib.util
# I even tried installing the dev requirements in another environment
# and it was still needed - maybe it's because of the coverage lib?
# anyway - good thing we have the e2e test - here is somebody else that was
# also confused: https://bugs.python.org/issue41958
# so don't remove this just because the main tests pass without it
# it confused this guy too
# https://stackoverflow.com/questions/66797668/module-importlib-has-no-attribute-util
import importlib.util

from sensor_pins import pir, led, relay

sensor_timer_path = sys.argv[1]

sensor_timer_spec = importlib.util.spec_from_file_location(
    "sensor_timer",
    sensor_timer_path,
)
sensor_timer = importlib.util.module_from_spec(sensor_timer_spec)
sensor_timer_spec.loader.exec_module(sensor_timer)


assert len(led) == len(pir)

for i in sensor_timer.sensor_timer(pir, led, relay):
    answers = ""
    for idx in range(len(pir)):
        if pir[idx].is_pressed:
            led[idx].on()
            answers += "X"
        else:
            led[idx].off()
            answers += "O"

    if answers == len(pir) * "X":
        relay.off()
    else:
        relay.on()
