import subprocess
import os
import sys
import time
from threading import Thread
import signal

from gpiozero import MotionSensor

# from signal import pause

from unit import conditional_message

command = sys.argv[1:]

print("getting ready to run the following command whenever there is action")
print(" ".join(command))
print("listening to gpio here: %s" % os.getenv("GPIOZERO_PIN_FACTORY"))


# oops - turns out I need to do this:
def number(string):
    if "." in string:
        return float(string)
    return int(string)


tuning = dict(
    zip(
        ("queue_len", "sample_rate", "threshold"),
        map(number, os.getenv("SECURITY_CAMERA_TUNING").split(":")),
    )
)

print("camera sensitivity: %s" % tuning)

sensor = MotionSensor(4, **tuning)


def action():
    # time.sleep(.3)
    print("motion detected")
    p = subprocess.Popen(command, close_fds=False)
    print("kicked off %s" % p.pid)
    p.communicate()
    if p.returncode:
        print("command failed: %s" % command)
    print("done monitor action")


def process_signal(*args):
    simulator = Thread(target=simulate)
    simulator.start()


def simulate():
    conditional_message(not is_mock(), "error coming; not using mock pins")
    conditional_message(is_mock(), "simulating motion")
    sensor.pin.drive_high()
    time.sleep(0.1)
    sensor.pin.drive_low()


signal.signal(signal.SIGQUIT, process_signal)


def is_mock():
    return os.getenv("GPIOZERO_PIN_FACTORY") == "mock"


conditional_message(is_mock(), "use ctrl+\\ to simulate a click")

while True:
    if sensor.value:
        action()
    time.sleep(0.01)
