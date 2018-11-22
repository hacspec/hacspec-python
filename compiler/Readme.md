# Compilers

hacspec can be compiled F\*.
Other formal languages should follow.

## Spec Checker

The base for the F\* compiler is an AST generated from the hacspec.
This also allows us to perform rigorous (type) checking on specs.

Run

    make

to build the spec checker.

## F\*

hacspec compiles to F\*. Run

    make

to build the F\* compiler.
The following targets exist for the compiler to generate F\* and check specs
from `../specs`.

    make -C fstar-compiler/specs
    make -C fstar-compiler/specs check
    make -C fstar-compiler/specs tests

Note that this requires `HACL_HOME` to point to a copy of [HACL\*](https://github.com/mitls/hacl-star/) and `FSTAR_HOME` to a copy of [F\*](https://github.com/FStarLang/FStar).
