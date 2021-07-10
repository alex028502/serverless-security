import subprocess
import os
import sys

from .helpers.email import files_chrono


def cron(env, sut):
    p = subprocess.Popen(
        ["%s/cron.sh" % sut],
        env=env,
        close_fds=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = p.communicate()[0].decode("UTF-8")
    sys.stdout.write(output)  # like using tee!
    return p.returncode, output


# this just sets up the environment for batch.sh - it's pretty straightforward
# now since we removed the device arg and started sending all devices


def test(main_env, email_server, email_config, sut, photos):
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config

    returncode, output = cron(dict(os.environ, **main_env), sut)
    assert not returncode
    received_messages = files_chrono(messages_folder)

    assert len(received_messages) == len(photos)
    assert "usage" not in output
