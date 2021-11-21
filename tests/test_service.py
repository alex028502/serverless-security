import subprocess
import time
import os

import pytest

from .helpers.email import files_chrono, wait_for_message
from .monitor.helpers import ctrl_key
from .helpers.send import (
    message_from_file,
    assert_format,
    asc_from_msg,
    msg_from_asc,
    compare_content_to_path,
)
from .helpers.photos import photo_relationship, photo_fake_size, real_convert


def start_service(env, *args):
    return subprocess.Popen(
        args,
        # preexec_fn=os.setsid,
        env=env,
        close_fds=False,
        stderr=subprocess.STDOUT,
    )


@pytest.fixture()
def service(email_server, main_env, sut):
    p = start_service(main_env, "%s/service.sh" % sut)
    time.sleep(1)
    yield p, email_server[1]
    ctrl_key(p, "c")
    time.sleep(1)


@pytest.fixture()
def alert(sut):
    with open("%s/alert.txt" % sut, "r") as alert_txt:
        return alert_txt.read().strip()


def test(service, demo_keys, main_env, photos, email_config, alert):
    config = email_config[1]
    batch_size = 2 * len(photos) + 1
    keys_dir, stranger_address = demo_keys
    p, messages_folder = service
    assert not len(files_chrono(messages_folder))
    picture_name = "security.jpg"
    assert "alert" in alert
    # every batch should have the same stuff in it
    # make sure it works three times - and each time check all the messages

    assert real_convert(main_env)

    for batch_key in range(0, 3):
        offset = len(files_chrono(messages_folder))
        assert offset == batch_key * batch_size
        ctrl_key(p, "\\")
        wait_for_message(messages_folder, offset + batch_size, 6)
        messages = files_chrono(messages_folder)
        print(messages)
        batch = messages[offset:]
        # we did it like this before:
        # batch = files_chrono(messages_folder)[-batch_size:]
        assert len(batch) == batch_size
        print("got", offset, batch, type(batch), len(batch))

        encrypted_msgs = map(message_from_file, batch)

        # try a different recipient each batch
        recipient = config["recipients"][batch_key % len(config["recipients"])]
        print("using recipient %s" % recipient)
        decrypted_msgs = []
        # check all the headers for this batch
        for encrypted_msg in encrypted_msgs:
            assert_format(
                encrypted_msg, config["sender"], config["recipients"], "motion"
            )
            asc = asc_from_msg(encrypted_msg)
            decrypted_msg, status = msg_from_asc(
                asc, keys_dir, recipient, config["sender"]
            )
            assert not status
            decrypted_msgs.append(decrypted_msg)

        # check the text message:
        assert alert in str(decrypted_msgs[0])
        assert not decrypted_msgs[0].is_multipart()
        assert decrypted_msgs[0].get_content_type() == "text/plain"
        assert decrypted_msgs[0].get_filename() is None
        assert decrypted_msgs[0].get_content().strip() == alert

        all_pictures_taken = files_chrono(
            main_env["SECURITY_CAMERA_HOME"] + "/data"
        )

        print(all_pictures_taken)

        full_pictures = []
        previews = []
        for pic in all_pictures_taken:
            if "preview" in os.path.basename(pic):
                previews.append(pic)
            else:
                full_pictures.append(pic)

        assert len(previews) == len(full_pictures)

        for photo_key in range(len(photos)):
            compressed_msg = decrypted_msgs[1 + photo_key]
            full_photo_msg = decrypted_msgs[1 + len(photos) + photo_key]
            for photo_msg in [compressed_msg, full_photo_msg]:
                assert not photo_msg.is_multipart()
                assert photo_msg.get_content_type() == "image/jpeg"
                assert photo_msg.get_filename() == picture_name
            compressed = compressed_msg.get_content()
            full_photo = full_photo_msg.get_content()
            assert not compare_content_to_path(full_photo, photos[photo_key])
            assert compare_content_to_path(compressed, photos[photo_key])
            # ok let's also prove that what you got in the email is what was
            # saved to disk - might be important for the preview image since
            # we can't test the content easily - so at least this might find
            # some of the possible issues
            # here is a gotcha - even though the previews get into the inbox
            # first, they are created after the full size images
            # actually here is another gotcha - the filename sorting
            # which it falls back on if the times are the same, which seems
            # to happen when they are created too fast, is different on
            # different computers, because it is what we get back from listing
            # the files, so now we just separate them
            outbox_idx = batch_key * len(photos) + photo_key
            preview_in_outbox = previews[outbox_idx]
            full_in_outbox = full_pictures[outbox_idx]
            assert "preview" in os.path.basename(preview_in_outbox)
            assert "preview" not in os.path.basename(full_in_outbox)
            # the above is obvious now that we sort them but
            assert os.path.basename(preview_in_outbox).replace(
                ".preview.jpg", ""
            ) == os.path.basename(full_in_outbox)
            assert not compare_content_to_path(compressed, preview_in_outbox)
            assert not compare_content_to_path(full_photo, full_in_outbox)

    # now let's just show how we have also saved all these pictures to disk
    # or maybe we should move this to the batch test - since it's not that
    # important for the end result
    number_of_batches = len(files_chrono(messages_folder)) / batch_size
    expected_pictures_taken = number_of_batches * (batch_size - 1)
    assert len(all_pictures_taken) == expected_pictures_taken
    # we are using these now instead:
    assert len(previews) + len(full_pictures) == expected_pictures_taken

    # actually - let's just check this now - why not!?
    preview_examples = zip(previews, photos * int(number_of_batches))
    full_examples = zip(full_pictures, photos * int(number_of_batches))
    for saved_pic, original in preview_examples:
        # use the fake size method to find out the real size
        # sorry about that
        assert photo_fake_size(saved_pic) == "128x128"
        # because we are using real convert we can't check that the
        # preview looks like it should without doing something more
        # sophisticated
        assert photo_relationship(saved_pic, original) == "different image"

    for saved_pic, original in full_examples:
        assert "x" in photo_fake_size(saved_pic)
        assert photo_fake_size(saved_pic) != "128x128"
        assert photo_relationship(saved_pic, original) == "identical files"

    for i in range(len(messages)):
        # finally let's try to open every message as an outsider
        # some stuff is repeated from the above tests
        encrypted_msg = message_from_file(messages[i])
        assert alert not in str(encrypted_msg)
        asc = asc_from_msg(encrypted_msg)
        decrypted_msg = msg_from_asc(
            asc,
            keys_dir,
            config["recipients"][0],
            config["sender"],
        )[0]
        if i % batch_size:
            assert decrypted_msg
            assert alert not in str(decrypted_msg)
            # cause this one is a photo
        else:
            assert alert in str(decrypted_msg)
        undecrypted_msg = msg_from_asc(
            asc,
            keys_dir,
            stranger_address,
            config["sender"],
        )[0]
        assert not undecrypted_msg
        # this doesn't really prove that it is encrypted but there are probably
        # ways that we could accidentally unencrypt the message that this would
        # warn us about
