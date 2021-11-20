import subprocess
import time
import os

import pytest

from .helpers.email import files_chrono
from .helpers.path import env_with_extended_path


@pytest.fixture()
def action_env(plain_env, action_env_vars, exe_path):
    # let's prove that certain parts don't matter for this test
    return env_with_extended_path(
        dict(plain_env, **action_env_vars), exe_path["fswebcam"]
    )


def get_path(env):
    p = subprocess.run(
        "echo $PATH",
        env=env,
        shell=True,
        capture_output=True,
        check=True,
    )
    assert not p.stderr, p
    return p.stdout.decode("UTF-8")


def test_action_env(action_env):
    # we modifiy the path so we have to make sure
    # it works, and proves that the test coverage programs
    # don't undo our changes to the PATH
    env = dict(os.environ, **action_env)
    mock_path = "tests/mock"
    assert mock_path in action_env["PATH"]
    assert mock_path in get_path(env)
    p = subprocess.Popen(
        ["which", "fswebcam"],
        env=env,
        close_fds=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    which_output = p.communicate()
    assert not p.returncode, which_output
    assert not which_output[1], which_output
    assert mock_path + "/fswebcam/fswebcam" in which_output[0].decode("UTF-8")


def test_filename(tmp_path, sut):
    name = "test%s" % (int(time.time()) % 10)
    ext = "xx%s" % ((int(time.time()) % 2) + 1)  # 1 or 2 I think
    program = ["%s/filename.sh" % sut, str(tmp_path), name, ext]
    number_of_files = 100
    for i in range(number_of_files):
        assert i < number_of_files / 2, str(tmp_path)  # not using whole range
        p = subprocess.Popen(
            program,
            close_fds=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output = p.communicate()
        if p.returncode:
            assert p.returncode == 1
            assert output[0] == b""
            assert b"no filenames left" in output[1]
            break
        assert output[1] == b"", "iteration %s" % i
        assert not p.returncode, output
        filename = output[0].strip()
        assert not os.path.isfile(filename), "iteration %s" % i
        subprocess.run(["touch", filename], check=True)
        assert os.path.isfile(filename), "iteration %s" % i

    files = files_chrono(str(tmp_path))
    assert len(files) > 8  # we are going to need up to 8 filenames per second
    assert "0000" in files[0]  # not really a requirement
    for filename in files:
        assert ext in filename
        assert name in filename


exe_paths = ["./tests/mock/fswebcam/fswebcam", "fswebcam"]


@pytest.mark.parametrize("exe", exe_paths)
def test_camera(photos, action_env, exe):
    # take advantage of action_env
    # creates a directory for us and tells us the PATH
    datadir = action_env["_SECURITY_CAMERA_DATA"]
    new_image = datadir + "/test.jpg"
    env = dict(os.environ, PATH=action_env["PATH"])
    p = subprocess.Popen(
        [exe, "--device", photos[0], new_image],
        env=env,
        close_fds=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = p.communicate()
    assert not p.returncode, output
    assert output[0], output
    assert_same_content(photos[0], new_image)
    assert not output[1], output


bad_args = [
    (["a", "b", "c"], False),
    (["--device", "b"], False),
    (["--device", "a", "c", "d"], False),
    (["--device", "azxcxc", "/tmp/c/asf"], True),
    (["--device", __file__, "/tmp/c/asf"], True),
]


@pytest.mark.parametrize("args", bad_args)
def test_camera_args(photos, action_env, args):
    arg_list, should_try_cp = args
    env = dict(os.environ, PATH=action_env["PATH"])
    p = subprocess.Popen(
        ["fswebcam"] + arg_list,
        env=env,
        close_fds=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = p.communicate()
    assert p.returncode, output
    assert output[0], output
    cp_phrase = "cp: cannot".encode("UTF-8")
    assert output[1], output
    if should_try_cp:
        assert cp_phrase in output[1]
    else:
        assert cp_phrase not in output[1]
    if len(arg_list) > 2:
        assert not os.path.isfile(arg_list[2])


def test(photos, action_env, sut):
    # now make sure the script that takes pictures works
    devices = " ".join(photos)  # the mock exe passes the photos right through
    env = dict(os.environ, **action_env, SECURITY_CAMERA_DEVS=devices)
    datadir = env["_SECURITY_CAMERA_DATA"]
    assert os.path.isdir(datadir)
    p = subprocess.Popen(
        ["%s/action.sh" % sut],
        env=env,
        close_fds=False,
        stdout=subprocess.PIPE,
    )
    output = p.communicate()[0].decode("utf-8")
    assert not p.returncode
    generated_files = files_chrono(datadir)
    assert len(generated_files) == len(photos)
    # full paths in the output:
    assert "\n".join(generated_files) + "\n" == output
    output_photos = output.strip().split("\n")
    assert len(output_photos) == len(photos)
    for copy_of_file, original_file in zip(output_photos, photos):
        assert_same_content(copy_of_file, original_file)


def test_env_issue(photos, action_env, sut):
    devices = " ".join(photos)  # the mock exe passes the photos right through
    env = dict(os.environ, **action_env, SECURITY_CAMERA_DEVS=devices)
    variable_to_unset = "_SECURITY_CAMERA_DATA"
    env_mod = {
        variable_to_unset: "",
    }
    p = subprocess.Popen(
        ["%s/action.sh" % sut],
        env=dict(env, **env_mod),
        close_fds=False,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    output = p.communicate()
    assert p.returncode
    assert not output[0]  # because we should only output if there are pics
    message = "must provide %s" % variable_to_unset
    assert message in output[1].decode("utf-8")


def assert_same_content(*args):
    # a compare two files python helper function might be better than
    # using bash all the time
    subprocess.run(["diff"] + list(args), check=True)
