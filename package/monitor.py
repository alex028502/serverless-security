import subprocess
import os
import sys
import time
from threading import Thread
import signal

from gpiozero import Button

# from signal import pause

from unit import conditional_message

command = sys.argv[1:]

print("getting ready to run the following command whenever there is action")
print(" ".join(command))
print("listening to gpio here: %s" % os.getenv("GPIOZERO_PIN_FACTORY"))

sensor = Button(4, pull_up=True)


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
    sensor.pin.drive_low()
    time.sleep(0.2)
    sensor.pin.drive_high()


signal.signal(signal.SIGQUIT, process_signal)


def is_mock():
    return os.getenv("GPIOZERO_PIN_FACTORY") == "mock"


conditional_message(is_mock(), "use ctrl+\\ to simulate a click")

while True:
    if sensor.is_pressed:
        action()
    time.sleep(0.1)
