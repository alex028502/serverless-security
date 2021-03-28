#! /usr/bin/env bash

if grep -v '^.git' | git check-ignore -nv --stdin | grep '::'
then
  echo source controlled file\(s\) ignored by coverage or format check
  exit 1
fi
