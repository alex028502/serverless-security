import sys
import subprocess
import time

import pytest

# this test is a cross between the email test and the monitor test!
from .helpers.email import files_chrono, wait_for_message
from .helpers.monitor import ctrl_key, wait_for_child_processes
from .helpers.path import env_with_extended_path

# this test is arguably redundant - it was written before the monitor test
# program, and then I wrote the test program to figure it out.  I originally
# wrote this so that I wouldn't have to figure out how to watch the output
# of a process, and thought sending email would be easier
# but actually there was no avoiding it


@pytest.fixture()
def monitor_env(plain_env, exe_path):
    return env_with_extended_path(
        dict(plain_env, GPIOZERO_PIN_FACTORY="mock"),
        exe_path["python"],
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
    env = dict(monitor_env, DELAY_AFTER_MAIL="0.5")
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


@pytest.fixture()
def monitor_process_stdout(monitor_env, sut, dirname, tmp_path):
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
    time.sleep(0.5)


def test(plain_env, monitor_process):
    p, messages_folder, mail_command = monitor_process
    assert not len(files_chrono(messages_folder))
    # first just try the mail command
    print("messags in", messages_folder)
    subprocess.Popen(
        mail_command,
        close_fds=False,
        stderr=subprocess.STDOUT,
        env=plain_env,
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


# TODO: now that we are testing with stdout, delete email test above?
def test_indicator(sut, dirname, monitor_process_stdout):
    # instead of checking the actions through email, we are checking stdout
    # originally tried to avoid this, but now we need to check that the
    # indicator light is on, so might as well also check the action
    # to look at stdout while the process is running, just send it to a file
    # and read the file
    p, logfilepath, action_word = monitor_process_stdout
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
