import json
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


import email_encryptor


# I hope I figure out more about modules soon
# assert os.getcwd() == os.path.dirname(__file__)

from unit import starttls

conf_dir = os.environ["_SECURITY_CAMERA_CONFIG"]

with open(conf_dir + "/settings.json") as json_file:
    settings = json.load(json_file)

sender = settings["sender"]
recipients = settings["recipients"]

profile = email_encryptor.get_profile(conf_dir, sender, recipients)

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

    msg = email_encryptor.encrypt_message(
        profile, data, sender, recipients, subject
    )

    # putting the correct recipients argument in the following function call
    # is not verified by the tests because the test server does not give
    # us the recipients
    session.sendmail(sender, recipients, str(msg))
    print("%s sent" % filepath)

session.quit()
