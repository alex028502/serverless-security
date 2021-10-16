# from .helpers.send import
import os
import time
import subprocess

from .helpers.email import files_chrono
from .helpers.send import (
    message_from_file,
    assert_format,
    asc_from_msg,
    section_from_msg,
    msg_from_asc,
    compare_content_to_path,
)


def assert_same_but_different(a, b):
    # to make sure they are the same but that we didn't accidentally just have
    # two references to the same object
    assert str(a) == str(b)
    assert a != b


def test(email_server, email_config, demo_keys, photos, component_env, sut):
    keys_dir = demo_keys[0]
    stranger_address = demo_keys[1]
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config

    assert smtp_port == config["smtp"]["port"], "just making sure"

    phrase = "welcome to serverless security"
    photo = photos[0]

    lines = [phrase, photo]
    messages = "\n".join(lines) + "\n"
    env = dict(os.environ, **component_env)

    # you are not meant to use random stuff in tests but sometimes I do anyhow
    testsubject = "test" + str(int(time.time()) % 10)
    p = subprocess.Popen(
        ["python", "%s/send.py" % sut, testsubject],
        env=env,
        # cwd=os.getcwd() + "/package",
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
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

    assert_format(
        phrase_msg,
        config["sender"],
        config["recipients"],
        testsubject,
    )

    word = "welcome"
    assert word in phrase
    assert word not in str(phrase_msg), "didn't encrypt?"
    assert testsubject in str(phrase_msg), "control"

    phrase_asc = asc_from_msg(phrase_msg)
    # from this point on, we can no longer pretend we don't know how many
    # recipients there are
    assert len(config["recipients"]) == 2
    recipientA, recipientB = config["recipients"]
    decrypted_phrase_msg = msg_from_asc(
        phrase_asc,
        keys_dir,
        recipientA,
        config["sender"],
    )[0]
    assert decrypted_phrase_msg
    assert_same_but_different(
        decrypted_phrase_msg,
        msg_from_asc(phrase_asc, keys_dir, recipientB, config["sender"])[0],
    )

    unauthorized_phrase_msg, unauthorized_phrase_status = msg_from_asc(
        phrase_asc,
        keys_dir,
        stranger_address,
        config["sender"][0],
    )
    assert not unauthorized_phrase_msg, "does this mean encryption works?"
    assert unauthorized_phrase_status == 2

    assert phrase in str(decrypted_phrase_msg)
    assert not decrypted_phrase_msg.is_multipart()
    assert decrypted_phrase_msg.get_content_type() == "text/plain"
    assert decrypted_phrase_msg.get_filename() is None
    decrypted_phrase_content = decrypted_phrase_msg.get_content()
    assert decrypted_phrase_content.strip() == phrase.strip()

    # now same only different for the photo
    photo_msg = message_from_file(results[photo])
    assert_format(
        photo_msg,
        config["sender"],
        config["recipients"],
        testsubject,
    )
    photo_asc = asc_from_msg(photo_msg)
    photo_xml = section_from_msg(".xml", photo_msg)
    assert photo_xml is None, "shows what the helper does when not found"
    # from this point on, we can no longer pretend we don't know how many
    # recipients there are
    decrypted_photo_msg = msg_from_asc(
        photo_asc, keys_dir, recipientA, config["sender"]
    )[0]
    assert decrypted_photo_msg
    assert_same_but_different(
        decrypted_photo_msg,
        msg_from_asc(photo_asc, keys_dir, recipientB, config["sender"])[0],
    )

    unauthorized_photo_msg, unauthorized_photo_status = msg_from_asc(
        photo_asc,
        keys_dir,
        stranger_address,
        config["sender"],
    )
    assert not unauthorized_photo_msg
    assert unauthorized_photo_status == 2

    assert not decrypted_photo_msg.is_multipart()
    assert decrypted_photo_msg.get_content_type() == "image/jpeg"
    assert decrypted_photo_msg.get_filename() == "security.jpg"
    for k, v in config["headers"].items():
        assert decrypted_photo_msg.get(k) == v

    photocon = decrypted_photo_msg.get_content()

    # let's compare with bash this time!
    # (to avoid copying what is in the implementation)
    assert not compare_content_to_path(photocon, photo)
    assert compare_content_to_path(b"wrong content", photo), "control"
