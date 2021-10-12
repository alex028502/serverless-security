def sensor_timer(sensor, light, output):
    print("TESTING")
    # assert 3 == do_if_true(gimme3, True)
    # assert not do_if_true(gimme3, False)
    sensor[0].pin.drive_low()
    sensor[1].pin.drive_low()
    yield
    assert not light[0].value
    assert not light[1].value
    assert output.value
    yield
    sensor[0].pin.drive_high()
    yield
    assert light[0].value
    assert not light[1].value
    assert output.value
    yield
    sensor[1].pin.drive_high()
    yield
    assert light[0].value
    assert light[1].value
    assert not output.value
    yield
    sensor[0].pin.drive_low()
    yield
    assert not light[0].value
    assert light[1].value
    assert output.value
    yield
    print("DONE TESTING")
