import subprocess
import os
import sys

import pytest

from .helpers.email import files_chrono

MOTION = "motion"
HEARTBEAT = "heartbeat"
MODES = [MOTION, HEARTBEAT]


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
@pytest.mark.parametrize("device_count", [1, 2])
def test_happy(
    env, email_server, email_config, photos, device_count, mode, sut
):
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config
    returncode, output = batch(
        dict(os.environ, **env),
        [mode] + photos[:device_count],
        sut,
    )
    assert not returncode
    received_messages = files_chrono(messages_folder)

    if mode == MOTION:
        expected_number_of_messages = device_count * 2 * 2 + 1
    else:
        assert mode == HEARTBEAT
        expected_number_of_messages = device_count

    assert len(received_messages) == expected_number_of_messages
    assert "usage" not in output


@pytest.mark.parametrize("situation", ["no args", "bad mode", "no device"])
def test_unhappy(env, email_server, email_config, photos, situation, sut):
    if situation == "no args":
        args = []
    elif situation == "bad mode":
        args = ["hello"] + photos
    else:
        assert situation == "no device"
        args = [MOTION]

    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config
    returncode, output = batch(
        dict(os.environ, **env),
        args,
        sut,
    )
    assert returncode
    received_messages = files_chrono(messages_folder)
    assert len(received_messages) == 0
    assert "usage" in output


@pytest.mark.parametrize("mode", MODES)
def test_broken_camera(env, email_server, email_config, bad_device, mode, sut):
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config
    returncode, output = batch(dict(os.environ, **env), [mode, bad_device], sut)
    assert not returncode
    received_messages = files_chrono(messages_folder)
    # YOU SHOULD STILL GET THE TEXT MESSAGE
    # in motion mode it's the initial alert and in heartbeat mode it's the
    # technical difficulaties error messages when send.py has nothing to send
    assert len(received_messages) == 1
    assert "usage" not in output
    # I DON'T KNOW THE BEST PLACE TO MAKE SURE THESE ARE CORRECT
    # MAYBE A FEW EXAMPLES IN THE END TO END TESTS


def test_mix(env, email_server, email_config, photos, bad_device, sut):
    # mix of working and broken cameras
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config
    assert not os.path.isfile(bad_device)
    returncode, output = batch(
        dict(os.environ, **env), [MOTION] + [bad_device, photos[0]], sut
    )
    assert not returncode
    received_messages = files_chrono(messages_folder)
    assert len(received_messages) == 5
    assert "usage" not in output
