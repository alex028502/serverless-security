import os
import subprocess
import time

import pytest

from .helpers.monitor import ctrl_key

# here we just prove that the wrapper injector script
# runs - we can't do anything to the mock pins


@pytest.fixture()
def sensor_p(main_env, sut):
    p = subprocess.Popen(
        ["%s/sensor.sh" % sut],
        env=dict(os.environ, **main_env),
        close_fds=False,
        stderr=subprocess.STDOUT,
    )
    yield p
    ctrl_key(p, "c")
    time.sleep(1)


@pytest.fixture()
def sleep_p():
    p = subprocess.Popen(
        ["sleep", "infinity"],  # don't try this on a mac?
        stderr=subprocess.STDOUT,
    )
    yield p
    ctrl_key(p, "c")
    time.sleep(0.3)


def test(sensor_p, sleep_p):
    # https://stackoverflow.com/a/43276598

    assert sensor_p.poll() is None
    # see watch this:
    echo_p = subprocess.Popen(
        ["echo", "test"],
        stderr=subprocess.STDOUT,
    )
    ls_p = subprocess.Popen(
        ["ls", "testxyz"],
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)
    # just show what all the possible values are
    # and that our program matches the one for a
    # running process
    assert echo_p.poll() == 0
    assert ls_p.poll() == 2
    assert sleep_p.poll() is None
    assert sensor_p.poll() is None
    # or to put it another way
    assert sensor_p.poll() is not echo_p.poll()
    assert sensor_p.poll() is not ls_p.poll()
    assert sensor_p.poll() is sleep_p.poll()


# this test doesn't do much but let's just make sure we
# don't do anythign to stop this useful test program from compiling
# and running successfully
# if we ever feel like we really need to test this, then we can use the same
# sensor timer as for the sensor program, and just check that no matter what
# we set the inputs to the outputs follow the planned pattern
def test_check_sensor_pins(bin_dir, sut):
    p = subprocess.Popen(
        ["%s/python" % bin_dir, "%s/check_sensor_pins.py" % sut, ".01"],
        env=dict(os.environ, GPIOZERO_PIN_FACTORY="mock"),
        stderr=subprocess.STDOUT,
    )

    p.communicate()
    assert not p.returncode


def test_actions(bin_dir, sut, dirname):
    test_cases = {
        "oo": "001",
        "oi": "011",
        "ii": "110",
        "io": "101",
    }

    # the third digit can be derived from the other two
    # the output is low if both lights are high:
    for vals in test_cases.values():
        val = list(map(int, vals))
        assert (val[0] and val[1]) == (not val[2])
    # the input button is set to pull_up=True
    # so we can press the button with a low signal

    test_input = "\n".join(test_cases.keys()) + "\n"
    expected_output = "\n".join(test_cases.values()) + "\n"
    p = subprocess.Popen(
        [
            "%s/python" % bin_dir,
            "%s/sensor.py" % sut,
            "%s/mock/sensor_timer.py" % dirname,
        ],
        env=dict(os.environ, GPIOZERO_PIN_FACTORY="mock"),
        close_fds=False,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    output = p.communicate(input=test_input.encode("utf-8"))[0]
    assert output.decode("utf-8") == expected_output
