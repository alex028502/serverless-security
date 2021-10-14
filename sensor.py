import time
import os
from package import sensor_timer
from unittest import TestCase

print("testing sensor and sensor timer")

TestCase().assertEqual(os.getenv("GPIOZERO_PIN_FACTORY"), "mock")

# this package will test itself since importing here changes the path to the
# sensor_timer import!
__import__("package.sensor")
# this works with a regular import too except flake8 doesn't like that it
# is unused, and doesn't like that it's not at the top


# let's make it take about one second
c = int(1.0 / sensor_timer.delay)
start_time = time.time()
generator = sensor_timer.sensor_timer(1, 2, 3)
for i in range(c):
    next(generator)

ellapsed_time = time.time() - start_time
assert ellapsed_time > 0.5, ellapsed_time
assert ellapsed_time < 1.5, ellapsed_time
print("done testing sensor timer")
print()
