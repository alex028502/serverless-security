#! /usr/bin/env bash

set -e

set -o pipefail

./tools/remove-comments.sh sysreq.txt | xargs -n1 tools/sysreq.sh
