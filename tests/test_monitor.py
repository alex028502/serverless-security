import subprocess
import time

import pytest

# this test is arguably redundant - it was written before the monitor test
# and now I accidentally put the indicator test in here

from .helpers.monitor import ctrl_key, wait_for_child_processes
from .helpers.path import env_with_extended_path


@pytest.fixture()
def monitor_env(plain_env, exe_path):
    return env_with_extended_path(
        dict(plain_env, GPIOZERO_PIN_FACTORY="mock"),
        exe_path["python"],
    )


@pytest.fixture()
def monitor_process(monitor_env, sut, dirname, tmp_path):
    # thanks https://stackoverflow.com/a/7389473
    logpath = "%s/output.log" % tmp_path
    log = open(logpath, "a")
    action_word = "action!"
    p = subprocess.Popen(
        [
            "python",
            "-u",
            "%s/monitor.py" % sut,
            "%s/mock/action.sh" % dirname,
            "3",
            action_word,
        ],
        # preexec_fn=os.setsid,
        env=monitor_env,
        close_fds=False,
        stdout=log,
    )
    time.sleep(1)
    yield p, logpath, action_word
    ctrl_key(p, "c")
    subprocess.run(
        ["cat", logpath],
        check=True,
    )
    time.sleep(0.5)


def test(sut, dirname, monitor_process):
    # instead of checking the actions through email, we are checking stdout
    # originally tried to avoid this, but now we need to check that the
    # indicator light is on, so might as well also check the action
    # to look at stdout while the process is running, just send it to a file
    # and read the file
    p, logfilepath, action_word = monitor_process
    time.sleep(3)
    # it's gonna be hard to find the information I am looking for in this log
    # in a meaningful way without just pasting the answer into the test
    wait_for_child_processes(p, 0)
    with open(logfilepath, "r") as f:
        initial_output = f.read()
        assert "listening to gpio here: mock" in initial_output
        print(initial_output)  # for debug
        for i in range(2):
            # the only reason we really run this twice is to check that the
            # indicator light turns off again
            ctrl_key(p, "\\")
            wait_for_child_processes(p, 1)
            wait_for_child_processes(p, 0)
            assert f.readline().strip() == "simulating motion", i
            assert f.readline().strip() == "indicator state: 0"
            assert f.readline().strip() == "indicator state: 0"
            assert f.readline().strip() == "motion detected"
            assert "kicked off" in f.readline()
            assert f.readline().strip() == "start %s" % action_word
            assert f.readline().strip() == "indicator state: 1"
            assert f.readline().strip() == "done %s" % action_word
            assert f.readline().strip() == "done monitor action"
