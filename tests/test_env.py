import subprocess

import pytest

# def test(component_env, bin_dir):
#     assert bin_dir in component_env["PATH"]
#     # so...
#     result = subprocess.Popen(
#         ["which", "python"],
#         close_fds=False,
#         env=dict(os.environ, **component_env),
#         stderr=subprocess.STDOUT,
#         stdout=subprocess.PIPE,
#     ).communicate()
#     assert bin_dir in result[0].decode("UTF-8")


def env_pollution(env):
    return list(filter(lambda x: "SECURITY_CAMERA" in x, env.keys()))


def test_plain_env(plain_env, original_env):
    assert plain_env["GPIOZERO_PIN_FACTORY"] == "unset"
    assert len(env_pollution(original_env))
    assert not len(env_pollution(plain_env))


@pytest.mark.parametrize("app", ["fswebcam", "python"])
def test_original_env(plain_env, app):
    p = subprocess.Popen(
        [app, "--version"],
        env=plain_env,
        close_fds=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = p.communicate()[0].decode("UTF-8")
    assert p.returncode == 7, plain_env["PATH"]
    assert "preventing" in output, plain_env["PATH"]
    assert "system %s" % app in output, plain_env["PATH"]
