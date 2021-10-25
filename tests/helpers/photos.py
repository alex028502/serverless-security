import subprocess

from PIL import Image


def photo_relationship(*path):
    if path[0] == path[1]:
        return "same file"

    try:
        subprocess.run(["diff"] + list(path), check=True)
        return "identical files"
    except subprocess.CalledProcessError:
        pass

    # thanks https://stackoverflow.com/a/23983459
    data = list(map(lambda x: list(Image.open(x).getdata()), path))

    if data[0] == data[1]:
        return "different meta data"

    return "different image"


def photo_fake_size(path):
    # the fake imagemagick exe copies and adds a comment field with the size
    # so this can verify the size
    # everybody says to use _getexif
    # but it return none, so using command line
    # program that I used to write the comment
    p = subprocess.Popen(
        ["exiftool", "-Comment", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = p.communicate()[0].decode("utf-8").split(":")[-1]
    if "size" in output:
        return output.replace("size", "").strip()

    return "x".join(map(str, Image.open(path).size))


def real_convert(env, exe="convert"):
    p = subprocess.Popen(
        [exe, "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        close_fds=False,
        env=env,
    )
    version_info = p.communicate()[0].decode("utf-8")
    return "ImageMagic" in version_info
