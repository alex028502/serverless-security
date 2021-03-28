import subprocess
import uuid
import os

import pytest

from .helpers.email import wait_for_message, files_chrono
from .helpers.fixtures import made_up_path


def simple_message(*args):
    subprocess.run(["python", "tools/mail.py"] + list(args), check=True)


@pytest.mark.parametrize("split", [False, True])
def test_email_server(email_server, split):
    (smtp_port, messages_folder) = email_server
    sender = "sender@example.com"
    message = "hello world %s" % uuid.uuid4()
    # check this out! we can pass it in as a single are or multiple!
    if split:
        message_args = message.split(" ")
    else:
        message_args = [message]
    simple_message("localhost", str(smtp_port), sender, *message_args)
    wait_for_message(messages_folder, 1, 3)
    received_messages = files_chrono(messages_folder)
    assert len(received_messages) == 1
    email_path = received_messages[0]
    assert sender in email_path
    with open(email_path) as f:
        email_content = f.read()
    assert message.strip() == email_content


def test_photos(photos):
    photo0, photo1 = photos
    assert os.path.isfile(photo0)
    assert os.path.isfile(photo1)


# we don't use the no extension option but we are putting it in and testing it
# for no reason - including it here instead of in the helpers tests
def test_made_up_path():
    assert made_up_path("test/hello.jpg", "bye") == "test/bye.jpg"
    assert made_up_path("test/hello", "bye") == "test/bye"
    # only use the final extension - the rest art just dots in the name:
    assert made_up_path("test/hello.2.jpg", "bye") == "test/bye.jpg"


def test_bad_device(bad_device, photos):
    assert not os.path.isfile(bad_device)
    # let's just make sure everything is making sense here:
    assert os.path.isfile(photos[0])
    assert os.path.isfile(photos[1])


def test_email_info(email_config, demo_keys):
    # if this fails, you might just have to rerun the installation
    demo_keys_dir = demo_keys[0]
    strangers = demo_keys[1:]
    email_config_dir, email_config_info = email_config
    accounts = email_config_info["recipients"] + [email_config_info["sender"]]
    assert len(strangers)
    assert len(accounts)
    assert sorted(strangers + accounts) == sorted(os.listdir(demo_keys_dir))
    assert sorted(accounts) == sorted(os.listdir(email_config_dir + "/keys"))


@pytest.mark.parametrize("case", ["stranger", "sender", "recipient"])
def test_email_config(email_config, demo_keys, case):
    email_config_dir, email_config_info = email_config
    pub_fname = "public-key-1.asc"
    priv_fname = "private-key-1.asc"
    public_only = [pub_fname]
    both = [priv_fname] + public_only
    all_keys_dir = demo_keys[0]
    user_keys_dir = email_config_dir + "/keys"

    # check for correct files in first of each group
    cases = {
        "recipient": {
            "address": email_config_info["recipients"][0],
            "configured": public_only,
        },
        "sender": {
            "address": email_config_info["sender"],
            "configured": both,
        },
        "stranger": {
            "address": demo_keys[1],
            "configured": None,
        },
    }

    test_keys_path = all_keys_dir + "/" + cases[case]["address"]
    assert sorted(os.listdir(test_keys_path)) == both

    app_keys_path = user_keys_dir + "/" + cases[case]["address"]
    assert os.path.isdir(app_keys_path) == bool(cases[case]["configured"])

    assert not same(
        test_keys_path + "/" + priv_fname, test_keys_path + "/" + pub_fname
    )

    if cases[case]["configured"]:
        assert sorted(os.listdir(app_keys_path)) == cases[case]["configured"]

        if len(cases[case]["configured"]) > 1:
            assert same(app_keys_path, test_keys_path)
        # might as well check this again for the one with the private key:
        assert same(
            app_keys_path + "/" + pub_fname,
            test_keys_path + "/" + pub_fname,
        )

    # if we had passed in the wrong files, we would have gotten an exception:
    with pytest.raises(Exception):
        same(
            app_keys_path + "/" + pub_fname,
            test_keys_path + "/" + "adlf" + pub_fname,
        )


def same(*args):
    p = subprocess.run(["diff"] + list(args))
    assert p.returncode in [0, 1]
    return not p.returncode
