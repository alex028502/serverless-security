import subprocess
import os

import pytest

from .helpers.photos import photo_relationship, photo_fake_size, real_convert
from .helpers.path import env_with_extended_path


# try the shrinker with fake and real imagemagick
# then confidently test most other features with fake imagemagick
@pytest.mark.parametrize("mode", ["REAL", "FAKE"])
def test(photos, tmp_path, sut, exe_path, mode, plain_env):
    photo_path = tmp_path / "photos"
    photo_path.mkdir()
    subprocess.run(["cp"] + photos + [str(photo_path)], check=True)
    new_names = []
    for photo in photos:
        new_names.append(str(photo_path) + "/" + os.path.basename(photo))
    if mode == "REAL":
        # the only thing from the environment that this tool uses is the
        # imagemagick program, so we can just use the plain environment
        # when we are not testing that
        env = plain_env
    else:
        assert mode == "FAKE"
        env = env_with_extended_path(plain_env, exe_path["convert"])

    # double check that the env above gets us the convert program we think
    assert real_convert(env) == (mode == "REAL"), env["PATH"]
    assert real_convert(env) == (mode != "FAKE")
    assert real_convert(env) != (mode == "FAKE")
    # etc.

    p = subprocess.Popen(
        ["%s/shrink.sh" % sut],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=False,
        env=env,
    )
    stdout, stderr = p.communicate(
        ("\n".join(new_names) + "\n").encode("UTF-8"),
    )
    assert not stderr
    assert not p.returncode
    generated_files = os.listdir(photo_path)
    assert len(generated_files) == 2 * len(photos)
    path_list = stdout.decode("UTF-8").strip()
    file_list = path_list.replace(str(photo_path) + "/", "").strip()
    assert sorted(generated_files) == sorted(file_list.split("\n"))
    paths = path_list.split("\n")
    pairs = zip(paths[: len(photos)], paths[len(photos) :])
    preview_size = "128x128"
    if mode == "REAL":
        expected_relationship = "different image"
        # in this mode it is hard to confirm that the images look the same
        # but we are checking the real size in this mode
    else:
        assert mode == "FAKE"
        expected_relationship = "different meta data"

    for pair in pairs:
        shrunken_image, full_image = pair
        assert photo_fake_size(shrunken_image) == preview_size, pair
        assert photo_fake_size(full_image) != preview_size, pair
        relationship = photo_relationship(full_image, shrunken_image)
        assert relationship == expected_relationship, pair


def test_helper(photos):
    assert photo_relationship(*photos[:2]) == "different image"
    assert photo_relationship(photos[0], photos[0]) == "same file"


BAD_TEST_ARGS = [
    ["TMP/filename.jpg", "-resize", "12x12"],
    ["TMP/filename.jpg", "-resize", "12x12", "TMP/filename.mini.jpg", "extra"],
    ["TMP/filename.jpg", "-resize"],
    ["TMP/filename.jpg", "12x12", "-resize", "TMP/filename.mini.jpg"],
]


@pytest.mark.parametrize("use_path", list(range(2)))
@pytest.mark.parametrize("args", BAD_TEST_ARGS)
def test_fake_convert_error(plain_env, args, tmp_path, exe_path, use_path):
    # the bad news is that if this function starts to accidentally write files
    # to disk to some path, during this test, we won't know... because we are
    # not testing that it does not write anything to disk - so be careful
    # actually let's still make it more likely that accidental files get
    # created in this directory:

    # also take the opportunity to confirm that we get the same result
    # whether we add it to the path or use the full exe
    if not use_path:
        env = plain_env
        exe = exe_path["convert"] + "/convert"
    else:
        env = env_with_extended_path(plain_env, exe_path["convert"])
        exe = "convert"

    assert not real_convert(env, exe)

    fixed_args = list(map(lambda x: x.replace("TMP", "%s" % tmp_path), args))
    p = subprocess.Popen(
        [exe] + fixed_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=False,
        env=env,
    )
    stdout, stderr = p.communicate()
    expected_output = " ".join(["unsupported", "configuration"] + fixed_args)
    assert stdout.decode("utf-8").strip() == ""
    assert stderr.decode("utf-8").strip() == expected_output
