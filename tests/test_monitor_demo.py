import os
import subprocess
import time

import pytest

from .helpers.monitor import ctrl_key

# this tests the script monitor.sh that is in the project root for manually
# testing the monitor script.  the script works in mock mode and native mode
# if you are on a raspberry pi 4 as a desktop, or run it on the target system
# and watch it on ssh


def file_content(path):
    with open(path, "r") as file:
        return file.read()


def wait_for_count_in_file(string, path, expected, limit):
    start_time = time.time()
    while True:
        actual = file_content(path).count(string)
        if actual == expected:
            break
        assert time.time() - start_time < limit, (actual, file_content(path))
        time.sleep(0.1)


@pytest.fixture()
def monitor_demo_script(sut):
    return "%s/monitor.sh" % sut, "simulate", "TEST"


@pytest.fixture()
def log(tmp_path):
    path = "%s/monitor.log" % tmp_path
    file_handle = open(path, "w")
    yield file_handle, path
    file_handle.close()


@pytest.fixture()
def monitor_demo_process(monitor_demo_script, main_env, tmp_path, log):
    script, ready_code, action_code = monitor_demo_script
    env = dict(os.environ, **main_env)
    log_file, log_file_path = log

    p = subprocess.Popen(
        [script],
        env=env,
        close_fds=False,
        stderr=subprocess.STDOUT,
        stdout=log_file,
    )

    yield p, log_file_path, ready_code, action_code

    ctrl_key(p, "c")

    time.sleep(0.1)


@pytest.fixture()
def monitor_demo_ready(monitor_demo_process):
    p, log_file_path, ready_code, action_code = monitor_demo_process
    start_time = time.time()
    while ready_code not in file_content(log_file_path):
        assert time.time() - start_time < 3, file_content(log_file_path)
        time.sleep(0.1)

    return p, log_file_path, action_code


def test_the_file(monitor_demo_script):
    path, ready_code, action_code = monitor_demo_script
    with open(path) as file:
        assert action_code in file.read()
    # start code is harder to test
    # so we'll find out the hard way if we change it!


def test_the_process(monitor_demo_ready):
    p, log_file_path, action_code = monitor_demo_ready
    initial_content = file_content(log_file_path)
    assert action_code in initial_content, "one at start"
    assert initial_content.count(action_code) == 1, initial_content
    print("first try")
    ctrl_key(p, "\\")
    wait_for_count_in_file(action_code, log_file_path, 2, 3)
    time.sleep(0.1)
    print("second try")
    ctrl_key(p, "\\")
    wait_for_count_in_file(action_code, log_file_path, 3, 3)
