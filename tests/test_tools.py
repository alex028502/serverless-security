import subprocess
import os

import pytest


def test_addresses(email_config, component_env):
    directory, data = email_config
    settings_file_path = directory + "/settings.json"
    p = subprocess.Popen(
        ["python", "tools/addresses.py", settings_file_path],
        stdout=subprocess.PIPE,
        env=dict(os.environ, **component_env),
    )
    names_from_tool = p.communicate()[0].decode("utf-8").strip().split("\n")
    names_from_fixture = [data["sender"]] + data["recipients"]
    assert not p.returncode
    assert sorted(names_from_tool) == sorted(names_from_fixture)


@pytest.mark.parametrize("failure", [True, False])
def test_new_account(tmp_path, failure):
    email = "luke@example.com"
    directory = str(tmp_path) + "/" + email
    private_filename = "private.asc"
    public_filename = "public.asc"

    if failure:
        # cause failure by creating directory
        os.mkdir(directory)

    p = subprocess.run(
        [
            "node",
            "tools/new-account.js",
            directory,
            email,
            private_filename,
            public_filename,
        ]
    )
    assert bool(p.returncode) == failure
    assert not os.path.isfile(directory + "/" + private_filename) == failure
    assert not os.path.isfile(directory + "/" + public_filename) == failure
