import subprocess
import os

# this is a test


def assertEqual(a, b):
    assert a == b, "%s vs %s" % (a, b)


__dir__ = os.path.dirname(os.path.realpath(__file__))

sut = "%s/run.sh" % __dir__
mock = "%s/mock" % __dir__
server = "kevin@raspi"
scp_style = "%s:~/security-directory" % server
test_script = "echo this is a test"

# the fake scp method will return it like this:
expected_result = "%s+++%s" % (server, test_script)


def try_exe(args):
    p = subprocess.Popen(
        args,
        env=dict(os.environ, PATH="%s:%s" % (mock, os.environ["PATH"])),
        close_fds=False,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
    )

    assertEqual(p.communicate()[0].strip().decode("UTF-8"), expected_result)


# prove the fake ssh method gives us the answer
try_exe(["ssh", server, test_script])

# this works too if we don't take advantage of path
try_exe(["%s/ssh" % mock, server, test_script])

# prove that extra args passed to ssh will be ignored
# so our sut has to properly quote the command and send it
# as a single arg

try_exe(["ssh", server, test_script, "extra"])

# and now the main event

try_exe([sut, scp_style, test_script])
