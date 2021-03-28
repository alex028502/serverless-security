import subprocess
import time
import os

import pytest

from .helpers.email import files_chrono, wait_for_message
from .helpers.monitor import ctrl_key, wait_for_child_processes
from .helpers.send import (
    message_from_file,
    assert_format,
    asc_from_msg,
    msg_from_asc,
    compare_content_to_path,
)


def start_service(env, *args):
    return subprocess.Popen(
        args,
        # preexec_fn=os.setsid,
        env=env,
        close_fds=False,
        stderr=subprocess.STDOUT,
    )


@pytest.fixture()
def env(main_env):
    return {**os.environ, **main_env}


@pytest.fixture()
def service(email_server, env, sut):
    p = start_service(env, "%s/service.sh" % sut)
    time.sleep(1)
    yield p, email_server[1]
    ctrl_key(p, "c")
    time.sleep(1)


@pytest.fixture()
def broken_camera(photos, bad_device, env, email_server, sut):
    device_file_path = "%s/devices.txt" % env["SECURITY_CAMERA_HOME"]
    # it comes with the two good devices so replace it with one good one and
    # one bad one
    with open(device_file_path, "w") as f:
        f.write(photos[0] + "\n" + bad_device + "\n")
    p = start_service(env, "%s/service.sh" % sut)
    time.sleep(1)
    yield p, email_server[1]
    ctrl_key(p, "c")
    time.sleep(1)


@pytest.fixture()
def misconfigured(env, email_server, sut):
    # empty device file for example
    device_file_path = "%s/devices.txt" % env["SECURITY_CAMERA_HOME"]
    with open(device_file_path, "w") as f:
        f.write("\n")
    p = start_service(env, "%s/service.sh" % sut)
    time.sleep(1)
    yield p, email_server[1]
    ctrl_key(p, "c")
    time.sleep(1)


@pytest.fixture()
def alert(sut):
    # too hard to extract from file so we just hard code and check it
    value = "security alert"
    with open("%s/alert.txt" % sut, "r") as alert_txt:
        assert value in alert_txt.read()
    return value


def check_all_message_headers(paths, config):
    for path in paths:
        msg = message_from_file(path)
        assert_format(
            msg,
            config["sender"],
            config["recipients"],
            "motion",
        )


def decrypt_messages(paths, keys_dir, recipient, sender):
    for path in paths:
        encrypted_msg = message_from_file(path)
        asc = asc_from_msg(encrypted_msg)
        msg, status = msg_from_asc(asc, keys_dir, recipient, sender)
        assert not status
        yield msg


def find_file_in_inbox(file_path, *args):
    total = 0
    for msg in decrypt_messages(*args):
        content = msg.get_content()
        if type(content) != bytes:
            #             print("skip because " + type(content))
            continue
        if not compare_content_to_path(content, file_path):
            #             print("got", content)
            total = total + 1
    return total


def find_words_in_inbox(string, *args):
    total = 0
    for msg in decrypt_messages(*args):
        if string in str(msg):
            total = total + 1
    return total


# def test_env(main_env):
#
#     p = subprocess.Popen(
#         ["python", "--version"], stdout=subprocess.PIPE, env=env
#     )
#     stdout, stderr = p.communicate()
#     assert not stderr  # because it is not being captured
#     assert "Python 3" in stdout.decode("UTF-8")


def test(service, demo_keys, main_env, photos, email_config, alert):
    (config_dir, config) = email_config
    keys_dir = demo_keys[0]
    batch_size = 9
    p, messages_folder = service
    assert not len(files_chrono(messages_folder))
    normal_state = 1
    wait_for_child_processes(p, normal_state)
    ctrl_key(p, "\\")
    wait_for_message(messages_folder, batch_size, 4)
    wait_for_child_processes(p, normal_state)
    ctrl_key(p, "\\")
    wait_for_message(messages_folder, 2 * batch_size, 4)
    wait_for_child_processes(p, normal_state)

    # the following is not that thorough, but hopefully as bugs appear we will
    # think of better tests. We are just making sure that all recipients can
    # read all messages and that the full sized photos are in there somewhere
    # we are not checking the reduced images
    batch = files_chrono(messages_folder)[-batch_size:]
    assert len(batch) == batch_size
    # so that should contain two 4 low res images and 4 high res images
    # oh wait check maybe let's just make sure that the pictures taken add up
    all_pictures_taken = files_chrono(
        main_env["SECURITY_CAMERA_HOME"] + "/data"
    )
    assert len(all_pictures_taken) == (batch_size - 1) * 2
    check_all_message_headers(batch, config)
    for recipient in config["recipients"]:
        assert (
            find_words_in_inbox(
                alert, batch, keys_dir, recipient, config["sender"]
            )
            == 1
        )
        for photo in photos:
            assert (
                find_file_in_inbox(
                    photo, batch, keys_dir, recipient, config["sender"]
                )
                == 2
            )
    assert not find_words_in_inbox(
        "fish", batch, keys_dir, recipient, config["sender"]
    )
    # need to prove what happens when we can't find the file so just use this
    # file as an example:
    assert not find_file_in_inbox(
        __file__, batch, keys_dir, recipient, config["sender"]
    )


def test_broken_camera(broken_camera):
    p, messages_folder = broken_camera
    assert not len(files_chrono(messages_folder))
    normal_state = 1
    wait_for_child_processes(p, normal_state)
    ctrl_key(p, "\\")
    wait_for_message(messages_folder, 5, 4)
    wait_for_child_processes(p, normal_state)
    time.sleep(0.1)
    ctrl_key(p, "\\")
    wait_for_message(messages_folder, 10, 4)
    wait_for_child_processes(p, normal_state)


def test_misconfigured(misconfigured):
    p, messages_folder = misconfigured
    assert not len(files_chrono(messages_folder))
    normal_state = 1
    wait_for_child_processes(p, normal_state)
    ctrl_key(p, "\\")
    wait_for_child_processes(p, normal_state)
    time.sleep(0.3)
    # we should not even get the test message because batch fails due to
    # misconfiguration and not missing cameras when no cameras are given at all
    assert not len(files_chrono(messages_folder))
