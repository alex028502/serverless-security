import os
import subprocess
import time

import pytest

from .helpers.monitor import ctrl_key


@pytest.fixture()
def monitor_mkdir_process(component_env, sut, tmp_path):
    tmp_dirname = "%s/sample-directory" % tmp_path
    env = dict(os.environ, **component_env)
    command = ["mkdir", tmp_dirname]  # never put -p; should fail if exists
    p = subprocess.Popen(
        ["python", "-u", "%s/monitor.py" % sut] + command,
        # preexec_fn=os.setsid,
        env=env,
        close_fds=False,
        # stderr=sudprocess.PIPE, # do not test logging; just output for debug
    )
    time.sleep(1)
    yield p, tmp_dirname
    ctrl_key(p, "c")
    time.sleep(0.5)


def test(monitor_mkdir_process):
    p, tmp_dirname = monitor_mkdir_process
    assert not os.path.exists(tmp_dirname)
    ctrl_key(p, "\\")
    time.sleep(0.3)
    assert os.path.exists(tmp_dirname)
    ctrl_key(p, "\\")  # command fails but we don't know that
    time.sleep(0.3)
    assert os.path.exists(tmp_dirname)  # still there
    os.rmdir(tmp_dirname)
    assert not os.path.exists(tmp_dirname)
    ctrl_key(p, "\\")
    time.sleep(0.3)
    # make sure it is still working after the failure:
    assert os.path.exists(tmp_dirname)  # back again
