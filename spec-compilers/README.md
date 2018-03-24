# Compilers

hacspec should be compiled to several languages. For now there's support for F\*.

## F\*

hacspec compiles to F\*. Run

    make fstar

to compile hacspecs to F\* and

    make typecheck

This requires `HACL_HOME` to point to a copy of [HACL\*](https://github.com/mitls/hacl-star/).
The resulting F\* code can be found in the `fstar` folder.
