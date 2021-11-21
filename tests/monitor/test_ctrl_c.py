import subprocess
import time

from .helpers import ctrl_key


def search_processes(identifier):
    p = subprocess.run(
        "ps axo pid,ppid,pgrp,command | grep -w %s | grep -v grep" % identifier,
        shell=True,
        capture_output=True,
        # stderr=subprocess.STDOUT,
        # stdout=subprocess.PIPE,
    )
    assert not p.stderr, p.stdout
    return list(filter(str.strip, p.stdout.decode("UTF-8").split("\n")))


def get_identifier():
    # the identifier is also the time passed to sleep
    # so somewhere between 1 and 2 minutes is good in case the clean-up
    # doesn't work, and has a really long fraction to make it _almost_
    # impossible to get the same one twice
    return str(time.time() % 60 + 60)


def test():
    identifier = get_identifier()
    assert not len(search_processes(identifier)), "That's unfortunate!!!"
    # create a background process with no cleanup - since when it passes it'll
    # clean itself up and when it fails, it'll expire in a couple minutes
    p = subprocess.Popen(
        ["tests/process-explosion.sh", str(identifier)],
        close_fds=False,
    )
    time.sleep(0.1)
    assert len(search_processes(identifier)) == 3

    ctrl_key(p, "c")

    time.sleep(0.1)

    assert not len(search_processes(identifier))
