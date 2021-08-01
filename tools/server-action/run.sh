#! /usr/bin/env bash

set -e

scp_style_target_info=$1
command=$2

echo ${scp_style_target_info} | cut -f 1 -d':' | xargs -I {} ssh {} "$command"
