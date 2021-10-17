import time
import sys

from sensor_pins import led, relay

delay = float(sys.argv[1])

print("all off")
led[0].off()
led[1].off()
relay.off()

time.sleep(delay)

print("click")
relay.on()

time.sleep(delay)

print("led 0")
led[0].on()

time.sleep(delay)

print("led 1")
led[1].on()

time.sleep(delay)

print("click")
relay.off()
