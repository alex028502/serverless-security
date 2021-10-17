import json
import sys
import re
import toml
import configparser
import os

# this script is combined with bash to produce lists of ignored files
# each argument produces a slightly different format and is combined with bash
# in a slightly different way, filtering a piped in find, or producing args
# for a find command


# format checks and coverage checks should only ignore files that
# are not in source control
# this script just takes all the filenames piped in, and outputs
# all the files that are ignored by any of the format or coverage checks
# so that we can make sure they are all git ignored too


def project_toml():
    return toml.load("pyproject.toml")


assert len(sys.argv) == 2, "bad arguments " + " ".join(sys.argv[1:])


def filter_exists(directories):
    # some stuff we are ignoring might not exist yet
    return filter(os.path.isdir, directories)


if sys.argv[1] == "flake8":
    flake8_config = configparser.ConfigParser()
    flake8_config.read(".flake8")
    flake8_ignore = filter_exists(
        map(
            str.strip,
            flake8_config["flake8"]["exclude"].strip().split(","),
        )
    )
    print(" ".join(map(str.strip, flake8_ignore)))
elif sys.argv[1] == "black":
    regex = re.compile(project_toml()["tool"]["black"]["extend-exclude"])
    for line in sys.stdin:
        if regex.match(line):
            print(line, end="")
elif sys.argv[1] == "nyc":
    with open(".nycrc.json", "r") as f:
        print(" ".join(filter_exists(json.loads(f.read())["exclude"])))
else:
    assert sys.argv[1] == "bash-coverage", "unknown arg %s" % sys.argv[1]
    with open("bashcov-ignore.json", "r") as bashcov_ignore_file:
        print(" ".join(filter_exists(json.loads(bashcov_ignore_file.read()))))
