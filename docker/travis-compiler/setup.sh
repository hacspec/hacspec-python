#!/usr/bin/env bash

set -v -e -x

export PATH="$PATH:/usr/local/bin"

# Prepare build (OCaml packages)
opam init --comp ${opamv}
echo ". /home/worker/.opam/opam-init/init.sh > /dev/null 2> /dev/null || true" >> .bashrc
# opam switch -v ${opamv}
opam install ocamlfind batteries sqlite3 fileutils yojson ppx_deriving_yojson zarith pprint menhir ulex process fix wasm stdint

# Get the HACL* code
git clone ${haclrepo} hacl-star
git -C hacl-star checkout ${haclversion}

# Prepare submodules
opam config exec -- make -C hacl-star prepare -j10

# Cleanup.
rm -rf ~/.ccache ~/.cache
