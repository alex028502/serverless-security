import subprocess
import os


def test(photos, tmp_path, sut):
    subprocess.run(["cp"] + photos + [str(tmp_path)], check=True)
    new_names = []
    for photo in photos:
        new_names.append(str(tmp_path) + "/" + os.path.basename(photo))

    p = subprocess.Popen(
        ["%s/shrink.sh" % sut],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=False,
    )
    stdout, stderr = p.communicate(
        ("\n".join(new_names) + "\n").encode("UTF-8"),
    )
    assert not stderr
    assert not p.returncode
    generated_files = os.listdir(tmp_path)
    assert len(generated_files) == 2 * len(photos)
    file_list = stdout.decode("UTF-8").replace(str(tmp_path) + "/", "").strip()
    assert sorted(generated_files) == sorted(file_list.split("\n"))
