#! /usr/bin/env bash

set -e

# this script does multipe things:
# - check that global requirements are all here
# - check that local installation has been done correctly
# - check that the tools for checking installation fail when they should
# - check that failure check works as it should

# I would have preferred to write these tests with make but it confuses bashcov
# when this fails, it is going to be hard to find the failure - and we can't
# use -x with bashcov either

sysreq=tools/sysreq.sh
remove_comments=tools/remove-comments.sh

ls $sysreq > /dev/null
ls $remove_comments > /dev/null
./tools/expect-failure.sh $remove_comments
./tools/expect-failure.sh $sysreq
./tools/expect-failure.sh $sysreq program-does-not-exist
./tools/expect-failure.sh $sysreq program-does not-exist
# check this out
./tools/expect-failure.sh ./tools/expect-failure.sh echo ok

set -o pipefail

$remove_comments sysreq.txt | xargs -n1 $sysreq

# make sure that our requirements file matches what we have installed
# if this fails maybe delete venv and try again
# I think it might happen if dependencies get removed
./venv-run.sh venv ./pip-freeze.sh | diff - requirements.txt
