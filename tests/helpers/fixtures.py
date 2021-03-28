import os


# helper to create a fake path with the same directory and extension as a path
# you pass in
def made_up_path(real_path, made_up_name):
    directory = os.path.dirname(real_path)
    good_filename = os.path.basename(real_path)
    pieces = good_filename.split(".")
    if len(pieces) - 1:
        new_name = "%s.%s" % (made_up_name, pieces[-1])
    else:
        new_name = made_up_name
    return "%s/%s" % (directory, new_name)
