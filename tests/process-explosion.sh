#! /usr/bin/env bash

set -e

dir=$(dirname $0)

# creates three levels of processes all running in the foreground to test out
# the ctrl+c helper in our tests - & makes things a bit harder but luckily we
# don't use it in our tests

# I think that in the terminal, the script is kicked off by creating a new
# processes group, and ctrl+c works by sending SIGINT to every process in the
# group... but we don't want different process groups in our tests because we
# hope to be able to use ctrl+c to stop the entire test process.. so instead
# we just find all the children recursively and send SIGINT to all of them

# this script makes the processes easily searchable for testing since they
# all contain the time_limit in the command name

time_limit=$1
last_recursion=$2

if [[ "$last_recursion" == "" ]]
then
  $0 $@ yes
else
  sleep $time_limit
fi
