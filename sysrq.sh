#! /usr/bin/env bash

set -e

set -o pipefail

./tools/remove-comments.sh sysrq.txt | xargs -n1 tools/sysrq.sh
