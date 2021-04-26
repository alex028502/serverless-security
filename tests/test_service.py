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
    batch_size = 2 * len(photos) + 1
    p, messages_folder = service
    assert not len(files_chrono(messages_folder))
    normal_state = 1
    wait_for_child_processes(p, normal_state)
    ctrl_key(p, "\\")
    wait_for_message(messages_folder, batch_size, 6)
    wait_for_child_processes(p, normal_state)
    print(files_chrono(messages_folder))
    ctrl_key(p, "\\")
    print(files_chrono(messages_folder))
    time.sleep(1)
    print(files_chrono(messages_folder))
    wait_for_message(messages_folder, 2 * batch_size, 6)
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

    # check the content of one message for one recipient
    # hopefully we check the details when we check the send
    # program
    recipient = config["recipients"][1]
    photo = photos[1]
    assert (
        find_words_in_inbox(alert, batch, keys_dir, recipient, config["sender"])
        == 1
    )
    assert (
        find_file_in_inbox(photo, batch, keys_dir, recipient, config["sender"])
        == 1
    )
    assert not find_words_in_inbox(
        "fish", batch, keys_dir, recipient, config["sender"]
    )
    # need to prove what happens when we can't find the file so just use this
    # file as an example:
    assert not find_file_in_inbox(
        __file__, batch, keys_dir, recipient, config["sender"]
    )

    # check one other recipient and photo to be sure
    # takes about 3 seconds each time so don't want to do this too much
    # but this should make us pretty confident that we are passing in the right
    # arguments to send to all users
    assert (
        find_file_in_inbox(
            photos[0],
            batch,
            keys_dir,
            config["recipients"][0],
            config["sender"],
        )
        == 1
    )

    # if the above went wrong we would probably notice by using the program
    # but the the thing that we might not notice is it it is not encyrpted at
    # all, or badly... and that is much harder to test as well
    with pytest.raises(Exception, match="assert not 2"):
        find_file_in_inbox(
            photos[0], batch, keys_dir, demo_keys[1], config["sender"]
        )
    # all we are really checking is the return code from the decryption
    # program so if we pass in arguments that fail for another reason
    # like wrong items in a dictionary, we will _might_ get a different
    # return code and know that we are not testing the right thing
    # we really confirmed that the right thing is happening by finding
    # this in the logs:
    # Error: Error decrypting message: Session key decryption failed.
    # but once we know that, just asserting the right return code
    # and hoping that if something changes that picks it up

    # CONSIDER DOING ONE OF THESE CHECKS IN CRON
