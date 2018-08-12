#!/usr/bin/env bash

set -v -x

# Run compilers and type check.
cd /home/worker/hacspec/spec-checker-ocaml
make
./checker.native ../specs/chacha20.py
