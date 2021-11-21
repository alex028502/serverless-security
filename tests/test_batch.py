import subprocess
import os
import sys
import time

import pytest

from .helpers.email import files_chrono
from .helpers.path import env_with_extended_path

from .helpers.send import (
    assert_photo_message,
    assert_text_message,
    message_from_file,
)

from .helpers.photos import photo_relationship, photo_fake_size, real_convert

MOTION = "motion"
HEARTBEAT = "heartbeat"
MODES = [HEARTBEAT, MOTION]


@pytest.fixture()
def env(plain_env, exe_path, send_env_vars, action_env_vars):
    return env_with_extended_path(
        dict(plain_env, **send_env_vars, **action_env_vars),
        *exe_path.values(),
    )


@pytest.fixture()
def encryptor(dirname):
    return "%s/mock/encryptor.py" % dirname


def batch(env, args, sut):
    p = subprocess.Popen(
        ["%s/batch.sh" % sut] + args,
        env=env,
        close_fds=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = p.communicate()[0].decode("UTF-8")
    sys.stdout.write(output)  # like using tee!
    return p.returncode, output


# TODO: speed up this test by making it just add a bad device for odd
# numbers in one mode and even numbers in the other mode
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("device_count", list(range(3)))
@pytest.mark.parametrize("bad_devices", [False, True])
def test_happy(
    env,
    email_server,
    email_config,
    photos,
    device_count,
    mode,
    sut,
    bad_device,
    bad_devices,
    encryptor,
    tmp_path,
):
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config

    assert not real_convert(env)

    # should work with and without bad devices in the list
    # usually the list is prefiltered in motion mode, and just handles all
    # the bad devices in cron mode but we can just make sure it always works
    # with and without a bad device in the list
    expected_photos = photos[:device_count]
    devices = " ".join([bad_device] * int(bad_devices) + expected_photos)
    returncode, output = batch(
        dict(env, SECURITY_CAMERA_DEVS=devices),
        [mode, encryptor],
        sut,
    )
    assert not returncode
    received_messages = files_chrono(messages_folder)
    print("check for duplicate timestamps or wrong number of items")
    subprocess.run(
        ["ls", "--full-time", str(messages_folder)],
        check=True,
    )

    if mode == MOTION:
        expected_messages = (
            ["security alert!"]
            + list(map(lambda x: "mini://%s" % x, expected_photos))
            + expected_photos
        )
    else:
        assert mode == HEARTBEAT
        if not device_count:
            expected_messages = ["technical difficulties"]
        else:
            expected_messages = expected_photos

    assert len(received_messages) == len(expected_messages)

    # this is my change to inspect the batch without encryption or compression
    # the entry point scripts will only be able to check the size of compressed
    # images and will have to decrypt messages

    mini_dir = tmp_path / "mini"
    mini_dir.mkdir()

    print(expected_messages)
    for received, expected in zip(received_messages, expected_messages):
        # I wrote mini like a "protocol" - because it looks cool
        mini_protocol = "mini://"
        received_msg = message_from_file(received)
        if ".jpg" not in expected:
            assert_text_message(expected, received_msg)
        elif mini_protocol not in expected:
            assert_photo_message(expected, received_msg)
        else:
            received_file = "%s/%s.jpg" % (mini_dir, time.time())
            # this method - until I refactor and make this a little less weird
            # returns the photo bytes if you don't give it something to compare
            # it to
            photo_content = assert_photo_message(None, received_msg)
            with open(received_file, "wb") as binary_file:
                binary_file.write(photo_content)
            expected_photo_path = expected.replace(mini_protocol, "")
            assert (
                photo_relationship(received_file, expected_photo_path)
                == "different meta data"
            )
            assert photo_fake_size(received_file) == "128x128"


@pytest.mark.parametrize("situation", ["no args", "bad mode", "bad encryptor"])
def test_unhappy(env, email_server, email_config, photos, situation, sut):
    if situation == "no args":
        args = []
    elif situation == "bad encryptor":
        args = ["heartbeat", "not/a/real/path"]
    else:
        assert situation == "bad mode"
        args = ["hello"]

    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config
    devices = " ".join(photos)
    returncode, output = batch(
        dict(os.environ, **env, SECURITY_CAMERA_DEVS=devices),
        args,
        sut,
    )
    assert returncode
    received_messages = files_chrono(messages_folder)
    assert len(received_messages) == 0
    assert "usage" in output
