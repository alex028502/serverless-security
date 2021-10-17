import sys


def sensor_timer(sensor, light, output):
    for actions in sys.stdin:
        for i in range(2):
            action = actions[i]
            if action == "i":
                sensor[i].pin.drive_high()
            else:
                assert action == "o"
                sensor[i].pin.drive_low()
        yield
        print("%s%s%s" % (light[0].value, light[1].value, output.value))
