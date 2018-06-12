# hacspec

hacspec is a proposal for a new specification language for crypto primitives that is succinct, that is easy to read and implement, and that lends itself to formal verification.

hacspec aims to formalize the pseudocode used in crypto standards by proposing a formal syntax that can be checked for simple errors. hacspec specifications can then be tested against test vectors specified in a common syntax.

hacspec specifications can also be compiled to cryptol, coq, F\*, easycrypt, and hence can be used as the basis for formal proofs of functional correctness, cryptographic security, and side-channel resistance.

# status

[![Build Status](https://travis-ci.org/HACS-workshop/hacspec.svg?branch=master)](https://travis-ci.org/HACS-workshop/hacspec)

This project is still in the early stages. We invite submissions of crypto specs in various formal languages and comments and suggestions for the specification syntax. This repository currently holds some preliminary examples collected at the HACS workshop in January 2018.

## compiler

See [spec-compilers](spec-compilers/) for details.

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

    make run     // disabled type checker
    make check   // check hacspec compliance
    make test    // run tests with type checker enabled

to run or check specs.

# contact

Discussions are happening on the [mailing list](https://moderncrypto.org/mailman/listinfo/hacspec).
