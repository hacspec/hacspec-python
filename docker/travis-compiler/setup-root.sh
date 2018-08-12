#!/usr/bin/env bash

set -v -e -x

# Update packages.
export DEBIAN_FRONTEND=noninteractive
apt-get -qq update
apt-get install -y libssl-dev libsqlite3-dev g++ gcc m4 make pkg-config python \
                   libgmp3-dev cmake curl libtool-bin autoconf wget locales unzip \
                   git

locale-gen en_US.UTF-8
dpkg-reconfigure locales

wget https://raw.github.com/ocaml/opam/master/shell/opam_installer.sh -O - | sh -s /usr/local/bin

apt-get autoremove -y
apt-get clean
apt-get autoclean
