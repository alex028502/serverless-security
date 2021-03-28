import subprocess
import os
import sys

import pytest

from .helpers.email import files_chrono


@pytest.fixture()
def env(main_env, bad_device):
    # add a bunch of entries to the device file
    # I hope there aren't any spaces in the path!
    device_file_path = main_env["SECURITY_CAMERA_HOME"] + "/devices.txt"
    with open(device_file_path, "a") as f:
        for i in range(5):
            f.write(bad_device + "\n")
    return main_env


def cron(env, sut, idx):
    p = subprocess.Popen(
        ["%s/cron.sh" % sut, str(idx)],
        env=env,
        close_fds=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = p.communicate()[0].decode("UTF-8")
    sys.stdout.write(output)  # like using tee!
    return p.returncode, output


@pytest.mark.parametrize("device_idx", [1, 2])
def test_happy(env, email_server, email_config, device_idx, sut, photos):
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config

    assert device_idx - 1 <= len(photos)  # number of good devices

    returncode, output = cron(dict(os.environ, **env), sut, device_idx)
    assert not returncode
    received_messages = files_chrono(messages_folder)

    assert len(received_messages) == 1
    assert "usage" not in output
    # TODO check for the right picture - must match the idx


@pytest.mark.parametrize("situation", ["BAD_CAMERA", "NON_CAMERA"])
def test_unhappy(env, email_server, email_config, photos, situation, sut):
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config

    if situation == "BAD_CAMERA":
        device_idx = len(photos) + 2
    else:
        assert situation == "NON_CAMERA"
        device_idx = len(photos) + 20

    returncode, output = cron(
        dict(os.environ, **env),
        sut,
        device_idx,
    )

    received_messages = files_chrono(messages_folder)
    usage_message = "usage" in output

    if situation == "BAD_CAMERA":
        assert not returncode  # doesn't know it didn't work
        assert len(received_messages)
        # TODO check for error message
    else:
        assert situation == "NON_CAMERA"
        assert returncode
        assert usage_message  # this is likely to change with refactoring
        assert not len(received_messages)
