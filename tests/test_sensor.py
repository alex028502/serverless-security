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
