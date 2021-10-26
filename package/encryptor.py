from base64 import b64encode

from autocrypt import message as autocrypt_message
from autocrypt import constants as autocrypt_constants

# https://github.com/juga0/pyac formats the email in a way that works with
# https://delta.chat - which is fantastic. I tried using delta.chat's rust
# library, but I was in over my head. The problem with autocrypt/pyac
# is that the version that worked isn't published to pypi. Pip can get the
# library straight from github, but pip freeze doesn't work, so I have had to
# create my own pip freeze wrapper (../tools/pip-freeze.sh). Also, it could
# disappear from github. I have cloend it just in case. What I would like to do
# is copy  this library into my project, and then use test coverage to delete
# everything unused and then inline the rest, and learn something about how it
# works. This way I could also remove the pip freeze wrapper


def getkey(conf_dir, address, kind):
    path = "%s/keys/%s/%s-key-1.asc" % (conf_dir, address, kind)
    with open(path, mode="rb") as file:
        return b64encode(file.read()).decode("ascii")


def get_profile(conf_dir, sender, recipients):
    profile = {
        autocrypt_constants.ACCOUNTS: {
            sender: {
                autocrypt_constants.PUBKEY: getkey(conf_dir, sender, "public"),
                autocrypt_constants.SECKEY: getkey(conf_dir, sender, "private"),
            },
        },
        autocrypt_constants.PEERS: {
            # fill this in right away
        },
    }

    for recipient in recipients:
        profile[autocrypt_constants.PEERS][recipient] = {
            autocrypt_constants.PUBKEY: getkey(conf_dir, recipient, "public"),
        }

    return profile


def encrypt_message(profile, data, sender, recipients, subject):
    cmsg = autocrypt_message.sign_encrypt(
        profile, data.as_bytes(), sender, recipients
    )

    msg = autocrypt_message.gen_encrypted_email(str(cmsg))
    autocrypt_message.add_headers(
        msg,
        sender,
        recipients,
        subject,
        None,
        False,
        None,
        {"Chat-Version": "1.0"},
    )
    keydata = autocrypt_message.get_own_public_keydata(profile, sender)
    autocrypt_message.add_ac_headers(msg, sender, keydata, None)
    return msg
