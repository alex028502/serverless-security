from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import policy
from email.parser import Parser

import importlib.util

import pytest

from .helpers.send import (
    assert_format,
    assert_test_format,
    section_from_msg,
    compare_content_to_path,
    asc_from_msg,
    msg_from_asc,
)

parser = Parser(policy=policy.default)


# TODO combine all the copies of this
def import_by_path(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def assert_same_but_different(a, b):
    # to make sure they are the same but that we didn't accidentally just have
    # two references to the same object
    assert str(a) == str(b)
    assert a != b


# we did this check in the send package before
# but now we only test real encryption at the highest and lowest levels
# to keep the tests in the middle more readable
# these modes will help us compare mock and real encryptor modes side by side
@pytest.mark.parametrize("secure", [False, True])
@pytest.mark.parametrize("pic", list(range(2)))
def test(photos, tmp_path, demo_keys, sut, email_config, dirname, secure, pic):
    keys_dir = demo_keys[0]
    stranger_address = demo_keys[1]
    (config_dir, config) = email_config
    if secure:
        encryptor_path = "%s/encryptor.py" % sut
    else:
        encryptor_path = "%s/mock/encryptor.py" % dirname

    encryptor = import_by_path(encryptor_path, "encryptor")

    profile = encryptor.get_profile(
        config_dir, config["sender"], config["recipients"]
    )

    testsubject = "test message"

    sample_header_name = "x-encrypted-sample-header"
    if not pic:
        phrase = "welcome to serverless security"
        data = MIMEText(phrase)
        data[sample_header_name] = "sample-header"
    else:
        picture_name = "picture-name.jpg"
        with open(photos[0], mode="rb") as file:
            photocon = file.read()
            data = MIMEImage(photocon, name=picture_name)

    msg = encryptor.encrypt_message(
        profile,
        data,
        config["sender"],
        config["recipients"],
        "security update - %s" % testsubject,
    )

    if not pic:
        word = "welcome"
        assert word in phrase

    format_assertion_args = [
        msg,
        config["sender"],
        config["recipients"],
        testsubject,
    ]

    if not pic:
        if secure:
            assert_format(*format_assertion_args)
            assert word not in str(msg), "didn't encrypt?"
        else:
            assert_test_format(*format_assertion_args)
            assert word in str(msg)

    assert testsubject in str(msg), "control"

    if pic and secure:
        # can't remember why this only applies to photo messages
        # maybe we can change it later
        photo_xml = section_from_msg(".xml", msg)
        assert photo_xml is None, "shows what the helper does when not found"

    if secure:
        # from this point on, we can no longer pretend we don't know how many
        # recipients there are
        assert len(config["recipients"]) == 2
        recipientA, recipientB = config["recipients"]
        phrase_asc = asc_from_msg(msg)
        decrypted_msg = msg_from_asc(
            phrase_asc,
            keys_dir,
            recipientA,
            config["sender"],
        )[0]
        assert decrypted_msg
        assert_same_but_different(
            decrypted_msg,
            msg_from_asc(phrase_asc, keys_dir, recipientB, config["sender"])[0],
        )
    else:
        # the decryptor returns an email.message.Message
        # so we can convert it to that and get the same answers
        decrypted_msg = parser.parsestr(str(msg))
        # in tests where we send the message to an email server
        # this gets done no matter what

    if secure:
        unauthorized_msg, unauthorized_phrase_status = msg_from_asc(
            phrase_asc,
            keys_dir,
            stranger_address,
            config["sender"][0],
        )
        assert not unauthorized_msg, "does this mean encryption works?"
        assert unauthorized_phrase_status == 2

    if not pic:
        assert phrase in str(decrypted_msg)
        assert not decrypted_msg.is_multipart()
        assert decrypted_msg.get_content_type() == "text/plain"
        assert decrypted_msg.get_filename() is None
        decrypted_phrase_content = decrypted_msg.get_content()
        assert decrypted_phrase_content.strip() == phrase.strip()
    else:
        assert not decrypted_msg.is_multipart()
        assert decrypted_msg.get_content_type() == "image/jpeg"
        assert decrypted_msg.get_filename() == picture_name
        photocon = decrypted_msg.get_content()

        photo = photos[0]
        # let's compare with bash this time!
        # (to avoid copying what is in the implementation)
        assert not compare_content_to_path(photocon, photo)
        assert compare_content_to_path(b"wrong content", photo), "control"

    assert decrypted_msg.get(sample_header_name) == data[sample_header_name]
