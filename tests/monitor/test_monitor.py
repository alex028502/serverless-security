import time

import psutil


from .helpers import ctrl_key, wait_for_child_processes

# this tests the script monitor.sh that is in the project root for manually
# testing the monitor script.  the script works in mock mode and native mode
# if you are on a raspberry pi 4 as a desktop, or run it on the target system
# and watch it on ssh


def test_the_file(monitor_demo_script):
    path, ready_code, action_code = monitor_demo_script
    with open(path) as file:
        assert action_code in file.read()
    # start code is harder to test
    # so we'll find out the hard way if we change it!


def test_indicator(sut, dirname, monitor_demo_ready):
    monitor_process = monitor_demo_ready
    # instead of checking the actions through email, we are checking stdout
    # originally tried to avoid this, but now we need to check that the
    # indicator light is on, so might as well also check the action
    # to look at stdout while the process is running, just send it to a file
    # and read the file
    p, logfilepath, action_word = monitor_process
    # small correction for waiting for child process
    cp = psutil.Process(p.pid).children()[0]
    time.sleep(3)
    # it's gonna be hard to find the information I am looking for in this log
    # in a meaningful way without just pasting the answer into the test
    wait_for_child_processes(cp, 0)
    with open(logfilepath, "r") as f:
        initial_output = f.read()
        assert "listening to gpio here: mock" in initial_output
        print(initial_output)  # for debug
        for i in range(2):
            # the only reason we really run this twice is to check that the
            # indicator light turns off again
            ctrl_key(p, "\\")
            wait_for_child_processes(cp, 1)
            wait_for_child_processes(cp, 0)
            assert f.readline().strip() == "simulating motion", i
            assert f.readline().strip() == "indicator state: 0"
            assert f.readline().strip() == "indicator state: 0"
            assert f.readline().strip() == "motion detected"
            assert "kicked off" in f.readline()
            assert f.readline().strip() == "start %s" % action_word
            assert f.readline().strip() == "indicator state: 1"
            assert f.readline().strip() == "done %s" % action_word
            assert f.readline().strip() == "done monitor action"
