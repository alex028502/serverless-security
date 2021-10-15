import subprocess

from email import policy
from email.parser import Parser
from email.message import EmailMessage

parser = Parser(policy=policy.default)


def message_from_file(msg_path):
    with open(msg_path, "r") as msg_file:
        msg = msg_file.read()
    return parser.parsestr(msg)


def assert_test_format(parsed_email, sender, recipients, subject):
    assert parsed_email["To"] == ", ".join(recipients), (
        "looking for %s" % parsed_email["To"]
    )
    assert parsed_email["From"] == sender, parsed_email["From"] == sender
    # we send an unencrypted subject so that we see it in the notification
    assert (
        parsed_email["Subject"] == "security update - %s" % subject
    ), parsed_email["Subject"]
    assert parsed_email["Chat-Version"] == "1.0", "for delta.chat"


def assert_format(parsed_email, *args):
    assert_test_format(parsed_email, *args)
    assert parsed_email.is_multipart()
    assert parsed_email.get_content_subtype() == "encrypted"


def asc_from_msg(msg):
    # TODO: find out what the other parts do and test them maybe
    return section_from_msg(".asc", msg)


def section_from_msg(filename_fragment, msg):
    for part in msg.walk():
        if filename_fragment in str(part.get_filename()):
            return part.get_payload()
    return None


def msg_from_asc(asc, keys_dir, recipient, sender):
    public_key_file = "%s/%s/public-key-1.asc" % (keys_dir, sender)
    private_key_file = "%s/%s/private-key-1.asc" % (keys_dir, recipient)
    p = subprocess.Popen(
        ["node", "tools/decrypt.js", public_key_file, private_key_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    result = p.communicate(asc.encode("UTF-8"))
    return (parser.parsestr(result[0].decode("UTF-8")), p.returncode)


def compare_content_to_path(content, path):
    # let's compare with bash this time!
    # (to avoid copying what is in the implementation)
    p = subprocess.Popen(["diff", "-", path], stdin=subprocess.PIPE)
    p.communicate(content)
    return p.returncode


def assert_text_message(phrase, decrypted_phrase_msg):
    assert type(decrypted_phrase_msg) == EmailMessage
    assert phrase in str(decrypted_phrase_msg)
    assert not decrypted_phrase_msg.is_multipart()
    assert decrypted_phrase_msg.get_content_type() == "text/plain"
    assert decrypted_phrase_msg.get_filename() is None
    decrypted_phrase_content = decrypted_phrase_msg.get_content()
    assert decrypted_phrase_content.strip() == phrase.strip()


def assert_photo_message(photo, decrypted_photo_msg):
    assert type(decrypted_photo_msg) == EmailMessage
    assert not decrypted_photo_msg.is_multipart()
    assert decrypted_photo_msg.get_content_type() == "image/jpeg"
    assert decrypted_photo_msg.get_filename() == "security.jpg"
    photocon = decrypted_photo_msg.get_content()
    if photo:
        assert not compare_content_to_path(photocon, photo)
    else:
        # if these are similar but different and we have to do a more
        # complicated comparison so just return the message content that has
        # been extracted above
        return photocon
