import os
import subprocess


def test(component_env, bin_dir):
    assert bin_dir in component_env["PATH"]
    # so...
    result = subprocess.Popen(
        ["which", "python"],
        close_fds=False,
        env=dict(os.environ, **component_env),
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
    ).communicate()
    assert bin_dir in result[0].decode("UTF-8")
