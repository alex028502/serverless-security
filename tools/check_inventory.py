import os
import sys
import subprocess
import json
from unittest import TestCase

target_dir = os.path.abspath(sys.argv[1])

# test inventory program and make sure the target directory matches what is in
# the makefile


def json_from_command(command, **env):
    p = subprocess.Popen(
        command,
        env=dict(os.environ, **env),
        stdout=subprocess.PIPE,
        close_fds=False,
    )
    output = p.communicate()[0].decode("UTF-8")
    assert not p.returncode, output
    return json.loads(output)


def try_inventory_file(sut, **env):
    inventory_list = json_from_command([sut, "--list"], **env)
    inventory_details = json_from_command([sut, "--host"], **env)
    return inventory_list, inventory_details


test_list, test_details = try_inventory_file("./inventory/testarea.sh")

# good enough to tell me if something has changed:
TestCase().assertEqual(test_list["default"][0], "test")
TestCase().assertEqual(
    os.path.abspath(test_details["security_camera_home"]), target_dir
)

prod_host = "example.com"
prod_home = "/home/username/appdir"

prod_list, prod_details = try_inventory_file(
    "./inventory/prodarea.sh",
    SECURITY_LIVE_TARGET="%s:%s" % (prod_host, prod_home),
)

TestCase().assertEqual(prod_list["prod"][0], prod_host)
TestCase().assertEqual(
    os.path.abspath(prod_details["security_camera_home"]), prod_home
)

no_prod_list, no_prod_details = try_inventory_file(
    "./inventory/prodarea.sh",
    SECURITY_LIVE_TARGET="",
)

TestCase().assertEqual(no_prod_list, {})
TestCase().assertEqual(no_prod_details, {})
