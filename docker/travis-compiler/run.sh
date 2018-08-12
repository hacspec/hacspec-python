#!/usr/bin/env bash

set -v -x

# Copy hacspec into the docker image.
# This is necessary because of weird errors travis throws otherwise.
cp -r /home/worker/_hacspec /home/worker/hacspec

# Run compilers and type check.
cd /home/worker/hacspec/spec-checker-ocaml
make
./checker.native ../specs/chacha20.py
