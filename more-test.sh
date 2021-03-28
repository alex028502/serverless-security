#! /usr/bin/env bash

set -e

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

./be-quiet.sh

./sysreq.sh
./check-install.sh


