#!/usr/bin/env bash

set -v -x

# Travis is weird.
cp -r /home/worker/_hacspec /home/worker/hacspec

# Docker doesn't give us a login shell.
. /home/worker/.opam/opam-init/init.sh > /dev/null 2> /dev/null || true

# Run compilers and type check.
cd /home/worker/hacspec/spec-checker-ocaml
make
make -C fstar-compiler/specs
make -C fstar-compiler/specs check
make -C fstar-compiler/specs tests
# FIXME: checker.native is currently broken.
# ./checker.native ../specs/chacha20.py
