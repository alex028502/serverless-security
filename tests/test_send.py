import time
import subprocess
import json

from .helpers.email import files_chrono
from .helpers.path import env_with_extended_path
from .helpers.send import (
    message_from_file,
    assert_test_format,
    section_from_msg,
    assert_photo_message,
    assert_text_message,
)

# This test is all done with non encrypted email
# encryption is tested at the top of the 'pyramid'


def test(email_server, photos, plain_env, sut, dirname, tmp_path, exe_path):
    (smtp_port, messages_folder) = email_server

    # all the other examples have two recipients because they have
    # to match what is in the encryption config
    # so here we can take advantage of no encryption and prove 3 will work
    config = {
        "sender": "camera.device@example.com",
        "recipients": [
            "edward@example.com",
            "andy@example.com",
            "simon@example.com",
        ],
        "headers": {
            "x-special": "user defined",
        },
        "smtp": {
            "address": "localhost",
            "port": smtp_port,
            "user": "",
            "password": "",
        },
    }

    tmp_config_dir = tmp_path / "config"
    tmp_config_dir.mkdir()

    with open("%s/settings.json" % tmp_config_dir, "w") as f:
        # who knew!? https://stackoverflow.com/a/12309296
        # I was using JSON.dumps and then putting it in a file!
        json.dump(config, f)

    phrase = "welcome to serverless security"
    photo = photos[0]

    lines = [phrase, photo]
    messages = "\n".join(lines) + "\n"
    env = dict(
        env_with_extended_path(plain_env, exe_path["python"]),
        _SECURITY_CAMERA_CONFIG=str(tmp_config_dir),
    )

    # you are not meant to use random stuff in tests but sometimes I do anyhow
    testsubject = "test" + str(int(time.time()) % 10)
    p = subprocess.Popen(
        [
            "python",
            "%s/send.py" % sut,
            "%s/mock/encryptor.py" % dirname,
            testsubject,
        ],
        # cwd=os.getcwd() + "/package",
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    p.communicate(input=messages.encode("UTF-8"))

    received_messages = files_chrono(messages_folder)
    assert len(received_messages) == len(lines)

    assert len(lines) == 2, "we actually know what number that is"

    for received_file_path in received_messages:
        assert config["sender"] in received_file_path
        # our fake mail server doesn't allow us to check the envelope recipient
        # the mailserver test above shows the envelope sender address is in
        # the filename

    # make a dictionary relating the input line to the correponding raw message
    results = dict(zip(lines, received_messages))

    # check the text message first
    phrase_msg = message_from_file(results[phrase])

    assert_test_format(
        phrase_msg,
        config["sender"],
        config["recipients"],
        testsubject,
    )

    # TODO: simplify this a bit more now that we are not encrypting
    assert phrase in str(phrase_msg)
    assert testsubject in str(phrase_msg)  # control
    decrypted_phrase_msg = phrase_msg
    # assert phrase_msg.get_content() == phrase
    # assert phrase_msg.content_type() ==
    assert_text_message(phrase, decrypted_phrase_msg)

    # now same only different for the photo
    photo_msg = message_from_file(results[photo])
    assert_test_format(
        photo_msg,
        config["sender"],
        config["recipients"],
        testsubject,
    )
    photo_xml = section_from_msg(".xml", photo_msg)
    assert photo_xml is None, "shows what the helper does when not found"
    # from this point on, we can no longer pretend we don't know how many
    # recipients there are
    decrypted_photo_msg = photo_msg  # TODO: unite these names
    assert decrypted_photo_msg

    assert_photo_message(photo, decrypted_photo_msg)
    for k, v in config["headers"].items():
        assert decrypted_photo_msg.get(k) == v

    # assert compare_content_to_path(b"wrong content", photo), "control"
