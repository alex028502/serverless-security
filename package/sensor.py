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

# I got a lot of false alarms from a single PIR sensor, so I put two PIR
# sensors instead.  They both have to be on to trigger the alarm. This program
# aggregates the results, and sends it to another GPIO output so that that can
# be used to activate them main program (but 'pushing a button') that takes a
# picture and sends the encrypted email. I used GPIO so that I could manually
# debug the connection between the two subsystems, because there is not
# automated test doing that.

# I think I have this problem
# https://forums.raspberrypi.com/viewtopic.php?t=254103 except that one is
# happening every 16 minutes and mine is happening every 5 minutes.
# Once I put two of them, it almost never happens (but still happens sometimes).
# I guess the odds of both PIR sensors finding themselves in the path of the
# thing that happens every 5 minutes and sets them off is quite slim. If I
# logged the sensor input, I could catch it doing it with one of the PIR
# sensors and not the other, but I haven't done that.

# Initially when I decided I needed two PIR sensors, I connected them to two
# relay modules, and then put the output of the relay modules in series. That
# worked great, until it stopped working all of a sudden. Then I realised that
# these were five volt relay modules. I ordered some 3V relay modules... that
# almost don't exist. I replaced my relays with the 3V ones, and that didn't
# work either.  Then I read somewhere that one of the kinds of 3V relay modules
# I got was flawed, and that it still requires 5V because of an optocoupler. So
# instead of using relays in series, I thought it would be quite easy to do with
# an arduino... except then I would have to figure
# out how to test the arduino program, or it would just seem like a way to
# avoid testing, and it would be twice as hard to deploy. Then I found out what
# I always assumed was not the case, that two different programs on the same
# raspberry pi can use different GPIO pins. So I replaced the two relays with
# their outputs in series, and their inputs connected to the PIR sensors with
# a second raspberry pi (this one), but still connected it to the input of the
# existing program using GPIO as though it is an external device, and I did
# that with a 3V relay so that I didn't risk connecting an output pin to an
# input pin incorrectly. I used the kind of 3V relay that didn't have the
# supposed 5V optocoupler flaw in it, and that worked great! ... until it
# stoppped working, and the LEDS on the relay module went on but the circuit
# didn't close. So then I asked a question on stack exchange and got over
# my fear of connecting two GPIO pins together, and removed the relay from the
# equaion, having learned that relay modules have their own nuances.

# Before using PIR motion sensors, or maybe after, I tried with a sonar trip
# wire connected to an arduino, running a program full of "heuristics" that I
# worked out using trial and error. Arduino,  having a 5V output, could easily
# send a signal to the input pin of my raspberry pi through a relay module.  I
# ran a phone cable across the room, because the optimal place for the camera
# wasn't the same as the optimal place for the _sonar unit_. It worked great
# but I wanted something more compact that could compete with my nest cam for
# convenience. Also, I bet the sonar trip wire would have also had nuances
# once I used it for a while.
