---
title: High Assurance Crypto Specification Language
abbrev: hacspec
docname: draft-hacspec-latest
category: info

ipr: trust200902
area: IRTF
keyword: Internet-Draft

stand_alone: yes
pi:

author:
 -  ins: K. Bhargavan
    name: Karthikeyan Bhargavan
    organization: Inria
    email: karthik.bhargavan@gmail.com
 -
    ins: F. Kiefer
    name: Franziskus Kiefer
    email: franziskuskiefer@gmail.com

normative:
  RFC2119:

informative:
        

--- abstract

hacspec is a proposal for a new specification language for crypto primitives that is succinct, that is easy to read and implement, and that lends itself to formal verification.

hacspec aims to formalize the pseudocode used in crypto standards by proposing a formal syntax that can be checked for simple errors. hacspec specifications can then be tested against test vectors specified in a common syntax.

hacspec specifications can also be compiled to cryptol, coq, F\*, easycrypt, and hence can be used as the basis for formal proofs of functional correctness, cryptographic security, and side-channel resistance.

--- middle

# Security Considerations


# IANA Considerations

This document makes no requests of IANA.

# Acknowledgements


--- back