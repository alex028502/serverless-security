#! /usr/bin/env bash

set -e

# this script does multipe things:
# - check that global requirements are all here
# - check that local installation has been done correctly
# (but really it is just checking the coverage for thos scripts since they
# are run before and right after installation)
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

# now run each of the tools successfully
# this is done earlier as well, but here we do it when we can check coverage

./sysreq.sh

echo the above script uses the stuff we tested in this file:
grep $sysreq ./sysreq.sh
grep $remove_comments ./sysreq.sh

./check-install.sh
