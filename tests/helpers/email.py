import time
import os


def wait_for_message(directory, expected, limit):
    start = time.time()
    while True:
        current = len(files_chrono(directory))
        assert current <= expected, "%s vs %s" % (current, expected)
        if current == expected:
            break
        assert time.time() - start < limit, "%s vs %s" % (current, expected)
        time.sleep(0.1)
    print("waited %s seconds for message #%s" % (time.time() - start, current))


def files_chrono(folder):
    # thanks https://stackoverflow.com/a/39327252
    files = os.listdir(folder)
    paths = []
    for basename in files:
        paths.append(folder + "/" + basename)
    return sorted(paths, key=os.path.getctime)
