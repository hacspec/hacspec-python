# hacspec

hacspec is a proposal for a new specification language for crypto primitives that is succinct, that is easy to read and implement, and that lends itself to formal verification.

hacspec aims to formalize the pseudocode used in crypto standards by proposing a formal syntax that can be checked for simple errors. hacspec specifications can then be tested against test vectors specified in a common syntax.

hacspec specifications can also be compiled to cryptol, coq, F\*, easycrypt, and hence can be used as the basis for formal proofs of functional correctness, cryptographic security, and side-channel resistance.

# status

[![Build Status](https://travis-ci.org/HACS-workshop/hacspec.svg?branch=master)](https://travis-ci.org/HACS-workshop/hacspec)
[![Join the chat at Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/hacspec/Lobby)

This project is still in relatively early stages.

[The wiki](https://github.com/HACS-workshop/hacspec/wiki) contains an overview of the hacspec architecture as well as its current state.

An overview of the current state of hacspec can be found in this [blog post](https://franziskuskiefer.de/post/hacspec2/).
For more details please see the [SSR paper](https://github.com/HACS-workshop/hacspec/blob/master/doc/hacspec-ssr18-paper.pdf) containing the hacspec language definition.

## development

The master branch holds a stable version of hacspec.
Development happens on the [dev branch](https://github.com/HACS-workshop/hacspec/tree/dev).
Please file pull requests against that branch.

## compiler

See [compiler](compiler/) for details.

# How to use

To use hacspec in your project install the hacspec python package as follows.

## Installation via pip
hacspec is distributed as a [pip package](https://pypi.org/project/hacspec/)

    pip install hacspec

To install the hacspec package from its source clone this repository and run

    make -C build install

Now you can use the speclib in your python code with

    from hacspec.speclib import *

The package further provides a tool to check hacpsec files for its correctness

    hacspec-check <your-hacspec>

See the `example` directory for a spec using the hacspec python package.

## Development

When working on hacspec itself installation is not necessary.
The makefile has three main targets

    make run      // disabled type checker
    make check    // check hacspec compliance
    make test     // run tests with type checker enabled
    make compiler // run the full spec checker and compiler (this requires ocaml)

to run or check specs.

# contact

Discussions are happening on the [mailing list](https://moderncrypto.org/mailman/listinfo/hacspec).

Chat with us on [gitter](https://gitter.im/hacspec/Lobby?utm_source=share-link&utm_medium=link&utm_campaign=share-link).
