# hacspec

hacspec is a proposal for a new specification language for crypto primitives that is succinct, that is easy to read and implement, and that lends itself to formal verification.

hacspec aims to formalize the pseudocode used in crypto standards by proposing a formal syntax that can be checked for simple errors. hacspec specifications can then be tested against test vectors specified in a common syntax.

hacspec specifications can also be compiled to cryptol, coq, F*, easycrypt, and hence can be used as the basis for formal proofs of functional correctness, cryptographic security, and side-channel resistance.


# status

This project is still in the early stages. We invite submissions of crypto specs in various formal languages and comments and suggestions for the specification syntax. This repository currently holds some preliminary examples collected at the HACS workshop in January 2018.

# contact

Discussions are happening on the [mailing list](https://moderncrypto.org/mailman/listinfo/hacspec).
