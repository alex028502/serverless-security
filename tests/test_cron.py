import subprocess
import os
import sys

from .helpers.email import files_chrono

from .helpers.send import (
    message_from_file,
    assert_photo_message,
    asc_from_msg,
    msg_from_asc,
)


def cron(env, sut):
    p = subprocess.Popen(
        ["%s/cron.sh" % sut],
        env=env,
        close_fds=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = p.communicate()[0].decode("UTF-8")
    sys.stdout.write(output)  # like using tee!
    return p.returncode, output


# this just sets up the environment for batch.sh - it's pretty straightforward
# now since we removed the device arg and started sending all devices

# it needs to work with an empty list and enverything but most of that
# is covered in the batch tests - here we can just test the typical case
# and then make sure that encryption is doing what we expect and the
# wrapper handles our closes test simulation to the real environment
def test(main_env, email_server, email_config, sut, photos, demo_keys):
    (smtp_port, messages_folder) = email_server
    (config_dir, config) = email_config
    keys_dir, stranger_address = demo_keys

    returncode, output = cron(dict(os.environ, **main_env), sut)
    assert not returncode
    received_messages = files_chrono(messages_folder)

    assert len(received_messages) == len(photos)
    assert "usage" not in output

    for received_message_path, photo in zip(received_messages, photos):
        encrypted_msg = message_from_file(received_message_path)
        asc = asc_from_msg(encrypted_msg)
        decrypted_msg = msg_from_asc(
            asc,
            keys_dir,
            config["recipients"][0],
            config["sender"],
        )[0]
        assert_photo_message(photo, decrypted_msg)
        # assert not decrypted_msg.is_multipart()
        # assert decrypted_msg.get_content_type() == "image/jpeg"
        # assert decrypted_msg.get_filename() == picture_name
        # photocon = decrypted_msg.get_content()
        # assert not compare_content_to_path(photocon, photo)
        undecrypted_msg = msg_from_asc(
            asc,
            keys_dir,
            stranger_address,
            config["sender"],
        )[0]
        assert not undecrypted_msg
