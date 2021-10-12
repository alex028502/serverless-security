import time

from gpiozero import Button, LED

from sensor_timer import sensor_timer

sensor = []
sensor.append(Button(16, pull_up=False))
sensor.append(Button(20, pull_up=False))

light = []
light.append(LED(19))
light.append(LED(26))

output = LED(21)

assert len(light) == len(sensor)

last_answers = "OK"

for i in sensor_timer(sensor, light, output):
    answers = ""
    for idx in range(len(sensor)):
        if sensor[idx].is_pressed:
            light[idx].on()
            answers += "X"
        else:
            light[idx].off()
            answers += "O"

    if answers == len(sensor) * "X":
        output.off()
    else:
        output.on()

    if last_answers != answers:
        print("%s - %s" % (answers, time.time()))

    last_answers = answers
