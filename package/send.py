import json
import os
import sys
from base64 import b64encode
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from autocrypt import message
from autocrypt import constants

# I hope I figure out more about modules soon
# assert os.getcwd() == os.path.dirname(__file__)

from unit import starttls

conf_dir = os.environ["_SECURITY_CAMERA_CONFIG"]

with open(conf_dir + "/settings.json") as json_file:
    settings = json.load(json_file)

sender = settings["sender"]
recipients = settings["recipients"]


def getkey(address, kind):
    path = "%s/keys/%s/%s-key-1.asc" % (conf_dir, address, kind)
    with open(path, mode="rb") as file:
        return b64encode(file.read()).decode("ascii")


profile = {
    constants.ACCOUNTS: {
        sender: {
            constants.PUBKEY: getkey(sender, "public"),
            constants.SECKEY: getkey(sender, "private"),
        },
    },
    constants.PEERS: {
        # fill this in right away
    },
}

for recipient in recipients:
    profile[constants.PEERS][recipient] = {
        constants.PUBKEY: getkey(recipient, "public"),
    }


session = smtplib.SMTP(
    settings["smtp"]["address"],
    settings["smtp"]["port"],
)

label = sys.argv[1]

print("sending batch as %s" % label)

subject = "security update - %s" % label

# now open the email session and start snapping and sending
starttls(session, settings["smtp"]["user"], settings["smtp"]["password"])

# keeping the session open doesn't seem to make things any faster
# it just takes a long time to encrypt and send these photos on this
# little device


def get_input():
    got_input = False
    for line in sys.stdin:
        if line.strip():
            got_input = True
            yield line
    if not got_input:
        yield "technical difficulties\n"


for line in get_input():
    filepath = line.strip()
    print("sending %s topic %s" % (filepath, label))
    try:
        with open(filepath, mode="rb") as file:
            photocon = file.read()
            data = MIMEImage(photocon, name="security.jpg")
    except FileNotFoundError:
        # the filepath is the message
        # and if it is a mistake, we will get the filepath
        # that does not exist for debugging
        data = MIMEText(filepath)

    # putting the correct recipients argument in the following function call
    # is not verified by the tests because the test server does not give
    # us the recipients
    cmsg = message.sign_encrypt(profile, data.as_bytes(), sender, recipients)

    msg = message.gen_encrypted_email(str(cmsg))
    message.add_headers(
        msg,
        sender,
        recipients,
        subject,
        None,
        False,
        None,
        {"Chat-Version": "1.0"},
    )
    keydata = message.get_own_public_keydata(profile, sender)
    message.add_ac_headers(msg, sender, keydata, None)
    session.sendmail(sender, recipients, str(msg))
    print("%s sent" % filepath)

session.quit()
