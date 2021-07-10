import subprocess
import os

import pytest


@pytest.mark.parametrize("case", ["forwards", "backwards"])
def test(component_env, sut, photos, bad_device, case):
    # let's test it in different orders to make sure that our set comparison
    # works and so that we always test with a good image last once and make
    # sure that the temp file is cleaned up properly
    all_devices = [bad_device] + photos
    if case == "backwards":
        all_devices.reverse()
        assert all_devices[0] != bad_device
    else:
        assert case == "forwards"
        assert all_devices[0] == bad_device

    env = dict(component_env, SECURITY_CAMERA_DEVS=" ".join(all_devices))
    assert set(photos) != set(all_devices)  # control
    p = subprocess.Popen(
        ["%s/discover.sh" % sut],
        env=env,
        close_fds=False,
        stdout=subprocess.PIPE,
    )
    good_devices = filter(
        lambda x: x,
        p.communicate()[0].decode("UTF-8").replace("\n", " ").split(" "),
    )
    assert p.returncode == 0
    assert set(photos) == set(good_devices)
    # and just make sure it cleans up after itself most of the time
    assert os.listdir(path=env["_SECURITY_CAMERA_DATA"]) == []
