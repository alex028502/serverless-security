#! /usr/bin/env bash

set -e

# this script does multipe things:
# - check that global requirements are all here
# - check that local installation has been done correctly
# (but really it is just checking the coverage for thos scripts since they
# are run before and right after installation)
# - check that the tools for checking installation fail when they should

# I would have preferred to write these tests with make but it confuses bashcov
# when this fails, it is going to be hard to find the failure - and we can't
# use -x with bashcov either

sysrq=tools/sysrq.sh
remove_comments=tools/remove-comments.sh

ls $sysrq > /dev/null
ls $remove_comments > /dev/null
./tools/expect-failure.sh $remove_comments
./tools/expect-failure.sh $sysrq
./tools/expect-failure.sh $sysrq program-does-not-exist
./tools/expect-failure.sh $sysrq program-does not-exist

# now run each of the tools successfully
# this is done earlier as well, but here we do it when we can check coverage

./sysrq.sh

echo the above script uses the stuff we tested in this file:
grep $sysrq ./sysrq.sh
grep $remove_comments ./sysrq.sh

./check-install.sh
