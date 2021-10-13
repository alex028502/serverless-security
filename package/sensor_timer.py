import time

delay = 0.1


def sensor_timer(sensor, light, output):
    while True:
        time.sleep(delay)
        yield
