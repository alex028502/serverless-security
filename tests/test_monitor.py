import os
import sys
import subprocess
import time

import pytest

# this test is a cross between the email test and the monitor test!
from .helpers.email import files_chrono, wait_for_message
from .helpers.monitor import ctrl_key, wait_for_child_processes

# this test is arguably redundant - it was written before the monitor test
# program, and then I wrote the test program to figure it out.  I originally
# wrote this so that I wouldn't have to figure out how to watch the output
# of a process, and thought sending email would be easier
# but actually there was no avoiding it


@pytest.fixture()
def monitor_env(component_env):
    return dict(
        component_env,
        _SECURITY_CAMERA_DATA="",
    )


@pytest.fixture()
def monitor_process(email_server, monitor_env, sut):
    port = email_server[0]
    mail_command = [
        sys.executable,
        "tools/mail.py",
        "localhost",
        str(port),
        "tester",
        "hello",
    ]
    env = dict(os.environ, DELAY_AFTER_MAIL="0.5", **monitor_env)
    p = subprocess.Popen(
        ["python", "-u", "%s/monitor.py" % sut] + mail_command,
        # preexec_fn=os.setsid,
        env=env,
        close_fds=False,
        # stderr=sudprocess.PIPE, # do not test logging; just output for debug
    )
    time.sleep(1)
    yield p, email_server[1], mail_command
    ctrl_key(p, "c")
    time.sleep(0.5)


def test(monitor_process):
    p, messages_folder, mail_command = monitor_process
    assert not len(files_chrono(messages_folder))
    # first just try the mail command
    print("messags in", messages_folder)
    subprocess.Popen(
        mail_command,
        close_fds=False,
        stderr=subprocess.STDOUT,
    ).communicate()
    wait_for_message(messages_folder, 1, 4)
    ctrl_key(p, "\\")
    wait_for_child_processes(p, 1)
    wait_for_message(messages_folder, 2, 4)
    wait_for_child_processes(p, 0)
    ctrl_key(p, "\\")
    wait_for_child_processes(p, 1)
    wait_for_message(messages_folder, 3, 4)
    wait_for_child_processes(p, 0)
    sender, message = mail_command[-2:]  # trust me
    last_message_path = files_chrono(messages_folder)[-1]
    assert sender in last_message_path
    with open(last_message_path, "r") as last_message_file:
        last_message = last_message_file.read()
    assert last_message.strip() == message.strip()
    time.sleep(0.1)
    wait_for_child_processes(p, 0)
