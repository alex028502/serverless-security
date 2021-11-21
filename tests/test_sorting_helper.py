import time
import os
import subprocess
from string import ascii_lowercase

import pytest

from .helpers.email import files_chrono

# not sure if file time sorting is working different on my raspberry pi 4
# where I am developing, and github actions


random_list = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
] + list(range(0, 19))

reversed_alphabet = list(reversed(ascii_lowercase))


@pytest.mark.parametrize("file_names", [reversed_alphabet, random_list])
def test(tmp_path, file_names):
    # thanks https://stackoverflow.com/a/17182670
    print("starttime %s" % time.time())
    for c in file_names:
        # the problem seems to be from create two files in the same nanosecond
        # which seems to not be possible on my desktop, but is possible on ci
        time.sleep(0.0001)  # do not delete based on test passing locally
        subprocess.run(
            ["touch", "%s/%s" % (tmp_path, c)],
            check=True,
        )

    # produce 26 filenames as quick as possible
    # all backwards so a lot of them have similar time stamps and prove
    # that we can sort them by timestamp even if we make one after the other
    print("endtime %s" % time.time())
    subprocess.run(
        ["ls", "--full-time", str(tmp_path)],
        check=True,
    )

    file_list = files_chrono(str(tmp_path))
    # debug a little more by showing the filetime python gets for each file
    for f in file_list:
        print("%s %s" % (f, os.path.getctime(f)))

    assert file_list == list(map(lambda x: "%s/%s" % (tmp_path, x), file_names))
