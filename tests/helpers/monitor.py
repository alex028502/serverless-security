import signal
import os
import time

import psutil


def ctrl_key(p, key):
    # the terminal sends a signal to every process in a group
    # instead of starting the subprocess in its own group, like thsi:
    # preexec_fn=os.setsid
    # which can mess us up later when we try to use ctrl+c to stop the tests,
    # we'll just make a list of all the whole process family, and send the
    # signal to all processes - so command line test tools we create should
    # work the same in the tests
    # thanks https://stackoverflow.com/a/38509696
    ps = [p] + list(psutil.Process(p.pid).children(recursive=True))
    for subp in ps:
        print("sending %s to %s" % (key, subp.pid))
        # subp.send_signal(lookup_signal(key))
        os.kill(subp.pid, lookup_signal(key))
    # for subp in ps:
    # print("see if %s is still there" % subp.pid)
    # subprocess.run("ps aux | grep %s | grep -v grep" % subp.pid, shell=True)


def lookup_signal(key):
    signals = {
        "c": signal.SIGINT,
        "\\": signal.SIGQUIT,
        "z": signal.SIGTSTP,
    }

    return signals[key.lower()]


def wait_for_child_processes(p, n):
    start = time.time()
    while len(psutil.Process(p.pid).children()) != n:
        assert time.time() - start < 5, psutil.Process(p.pid).children()
        time.sleep(0.2)
    time.sleep(0.4)
