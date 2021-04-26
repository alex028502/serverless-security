import subprocess
import os
import sys

import pytest

from .helpers.email import files_chrono

MOTION = "motion"
HEARTBEAT = "heartbeat"
MODES = [HEARTBEAT, MOTION]


@pytest.fixture()
def env(component_env):
    new_env = dict(os.environ, **component_env)
    new_env.pop("GPIOZERO_PIN_FACTORY")
    return new_env


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


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("device_count", [1, 2, 0])
def test_happy(
    env,
    email_server,
    email_config,
    photos,
    device_count,
    mode,
    sut,
    bad_device,
):
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config
    # there will always be bad devices in the list since in practice we just
    # pass in /dev/video* and they are not all cameras
    # even some cameras have two devices on the list and only one works for this
    # so we might as well just always test with at least one bad device
    devices = " ".join([bad_device] + photos[:device_count])
    returncode, output = batch(
        dict(os.environ, SECURITY_CAMERA_DEVS=devices, **env),
        [mode],
        sut,
    )
    assert not returncode
    received_messages = files_chrono(messages_folder)

    if mode == MOTION:
        expected_number_of_messages = device_count * 2 + 1
    else:
        assert mode == HEARTBEAT
        expected_number_of_messages = device_count

    # even when 0 messages are expected we get one message because
    # if there are not cameras connected, we get a technical difficulty message
    assert len(received_messages) == max(expected_number_of_messages, 1)
    assert "usage" not in output


@pytest.mark.parametrize("situation", ["no args", "bad mode"])
def test_unhappy(env, email_server, email_config, photos, situation, sut):
    if situation == "no args":
        args = []
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
