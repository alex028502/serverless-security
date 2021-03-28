import time
import os


def wait_for_message(directory, number, limit):
    start = time.time()
    while len(files_chrono(directory)) != number:
        assert time.time() - start < limit, len(files_chrono(directory))
        time.sleep(0.1)
    print("waited %s seconds for message #%s" % (time.time() - start, number))


def files_chrono(folder):
    # thanks https://stackoverflow.com/a/39327252
    files = os.listdir(folder)
    paths = []
    for basename in files:
        paths.append(folder + "/" + basename)
    return sorted(paths, key=os.path.getctime)
