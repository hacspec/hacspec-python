**FIPS PUB 180-4 **

**FEDERAL INFORMATION PROCESSING STANDARDS PUBLICATION**

**Secure Hash Standard (SHS)**

**CATEGORY: COMPUTER SECURITY SUBCATEGORY: CRYPTOGRAPHY**

Information Technology Laboratory

National Institute of Standards and Technology

Gaithersburg, MD 20899-8900

This publication is available free of charge from:

<http://dx.doi.org/10.6028/NIST.FIPS.180-4>

August 2015

<!-- ![](media/image1.png){width="1.7409722222222221in" height="1.8055555555555556in"} -->

**U.S. Department of Commerce**

*Penny Pritzker, Secretary*

**National Institute of Standards and Technology**

*Willie E. May, Under Secretary for Standards and Technology and
Director*

FOREWORD

The Federal Information Processing Standards Publication Series of the
National Institute of Standards and Technology (NIST) is the official
series of publications relating to standards and guidelines adopted and
promulgated under the provisions of the Federal Information Security
Management Act (FISMA) of 2002.

Comments concerning FIPS publications are welcomed and should be
addressed to the Director, Information Technology Laboratory, National
Institute of Standards and Technology, 100 Bureau Drive, Stop 8900,
Gaithersburg, MD 20899-8900.

Charles H. Romine, Director

Information Technology Laboratory

**Abstract**

This standard specifies hash algorithms that can be used to generate
digests of messages. The digests are used to detect whether messages
have been changed since the digests were generated.

*Key words*: computer security, cryptography, message digest, hash
function, hash algorithm, Federal Information Processing Standards,
Secure Hash Standard.

**Federal Information**

**Processing Standards Publication 180-4**

August 2015

**Announcing the**

**SECURE HASH STANDARD**

Federal Information Processing Standards Publications (FIPS PUBS) are
issued by the National Institute of Standards and Technology (NIST)
after approval by the Secretary of Commerce pursuant to Section 5131 of
the Information Technology Management Reform Act of 1996 (Public Law
104-106), and the Computer Security Act of 1987 (Public Law 100-235).

1.  **Name of Standard**: Secure Hash Standard (SHS) (FIPS PUB 180-4).

2.  **Category of Standard**: Computer Security Standard, Cryptography.

3.  **Explanation**: This Standard specifies secure hash algorithms -
    SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, SHA-512/224 and
    SHA-512/256 - for computing a condensed representation of electronic
    data (message). When a message of any length less than 2^64^ bits
    (for SHA-1, SHA-224 and SHA-256) or less than 2^128^ bits (for
    SHA-384, SHA-512, SHA-512/224 and SHA-512/256) is input to a hash
    algorithm, the result is an output called a message digest. The
    message digests range in length from 160 to 512 bits, depending on
    the algorithm. Secure hash algorithms are typically used with other
    cryptographic algorithms, such as digital signature algorithms and
    keyed-hash message authentication codes, or in the generation of
    random numbers (bits).

The hash algorithms specified in this Standard are called secure
because, for a given algorithm, it is computationally infeasible 1) to
find a message that corresponds to a given message digest, or 2) to find
two different messages that produce the same message digest. Any change
to a message will, with a very high probability, result in a different
message digest. This will result in a verification failure when the
secure hash algorithm is used with a digital signature algorithm or a
keyed-hash message authentication algorithm.

This Standard supersedes FIPS 180-3 \[FIPS 180-3\].

1.  **Approving Authority**: Secretary of Commerce.

2.  **Maintenance Agency**: U.S. Department of Commerce, National
    Institute of Standards and Technology (NIST), Information Technology
    Laboratory (ITL).

**6. Applicability**: This Standard is applicable to all Federal
departments and agencies for the protection of sensitive unclassified
information that is not subject to Title 10 United States Code Section
2315 (10 USC 2315) and that is not within a national security system as
defined in Title 40 United States Code Section 11103(a)(1) (40 USC
11103(a)(1)). Either this Standard or Federal Information Processing
Standard (FIPS) 202 must be implemented wherever a secure hash algorithm
is required for Federal applications, including as a component within
other cryptographic algorithms and protocols. This Standard may be
adopted and used by non-Federal Government organizations.

**7. Specifications**: Federal Information Processing Standard (FIPS)
180-4, Secure Hash Standard (SHS) (affixed).

**8. Implementations:** The secure hash algorithms specified herein may
be implemented in software, firmware, hardware or any combination
thereof. Only algorithm implementations that are validated by NIST will
be considered as complying with this standard. Information about the
validation program can be obtained at
<http://csrc.nist.gov/groups/STM/index.html>.

**9. Implementation Schedule**: Guidance regarding the testing and
validation to FIPS 180-4 and its relationship to FIPS 140-2 can be found
in IG 1.10 of the Implementation Guidance for FIPS PUB 140-2 and the
Cryptographic Module Validation Program at
<http://csrc.nist.gov/groups/STM/cmvp/index.html>.

**10. Patents**: Implementations of the secure hash algorithms in this
standard may be covered by U.S. or foreign patents.

**11. Export Control**: Certain cryptographic devices and technical data
regarding them are\
subject to Federal export controls. Exports of cryptographic modules
implementing this standard and technical data regarding them must comply
with these Federal regulations and be licensed by the Bureau of Export
Administration of the U.S. Department of Commerce. Information about
export regulations is available at: <http://www.bis.doc.gov/index.htm>.

**12. Qualifications:** While it is the intent of this Standard to
specify general security requirements for generating a message digest,
conformance to this Standard does not assure that a particular
implementation is secure. The responsible authority in each agency or
department shall assure that an overall implementation provides an
acceptable level of security. This Standard will be reviewed every five
years in order to assess its adequacy.

**13. Waiver Procedure:** The Federal Information Security Management
Act (FISMA) does not allow for waivers to a FIPS that is made mandatory
by the Secretary of Commerce.

**14. Where to Obtain Copies of the Standard**: This publication is
available electronically by accessing
<http://csrc.nist.gov/publications/>. Other computer security
publications are available at the same web site.

**Federal Information**

**Processing Standards Publication 180-4**

**Specifications for the**

**SECURE HASH STANDARD**

**Table of Contents**

1\. INTRODUCTION 3

2\. DEFINITIONS 4

2.1 Glossary of Terms and Acronyms 4

2.2 Algorithm Parameters, Symbols, and Terms 4

2.2.1 Parameters 4

2.2.2 Symbols and Operations 5

3\. NOTATION AND CONVENTIONS 7

3.1 Bit Strings and Integers 7

3.2 Operations on Words 8

4\. FUNCTIONS AND CONSTANTS 10

4.1 Functions 10

4.1.1 SHA-1 Functions 10

4.1.2 SHA-224 and SHA-256 Functions 10

4.1.3 SHA-384, SHA-512, SHA-512/224 and SHA-512/256 Functions 11

4.2 Constants 11

4.2.1 SHA-1 Constants 11

4.2.2 SHA-224 and SHA-256 Constants 11

4.2.3 SHA-384, SHA-512, SHA-512/224 and SHA-512/256 Constants 12

5\. PREPROCESSING 13

5.1 Padding the Message 13

5.1.1 SHA-1, SHA-224 and SHA-256 13

5.1.2 SHA-384, SHA-512, SHA-512/224 and SHA-512/256 13

5.2 Parsing the Message 14

5.2.1 SHA-1, SHA-224 and SHA-256 14

5.2.2 SHA-384, SHA-512, SHA-512/224 and SHA-512/256 14

5.3 Setting the Initial Hash Value (*H*^(0)^) 14

5.3.1 SHA-1 14

5.3.2 SHA-224 14

5.3.3 SHA-256 15

5.3.4 SHA-384 15

5.3.5 SHA-512 15

5.3.6 SHA-512/t 16

6\. SECURE HASH ALGORITHMS 18

6.1 SHA-1 18

6.1.1 SHA-1 Preprocessing 18

6.1.2 SHA-1 Hash Computation 18

6.1.3 Alternate Method for Computing a SHA-1 Message Digest 20

6.2 SHA-256 21

6.2.1 SHA-256 Preprocessing 22

6.2.2 SHA-256 Hash Computation 22

6.3 SHA-224 23

6.4 SHA-512 24

6.4.1 SHA-512 Preprocessing 24

6.4.2 SHA-512 Hash Computation 24

6.5 SHA-384 26

6.6 SHA-512/224 26

6.7 SHA-512/256 26

7\. TRUNCATION OF A MESSAGE DIGEST 27

APPENDIX A: Additional Information 28

A.1 Security of the Secure Hash Algorithms 28

A.2 Implementation Notes 28

A.3 Object Identifiers 28

APPENDIX B: REFERENCES 29

APPENDIX C: Technical Changes from FIPS 180-3 30

ERRATUM 31

1. INTRODUCTION
===============

This Standard specifies secure hash algorithms, SHA-1, SHA-224, SHA-256,
SHA-384, SHA-512, SHA-512/224 and SHA-512/256. All of the algorithms are
iterative, one-way hash functions that can process a message to produce
a condensed representation called a *message digest*. These algorithms
enable the determination of a message’s integrity: any change to the
message will, with a very high probability, result in a different
message digest. This property is useful in the generation and
verification of digital signatures and message authentication codes, and
in the generation of random numbers or bits.

Each algorithm can be described in two stages: preprocessing and hash
computation. Preprocessing involves padding a message, parsing the
padded message into *m*-bit blocks, and setting initialization values to
be used in the hash computation. The hash computation generates a
*message schedule* from the padded message and uses that schedule, along
with functions, constants, and word operations to iteratively generate a
series of hash values. The final hash value generated by the hash
computation is used to determine the message digest.

The algorithms differ most significantly in the security strengths that
are provided for the data being hashed. The security strengths of these
hash functions and the system as a whole when each of them is used with
other cryptographic algorithms, such as digital signature algorithms and
keyed-hash message authentication codes, can be found in \[SP 800-57\]
and \[SP 800-107\].

Additionally, the algorithms differ in terms of the size of the blocks
and words of data that are used during hashing or message digest sizes.
Figure 1 presents the basic properties of these hash algorithms.

  -------------------------------------------------------------------------------------------------
  **Algorithm**       **Message Size**   **Block Size**   **Word Size**   **Message Digest Size**
                                                                          
<!---                      **(bits)**         **(bits)**       **(bits)**      **(bits)** --->
  ------------------- ------------------ ---------------- --------------- -------------------------
  > **SHA-1**         &lt; 2^64^         512              32              160

  > **SHA-224**       &lt; 2^64^         512              32              224

  > **SHA-256**       &lt; 2^64^         512              32              256

  > **SHA-384**       &lt; 2^128^        1024             64              384

  > **SHA-512**       &lt; 2^128^        1024             64              512

  > **SHA-512/224**   &lt; 2^128^        1024             64              224

  > **SHA-512/256**   &lt; 2^128^        1024             64              256
  -------------------------------------------------------------------------------------------------

Figure 1: Secure Hash Algorithm Properties

2. DEFINITIONS
==============

2.1 Glossary of Terms and Acronyms
----------------------------------

> Bit A binary digit having a value of 0 or 1.
>
> Byte A group of eight bits.
>
> FIPS Federal Information Processing Standard.
>
> NIST National Institute of Standards and Technology.
>
> SHA Secure Hash Algorithm.
>
> SP Special Publication
>
> Word A group of either 32 bits (4 bytes) or 64 bits (8 bytes),
> depending on the secure hash algorithm.

2.2 Algorithm Parameters, Symbols, and Terms
--------------------------------------------

### 2.2.1 Parameters

The following parameters are used in the secure hash algorithm
specifications in this Standard.

> *a, b, c, …, h* Working variables that are the *w*-bit words used in
> the computation of the hash values, *H*^(*i*)^.
>
> The *i*^th^ hash value. *H*^(0)^ is the *initial* hash value;
> *H*^(*N*)^ is the *final* hash value and is used to determine the
> message digest.
>
> The *j*^th^ word of the *i*^th^ hash value, where is the left-most
> word of hash value *i*.
>
> *K~t~* Constant value to be used for the iteration *t* of the hash
> computation.
>
> *k* Number of zeroes appended to a message during the padding step.
>
> Length of the message, *M*, in bits.
>
> *m* Number of bits in a message block, *M^(i)^*.
>
> *M* Message to be hashed.
>
> *M^(i)^* Message block *i*, with a size of *m* bits.
>
> The *j*^th^ word of the *i*^th^ message block, where is the left-most
> word of message block *i*.
>
> *n* Number of bits to be rotated or shifted when a word is operated
> upon.
>
> *N* Number of blocks in the padded message.
>
> *T* Temporary *w*-bit word used in the hash computation.
>
> *w* Number of bits in a word.
>
> *W~t~* The *t*^th^ *w*-bit word of the message schedule.

```cryptol
import Cryptol::Extras
```

### 2.2.2 Symbols and Operations

The following symbols are used in the secure hash algorithm
specifications; each operates on *w*-bit words.

> ∧ Bitwise AND operation.

```cryptol
//  (&&) : {a} a -> a -> a
```

>
> ∨ Bitwise OR (“inclusive-OR”) operation.
>

```cryptol
//  (||) : {a} a -> a -> a
```

> ⊕ Bitwise XOR (“exclusive-OR”) operation.
>

```cryptol
//  (^) : {a} a -> a -> a
```

> ¬ Bitwise complement operation.

```cryptol
//  (~) : {a} a -> a
```

>
> + Addition modulo 2*^w^*.
>

```cryptol
//  (+) : {a} (Arith a) => a -> a -> a
```

> &lt;&lt; Left-shift operation, where *x* &lt;&lt; *n* is obtained by
> discarding the left-most *n* bits of the word *x* and then padding the
> result with *n* zeroes on the right.
>

```cryptol
//  (<<) : {a, b, c} (fin b) => [a]c -> [b] -> [a]c
```

> &gt;&gt; Right-shift operation, where *x* &gt;&gt; *n* is obtained by
> discarding the right-most *n* bits of the word *x* and then padding
> the result with *n* zeroes on the left.
>

```cryptol
//  (>>) : {a, b, c} (fin b) => [a]c -> [b] -> [a]c
```

> The following operations are used in the secure hash algorithm
> specifications:
>
> ***ROTL* *^n^*(*x*)** The *rotate left* (circular left shift)
> operation, where *x* is a *w*-bit word and *n* is an integer with 0
> *n* &lt; *w*, is defined by *ROTL ^n^*(*x*)=(*x* &lt;&lt; *n*)\
> (*x* &gt;&gt; *w* - *n*).

```cryptol
ROTL (n : [8]) x = x <<< n

ROTLDef n x = ~(n < width x) || (ROTL n x == ((x << n) || (x >> ((width x) - n))))
property ROTLDefs n (x8 : [8]) (x16 : [16]) (x32 : [32]) (x64 : [64]) = 
  ROTLDef n x8  && 
  ROTLDef n x16 &&
  ROTLDef n x32 && 
  ROTLDef n x64
```

>
> ***ROTR ^n^*(*x*)** The *rotate right* (circular right shift)
> operation, where *x* is a *w*-bit word and *n* is an integer with 0
> *n* &lt; *w*, is defined by *ROTR* *^n^*(*x*)=(*x* &gt;&gt; *n*)\
> (*x* &lt;&lt; *w* - *n*).

```cryptol
ROTR (n : [8]) x = x >>> n

ROTRDef n x = ~(n < width x) || (ROTR n x == ((x >> n) || (x << ((width x) - n))))
property ROTRDefs n (x8 : [8]) (x16 : [16]) (x32 : [32]) (x64 : [64]) = 
  ROTRDef n x8 && ROTRDef n x16 && ROTRDef n x32 && ROTRDef n x64
```

>
> ***SHR ^n^*(*x*)** The *right shift* operation, where *x* is a *w*-bit
> word and *n* is an integer with 0 *n* &lt; *w*, is defined by *SHR
> ^n^*(*x*)=*x* &gt;&gt; *n*.

```cryptol
SHR : {a, b, c} (fin b) => [b] -> [a]c -> [a]c
SHR n x = x >> n
```

3. NOTATION AND CONVENTIONS
===========================

3.1 Bit Strings and Integers
----------------------------

The following terminology related to bit strings and integers will be
used.

1.  A *hex digit* is an element of the set {0, 1,…, 9, a,…, f}. A hex
    > digit is the representation of a 4-bit string. For example, the
    > hex digit “7” represents the 4-bit string “0111”, and the hex
    > digit “a” represents the 4-bit string “1010”.

2.  A *word* is a *w*-bit string that may be represented as a sequence
    > of hex digits. To convert a word to hex digits, each 4-bit string
    > is converted to its hex digit equivalent, as described in (1)
    > above. For example, the 32-bit string

1010 0001 0000 0011 1111 1110 0010 0011

> can be expressed as “a103fe23”, and the 64-bit string

1010 0001 0000 0011 1111 1110 0010 0011

0011 0010 1110 1111 0011 0000 0001 1010

> can be expressed as “a103fe2332ef301a”.
>
> *Throughout this specification, the “big-endian” convention is used
> when expressing both 32- and 64-bit words, so that within each word,
> the most significant bit is stored in the left-most bit position.*

1.  An *integer* may be represented as a word or pair of words. A word
    > representation of the message length, , in bits, is required for
    > the padding techniques of Sec. 5.1.

> An integer between 0 and 2^32^-1 *inclusive* may be represented as a
> 32-bit word. The least significant four bits of the integer are
> represented by the right-most hex digit of the word representation.
> For example, the integer 291=2^8^ + 2^5^ + 2^1^ + 2^0^=256+32+2+1 is
> represented by the hex word “00000123”.
>
> The same holds true for an integer between 0 and 2^64^-1 *inclusive*,
> which may be represented as a 64-bit word.
>
> If *Z* is an integer, 0 *Z* &lt; 2^64^, then *Z*=2^32^*X* + *Y*, where
> 0 *X* &lt; 2^32^ and 0 *Y* &lt; 2^32^. Since *X* and *Y* can be
> represented as 32-bit words *x* and *y*, respectively, the integer *Z*
> can be represented as the pair of words (*x*, *y*). This property is
> used for SHA-1, SHA-224 and SHA-256.
>
> If *Z* is an integer, 0 *Z* &lt; 2^128^, then *Z*=2^64^*X* + *Y*,
> where 0 *X* &lt; 2^64^ and 0 *Y* &lt; 2^64^. Since *X* and *Y* can be
> represented as 64-bit words *x* and *y*, respectively, the integer *Z*
> can be represented as the pair of words (*x*, *y*). This property is
> used for SHA-384, SHA-512, SHA-512/224 and SHA-512/256.

1.  For the secure hash algorithms, the size of the *message block* -
    > *m* bits - depends on the algorithm.

<!-- -->

a)  For **SHA-1, SHA-224** and **SHA-256**, each message block has **512
    > bits**, which are represented as a sequence of sixteen **32-bit
    > words**.

b)  For **SHA-384**, **SHA-512, SHA-512/224** and **SHA-512/256** each
    > message block has **1024 bits**, which are represented as a
    > sequence of sixteen **64-bit words**.

3.2 Operations on Words
-----------------------

The following operations are applied to *w*-bit words in all five secure
hash algorithms. SHA-1, SHA-224 and SHA-256 operate on 32-bit words
(*w*=32), and SHA-384, SHA-512, SHA-512/224 and SHA-512/256 operate on
64-bit words (*w*=64).

1.  Bitwise *logical* word operations: , , , and (see Sec. 2.2.2).

2.  Addition modulo 2*^w^*.

> The operation *x* + *y* is defined as follows. The words *x* and *y*
> represent integers *X* and *Y*, where 0 *X* &lt; 2*^w^* and 0 *Y* &lt;
> 2*^w^*. For positive integers *U* and *V*, let be the remainder upon
> dividing *U* by *V*. Compute
>
> *Z*=( *X* + *Y* ) mod 2*^w^*.
>
> Then 0 *Z* &lt; 2*^w^*. Convert the integer *Z* to a word, *z*, and
> define *z=x* + *y*.

1.  The *right shift* operation ***SHR ^n^*(*x*)**, where *x* is a
    > *w*-bit word and *n* is an integer with 0 *n* &lt; *w*, is defined
    > by

> *SHR ^n^*(*x*)=*x* &gt;&gt; *n*.
>
> This operation is used in the SHA-224, SHA-256, SHA-384, SHA-512,
> SHA-512/224 and SHA-512/256 algorithms.

1.  The *rotate right* (circular right shift) operation ***ROTR
    > ^n^*(*x*)**, where *x* is a *w*-bit word and *n* is an integer
    > with 0 *n* &lt; *w*, is defined by

> *ROTR* *^n^*(*x*)=(*x* &gt;&gt; *n*) (*x* &lt;&lt; *w* - *n*).
>
> Thus, *ROTR* *^n^*(*x*) is equivalent to a circular shift (rotation)
> of *x* by *n* positions to the right.
>
> This operation is used by the SHA-224, SHA-256, SHA-384, SHA-512,
> SHA-512/224 and SHA-512/256 algorithms.

5.  The *rotate left* (circular left shift) operation, ***ROTL*
    > *^n^*(*x*)**, where *x* is a *w*-bit word and *n* is an integer
    > with 0 *n* &lt; *w*, is defined by

> *ROTL ^n^*(*x*)=(*x* &lt;&lt; *n*) (*x* &gt;&gt; *w* - *n*).
>
> Thus, *ROTL ^n^*(*x*) is equivalent to a circular shift (rotation) of
> *x* by *n* positions to the left.
>
> This operation is used only in the SHA-1 algorithm.

5.  Note the following equivalence relationships, where *w* is fixed in
    > each relationship:

> *ROTL ^n^*(*x*) *ROTR ^w-n^*(*x*)

```cryptol
ROTLREquiv n x = ROTL n x == ROTR (width x - n) x
property ROTLREquivs n (x8 : [8]) (x16 : [16]) (x32 : [32]) (x64 : [64]) =
  ROTLREquiv n x8 && ROTLREquiv n x16 && ROTLREquiv n x32 && ROTLREquiv n x64
```

>
> *ROTR ^n^*(*x*) *ROTL ^w-n^*(*x*)

```cryptol
ROTRLEquiv n x = ROTR n x == ROTL (width x - n) x
property ROTRLEquivs n (x8 : [8]) (x16 : [16]) (x32 : [32]) (x64 : [64]) =
  ROTRLEquiv n x8 && ROTRLEquiv n x16 && ROTRLEquiv n x32 && ROTRLEquiv n x64
```

4. FUNCTIONS AND CONSTANTS
==========================

4.1 Functions
-------------

This section defines the functions that are used by each of the
algorithms. Although the SHA-224, SHA-256, SHA-384,SHA-512, SHA-512/224
and SHA-512/256 algorithms all use similar functions, their descriptions
are separated into sections for SHA-224 and SHA-256 (Sec. 4.1.2) and for
SHA-384, SHA-512, SHA-512/224 and SHA-512/256 (Sec. 4.1.3), since the
input and output for these functions are words of different sizes. Each
of the algorithms include *Ch*(*x*, *y*, *z*) and *Maj*(*x*, *y*, *z*)
functions; the exclusive-OR operation () in these functions may be
replaced by a bitwise OR operation (∨) and produce identical results.

### 4.1.1 SHA-1 Functions

SHA-1 uses a sequence of logical functions, *f*~0~, *f*~1~,…, *f*~79~.
Each function *f*~t~, where 0 *t* 79, operates on three 32-bit words,
*x*, *y*, and *z*, and produces a 32-bit word as output. The function
*f~t~* (*x*, *y*, *z*) is defined as follows:

*Ch*(*x*, *y*, *z*)=(*xy*) (*xz*) 0 *t* 19

*Parity*(*x*, *y*, *z*)=x *y* *z* 20 *t* 39

*f~t~* (*x*, *y*, *z*) = (4.1)

*Maj*(*x*, *y*, *z*)=(*xy*) (*xz*) (*yz*) 40 *t* 59

*Parity*(*x*, *y*, *z*)=*x* *y* *z* 60 *t* 79.

```cryptol
Ch : {a} a -> a -> a -> a
Ch x y z = (x && y) ^ (~x && z)

Parity : {a} a -> a -> a -> a
Parity x y z = x ^ y ^ z

Maj : {a} a -> a -> a -> a
Maj x y z = (x && y) ^ (x && z) ^ (y && z)

Ch' : {a} a -> a -> a -> a
Ch' x y z = (x && y) || (~x && z)

Maj' : {a} a -> a -> a -> a
Maj' x y z = (x && y) || (x && z) || (y && z)

ChXorOrEquiv x y z = Ch x y z == Ch' x y z
property ChXorOrEquiv32 (x : [32]) (y : [32]) (z : [32]) = ChXorOrEquiv x y z

f : [8] -> [32] -> [32] -> [32] -> [32]
f t = if t <= 19 then Ch
      else if t <= 39 then Parity
      else if t <= 59 then Maj
      else if t <= 79 then Parity
      else error "f: t is out of range"
```

### 4.1.2 SHA-224 and SHA-256 Functions

SHA-224 and SHA-256 both use six logical functions, where *each function
operates on 32-bit words*, which are represented as *x*, *y*, and *z*.
The result of each function is a new 32-bit word.

= (4.2)

= (4.3)

= *ROTR* ^2^(*x*) *ROTR* ^13^(*x*) *ROTR* ^22^(*x*) (4.4)

= *ROTR* ^6^(*x*) *ROTR* ^11^(*x*) *ROTR* ^25^(*x*) (4.5)

= *ROTR* ^7^(*x*) *ROTR* ^18^(*x*) *SHR* ^3^(*x*) (4.6)

= *ROTR* ^17^(*x*) *ROTR* ^19^(*x*) *SHR* ^10^(*x*) (4.7)

```cryptol
S_0_256 x = ROTR  2 x ^ ROTR 13 x ^ ROTR 22 x
S_1_256 x = ROTR  6 x ^ ROTR 11 x ^ ROTR 25 x
s_0_256 x = ROTR  7 x ^ ROTR 18 x ^ SHR   3 x
s_1_256 x = ROTR 17 x ^ ROTR 19 x ^ SHR  10 x
```

### 4.1.3 SHA-384, SHA-512, SHA-512/224 and SHA-512/256 Functions

SHA-384, SHA-512, SHA-512/224 and SHA-512/256 use six logical functions,
where *each function operates on 64-bit words*, which are represented as
*x*, *y*, and *z*. The result of each function is a new 64-bit word.

= (4.8)

= (4.9)

= *ROTR* ^28^(*x*) *ROTR* ^34^(*x*) *ROTR* ^39^(*x*) (4.10)

= *ROTR* ^14^(*x*) *ROTR* ^18^(*x*) *ROTR* ^41^(*x*) (4.11)

= *ROTR* ^1^(*x*) *ROTR* ^8^(*x*) *SHR* ^7^(*x*) (4.12)

= *ROTR* ^19^(*x*) *ROTR* ^61^(*x*) *SHR* ^6^(*x*) (4.13)

```cryptol
property ChXorOrEquiv64 (x : [64]) (y : [64]) (z : [64]) = ChXorOrEquiv x y z

S_0_512 x = ROTR 28 x ^ ROTR 34 x ^ ROTR 39 x
S_1_512 x = ROTR 14 x ^ ROTR 18 x ^ ROTR 41 x
s_0_512 x = ROTR  1 x ^ ROTR  8 x ^ SHR   7 x
s_1_512 x = ROTR 19 x ^ ROTR 61 x ^ SHR   6 x
```

4.2 Constants
-------------

### 4.2.1 SHA-1 Constants

SHA-1 uses a sequence of eighty constant 32-bit words, *K*~0~, *K*~1~,…,
*K*~79~, which are given by

5a827999 0 *t* 19

6ed9eba1 20 *t* 39

*K~t~* = (4.14)

8f1bbcdc 40 *t* 59

ca62c1d6 60 *t* 79

```cryptol
sha1_K : [80][32]
sha1_K = [ 0x5a827999 | t <- [ 0 .. 19] ] #
         [ 0x6ed9eba1 | t <- [20 .. 39] ] #
         [ 0x8f1bbcdc | t <- [40 .. 59] ] #
         [ 0xca62c1d6 | t <- [60 .. 79] ]
```

### 4.2.2 SHA-224 and SHA-256 Constants

SHA-224 and SHA-256 use the same sequence of sixty-four constant 32-bit
words, . These words represent the first thirty-two bits of the
fractional parts of the cube roots of the first sixty-four prime
numbers. In hex, these constant words are (from left to right)

> 428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4
> ab1c5ed5
>
> d807aa98 12835b01 243185be 550c7dc3 72be5d74 80deb1fe 9bdc06a7
> c19bf174
>
> e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc
> 76f988da
>
> 983e5152 a831c66d b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351
> 14292967
>
> 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e
> 92722c85
>
> a2bfe8a1 a81a664b c24b8b70 c76c51a3 d192e819 d6990624 f40e3585
> 106aa070
>
> 19a4c116 1e376c08 2748774c 34b0bcb5 391c0cb3 4ed8aa4a 5b9cca4f
> 682e6ff3
>
> 748f82ee 78a5636f 84c87814 8cc70208 90befffa a4506ceb bef9a3f7
> c67178f2

```cryptol
K32 : [64][32]
K32 = [ 0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2  ]
```

### 4.2.3 SHA-384, SHA-512, SHA-512/224 and SHA-512/256 Constants

SHA-384, SHA-512, SHA-512/224 and SHA-512/256 use the same sequence of
eighty constant 64-bit words, . These words represent the first
sixty-four bits of the fractional parts of the cube roots of the first
eighty prime numbers. In hex, these constant words are (from left to
right)

> 428a2f98d728ae22 7137449123ef65cd b5c0fbcfec4d3b2f e9b5dba58189dbbc
>
> 3956c25bf348b538 59f111f1b605d019 923f82a4af194f9b ab1c5ed5da6d8118
>
> d807aa98a3030242 12835b0145706fbe 243185be4ee4b28c 550c7dc3d5ffb4e2
>
> 72be5d74f27b896f 80deb1fe3b1696b1 9bdc06a725c71235 c19bf174cf692694
>
> e49b69c19ef14ad2 efbe4786384f25e3 0fc19dc68b8cd5b5 240ca1cc77ac9c65
>
> 2de92c6f592b0275 4a7484aa6ea6e483 5cb0a9dcbd41fbd4 76f988da831153b5
>
> 983e5152ee66dfab a831c66d2db43210 b00327c898fb213f bf597fc7beef0ee4
>
> c6e00bf33da88fc2 d5a79147930aa725 06ca6351e003826f 142929670a0e6e70
>
> 27b70a8546d22ffc 2e1b21385c26c926 4d2c6dfc5ac42aed 53380d139d95b3df
>
> 650a73548baf63de 766a0abb3c77b2a8 81c2c92e47edaee6 92722c851482353b
>
> a2bfe8a14cf10364 a81a664bbc423001 c24b8b70d0f89791 c76c51a30654be30
>
> d192e819d6ef5218 d69906245565a910 f40e35855771202a 106aa07032bbd1b8
>
> 19a4c116b8d2d0c8 1e376c085141ab53 2748774cdf8eeb99 34b0bcb5e19b48a8
>
> 391c0cb3c5c95a63 4ed8aa4ae3418acb 5b9cca4f7763e373 682e6ff3d6b2b8a3
>
> 748f82ee5defb2fc 78a5636f43172f60 84c87814a1f0ab72 8cc702081a6439ec
>
> 90befffa23631e28 a4506cebde82bde9 bef9a3f7b2c67915 c67178f2e372532b
>
> ca273eceea26619c d186b8c721c0c207 eada7dd6cde0eb1e f57d4f7fee6ed178
>
> 06f067aa72176fba 0a637dc5a2c898a6 113f9804bef90dae 1b710b35131c471b
>
> 28db77f523047d84 32caab7b40c72493 3c9ebe0a15c9bebc 431d67c49c100d4c
>
> 4cc5d4becb3e42b6 597f299cfc657e2a 5fcb6fab3ad6faec 6c44198c4a475817

```cryptol
K64 : [80][64]
K64 = [ 0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
        0x3956c25bf348b538, 0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
        0xd807aa98a3030242, 0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
        0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 0xc19bf174cf692694,
        0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
        0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
        0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4,
        0xc6e00bf33da88fc2, 0xd5a79147930aa725, 0x06ca6351e003826f, 0x142929670a0e6e70,
        0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
        0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6, 0x92722c851482353b,
        0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30,
        0xd192e819d6ef5218, 0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
        0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
        0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
        0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
        0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b,
        0xca273eceea26619c, 0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
        0x06f067aa72176fba, 0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
        0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
        0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817  ]
```

5. PREPROCESSING
================

Preprocessing consists of three steps: padding the message, *M* (Sec.
5.1), parsing the message into message blocks (Sec. 5.2), and setting
the initial hash value, *H*^(0)^ (Sec. 5.3).

5.1 Padding the Message
-----------------------

The purpose of this padding is to ensure that the padded message is a
multiple of 512 or 1024 bits, depending on the algorithm. Padding can be
inserted before hash computation begins on a message, or at any other
time during the hash computation prior to processing the block(s) that
will contain the padding.

### 5.1.1 SHA-1, SHA-224 and SHA-256

Suppose that the length of the message, *M*, is bits. Append the bit “1”
to the end of the message, followed by *k* zero bits, where *k* is the
smallest, non-negative solution to the equation . Then append the 64-bit
block that is equal to the number expressed using a binary
representation. For example, the (8-bit ASCII) message “**abc**” has
length , so the message is padded with a one bit, then zero bits, and
then the message length, to become the 512-bit padded message

423 64

01100001 01100010 01100011 1 00…00 00…011000

“**a**” “**b**” “**c**”

The length of the padded message should now be a multiple of 512 bits.

```cryptol
pad512 : {msgLen} 
          (fin msgLen,
           64 >= width msgLen) => 
          [msgLen] -> [msgLen + 65 + (512 - (msgLen + 65) % 512) % 512]
pad512 msg = msg # [True] # (zero:[padding]) # (`msgLen:[64])
  where type contentLen = msgLen + 65
        type padding    = (512 - contentLen % 512) % 512 
```

### 5.1.2 SHA-384, SHA-512, SHA-512/224 and SHA-512/256

Suppose the length of the message *M*, in bits, is bits. Append the bit
“1” to the end of the message, followed by *k* zero bits, where *k* is
the smallest non-negative solution to the equation . Then append the
128-bit block that is equal to the number expressed using a binary
representation. For example, the (8-bit ASCII) message “**abc**” has
length , so the message is padded with a one bit, then zero bits, and
then the message length, to become the 1024-bit padded message

871 128

01100001 01100010 01100011 1 00…00 00…011000

“**a**” “**b**” “**c**”

The length of the padded message should now be a multiple of 1024 bits.

```cryptol
pad1024 : {msgLen} 
          (fin msgLen,
           128 >= width msgLen) => 
          [msgLen] -> [msgLen + 129 + (1024 - (msgLen + 129) % 1024) % 1024]
pad1024 msg = msg # [True] # (zero:[padding]) # (`msgLen:[128])
  where type contentLen = msgLen + 129
        type padding    = (1024 - contentLen % 1024) % 1024 
```

5.2 Parsing the Message
-----------------------

The message and its padding must be parsed into *N* *m*-bit blocks.

### 5.2.1 SHA-1, SHA-224 and SHA-256

For SHA-1, SHA-224 and SHA-256, the message and its padding are parsed
into *N* 512-bit blocks, *M*^(1)^, *M*^(2)^,…, *M*^(*N*)^. Since the 512
bits of the input block may be expressed as sixteen 32-bit words, the
first 32 bits of message block *i* are denoted , the next 32 bits are ,
and so on up to .

```cryptol
parse512 : {blocks} [512 * blocks] -> [blocks][512]
parse512 = split

padparse512 : {msgLen,blocks} 
              ( fin msgLen, 
                64 >= width msgLen, 
                blocks == (msgLen + 65 + 511) / 512) => 
              [msgLen] -> [blocks][512]
padparse512 M = parse512 (pad512 M) 
```

### 5.2.2 SHA-384, SHA-512, SHA-512/224 and SHA-512/256

For SHA-384, SHA-512, SHA-512/224 and SHA-512/256, the message and its
padding are parsed into *N* 1024-bit blocks, *M*^(1)^, *M*^(2)^,…,
*M*^(*N*)^. Since the 1024 bits of the input block may be expressed as
sixteen 64-bit words, the first 64 bits of message block *i* are denoted
, the next 64 bits are , and so on up to .

```cryptol
parse1024 : {blocks} [1024 * blocks] -> [blocks][1024]
parse1024 = split

padparse1024 : {msgLen,blocks} 
               ( fin msgLen, 
                 128 >= width msgLen, 
                 blocks == (msgLen + 129 + 1023) / 1024 ) => 
               [msgLen] -> [blocks][1024]
padparse1024 M = parse1024 (pad1024 M)
```

5.3 Setting the Initial Hash Value (*H*^(0)^)
---------------------------------------------

Before hash computation begins for each of the secure hash algorithms,
the initial hash value, *H*^(0)^, must be set. The size and number of
words in *H*^(0)^ depends on the message digest size.

### 5.3.1 SHA-1

For SHA-1, the initial hash value, *H*^(0)^, shall consist of the
following five 32-bit words, in hex:

= 67452301

= efcdab89

= 98badcfe

= 10325476

= c3d2e1f0

```cryptol
sha1_H0 : [5][32]
sha1_H0 = [ 0x67452301, 
            0xefcdab89,
            0x98badcfe,
            0x10325476,
            0xc3d2e1f0  ]
```

### 5.3.2 SHA-224

For SHA-224, the initial hash value, *H*^(0)^, shall consist of the
following eight 32-bit words, in hex:

= c1059ed8

= 367cd507

= 3070dd17

= f70e5939

= ffc00b31

= 68581511

= 64f98fa7

= befa4fa4

```cryptol
sha224_H0 : [8][32]
sha224_H0 = [ 0xc1059ed8,
              0x367cd507,
              0x3070dd17,
              0xf70e5939,
              0xffc00b31,
              0x68581511,
              0x64f98fa7,
              0xbefa4fa4  ]
```

### 5.3.3 SHA-256

For SHA-256, the initial hash value, *H*^(0)^, shall consist of the
following eight 32-bit words, in hex:

= 6a09e667

= bb67ae85

= 3c6ef372

= a54ff53a

= 510e527f

= 9b05688c

= 1f83d9ab

= 5be0cd19

```cryptol
sha256_H0 : [8][32]
sha256_H0 = [ 0x6a09e667,
              0xbb67ae85,
              0x3c6ef372,
              0xa54ff53a,
              0x510e527f,
              0x9b05688c,
              0x1f83d9ab,
              0x5be0cd19  ]

```

These words were obtained by taking the first thirty-two bits of the
fractional parts of the square roots of the first eight prime numbers.

### 5.3.4 SHA-384

For SHA-384, the initial hash value, *H*^(0)^, shall consist of the
following eight 64-bit words, in hex:

= cbbb9d5dc1059ed8

= 629a292a367cd507

= 9159015a3070dd17

= 152fecd8f70e5939

= 67332667ffc00b31

= 8eb44a8768581511

= db0c2e0d64f98fa7

= 47b5481dbefa4fa4

```cryptol
sha384_H0 : [8][64]
sha384_H0 = [ 0xcbbb9d5dc1059ed8,
              0x629a292a367cd507,
              0x9159015a3070dd17,
              0x152fecd8f70e5939,
              0x67332667ffc00b31,
              0x8eb44a8768581511,
              0xdb0c2e0d64f98fa7,
              0x47b5481dbefa4fa4  ]
```

These words were obtained by taking the first sixty-four bits of the
fractional parts of the square roots of the ninth through sixteenth
prime numbers.

### 5.3.5 SHA-512

For SHA-512, the initial hash value, *H*^(0)^, shall consist of the
following eight 64-bit words, in hex:

= 6a09e667f3bcc908

= bb67ae8584caa73b

= 3c6ef372fe94f82b

= a54ff53a5f1d36f1

= 510e527fade682d1

= 9b05688c2b3e6c1f

= 1f83d9abfb41bd6b

= 5be0cd19137e2179

```cryptol
sha512_H0 : [8][64]
sha512_H0 = [ 0x6a09e667f3bcc908,
              0xbb67ae8584caa73b,
              0x3c6ef372fe94f82b,
              0xa54ff53a5f1d36f1,
              0x510e527fade682d1,
              0x9b05688c2b3e6c1f,
              0x1f83d9abfb41bd6b,
              0x5be0cd19137e2179  ]
```

These words were obtained by taking the first sixty-four bits of the
fractional parts of the square roots of the first eight prime numbers.

### 5.3.6 SHA-512 / *t*

"SHA-512 / *t*" is the general name for a *t*-bit hash function based on
SHA-512 whose output is truncated to *t* bits. Each hash function
requires a distinct initial hash value. This section provides a
procedure for determining the initial value for SHA-512/ *t* for a given
value of *t*.

For SHA-512 / *t*, *t* is any positive integer without a leading zero such
that *t* &lt; 512, and *t* is not 384. For example: *t* is 256, but not
0256, and “SHA-512 / *t*” is “SHA-512/256” (an 11 character long ASCII
string), which is equivalent to 53 48 41 2D 35 31 32 2F 32 35 36 in
hexadecimal.

The initial hash value for SHA-512 / *t*, for a given value of *t*, shall
be generated by the SHA-512 / *t* IV Generation Function below.

*SHA-512/t IV Generation Function*

(begin:)

Denote *H*^(0)′^ to be the initial hash value of SHA-512 as specified in
Section 5.3.5 above.

Denote *H*^(0)′′^ to be the initial hash value computed below.

*H*^(0)^ is the IV for SHA-512 / *t*.

For *i* = 0 to 7

> {
>
> *H~i~*^(0)′′^ = *H~i~*^(0)′^ a5a5a5a5a5a5a5a5(in hex).
>
> }

*H*^(0)^ = SHA-512 (“SHA-512 / *t*”) using *H*^(0)′′^ as the IV, where *t*
is the specific truncation value.

(end.)

```cryptol
sha512t_H_internal : [8][64]
sha512t_H_internal = [ h ^ 0xa5a5a5a5a5a5a5a5 | h <- sha512_H0]
```

SHA-512/224 (*t* = 224) and SHA-512/256 (*t* = 256) are **approved**
hash algorithms. Other SHA-512 / *t* hash algorithms with different *t*
values may be specified in \[SP 800-107\] in the future as the need
arises. Below are the IVs for SHA-512/224 and SHA-512/256.

#### 5.3.6.1 SHA-512/224

For SHA-512/224, the initial hash value, *H*^(0)^, shall consist of the
following eight 64-bit words, in hex:

= 8C3D37C819544DA2

= 73E1996689DCD4D6

= 1DFAB7AE32FF9C82

= 679DD514582F9FCF

= 0F6D2B697BD44DA8

= 77E36F7304C48942

= 3F9D85A86A1D36C8

= 1112E6AD91D692A1

```cryptol
sha512_224_H0 : [8][64]
sha512_224_H0 = [ 0x8C3D37C819544DA2,
                  0x73E1996689DCD4D6,
                  0x1DFAB7AE32FF9C82,
                  0x679DD514582F9FCF,
                  0x0F6D2B697BD44DA8,
                  0x77E36F7304C48942,
                  0x3F9D85A86A1D36C8,
                  0x1112E6AD91D692A1  ]

property sha512_224_H0s_equiv = 
  sha512_224_H0 == split (sha512t "SHA-512/224" sha512t_H_internal)
```

These words were obtained by executing the *SHA-512/t IV Generation
Function* with *t* = 224.

#### 5.3.6.2 SHA-512/256

For SHA-512/256, the initial hash value, *H*^(0)^, shall consist of the
following eight 64-bit words, in hex:

= 22312194FC2BF72C

= 9F555FA3C84C64C2

= 2393B86B6F53B151

= 963877195940EABD

= 96283EE2A88EFFE3

= BE5E1E2553863992

= 2B0199FC2C85B8AA

= 0EB72DDC81C52CA2

```cryptol
sha512_256_H0 : [8][64]
sha512_256_H0 = [ 0x22312194FC2BF72C,
                  0x9F555FA3C84C64C2,
                  0x2393B86B6F53B151,
                  0x963877195940EABD,
                  0x96283EE2A88EFFE3,
                  0xBE5E1E2553863992,
                  0x2B0199FC2C85B8AA,
                  0x0EB72DDC81C52CA2  ]

property sha512_256_H0s_equiv = 
  sha512_256_H0 == split (sha512t "SHA-512/256" sha512t_H_internal)
```

These words were obtained by executing the *SHA-512/t IV Generation
Function* with *t* = 256.

6. SECURE HASH ALGORITHMS
=========================

In the following sections, the hash algorithms are not described in
ascending order of size. SHA-256 is described before SHA-224 because the
specification for SHA-224 is identical to SHA-256, except that different
initial hash values are used, and the final hash value is truncated to
224 bits for SHA-224. The same is true for SHA-512, SHA-384, SHA-512/224
and SHA-512/256, except that the final hash value is truncated to 224
bits for SHA-512/224, 256 bits for SHA-512/256 or 384 bits for SHA-384.

For each of the secure hash algorithms, there may exist alternate
computation methods that yield identical results; one example is the
alternative SHA-1 computation described in Sec. 6.1.3. Such alternate
methods may be implemented in conformance to this standard.

6.1 SHA-1
---------

SHA-1 may be used to hash a message, *M*, having a length of bits, where
. The algorithm uses 1) a message schedule of eighty 32-bit words, 2)
five working variables of 32 bits each, and 3) a hash value of five
32-bit words. The final result of SHA-1 is a 160-bit message digest.

The words of the message schedule are labeled *W*~0~, *W*~1~,…, *W*~79~.
The five working variables are labeled ***a***, ***b***, ***c***,
***d***, and ***e***. The words of the hash value are labeled , which
will hold the initial hash value, *H*^(0)^, replaced by each successive
intermediate hash value (after each message block is processed),
*H*^(*i*)^, and ending with the final hash value, *H*^(*N*)^. SHA-1 also
uses a single temporary word, *T*.

### 6.1.1 SHA-1 Preprocessing

1.  Set the initial hash value, *H*^(0)^, as specified in Sec. 5.3.1.

2.  The message is padded and parsed as specified in Section 5.

### 6.1.2 SHA-1 Hash Computation

The SHA-1 hash computation uses functions and constants previously
defined in Sec. 4.1.1 and Sec. 4.2.1, respectively. Addition (+) is
performed modulo 2^32^.

Each message block, *M*^(1)^, *M*^(2)^, …, *M*^(*N*)^, is processed in
order, using the following steps:

> For *i*=1 to *N*:
>
> {

1.  Prepare the message schedule, {*W~t~*}:

> =
>
> *ROTL*^1^()

```cryptol
sha1_W : [16][32] -> [80][32]
sha1_W Mblock = W
  where W = Mblock # [ ROTL 1 (W@(t - 3) ^ W@(t - 8) ^ W@(t - 14) ^ W@(t-16)) | t <- [16 .. 79] ]
```


1.  Initialize the five working variables, ***a***, ***b***, ***c***,
    > ***d***, and ***e***, with the (*i*-1)^st^ hash value:

2.  For *t*=0 to 79:

> {
>
> }

```cryptol
sha1_T : [80][32] -> [8] -> [5][32] -> [32]
sha1_T W t abcde = (ROTL 5 a) + (f t b c d) + e + (sha1_K @ t) + (W @ t)
  where [a, b, c, d, e] = abcde

sha1_helper : [16][32] -> [80][32] -> [8] -> [6][32] -> [6][32]
sha1_helper Mblock W t Tabcde = [ T', a', b', c', d', e' ]
  where [T, a, b, c, d, e] = Tabcde
        T' = sha1_T W t [a', b', c', d', e']
        e' = d
        d' = c
        c' = ROTL 30 b
        b' = a
        a' = T
```

```cryptol
sha1_block : [16][32] -> [5][32] -> [5][32]
sha1_block Mblock abcde = drop`{1}(Tabcdes ! 0)
  where W       = sha1_W Mblock
        sha1_h  = sha1_helper Mblock W
        Tabcde0 = [sha1_T W 0 abcde] # abcde
        Tabcdes = [ Tabcde0 ] # [ sha1_h (t+1) (Tabcdes @ t) | t <- [ 0 .. 79 ] ]
```

```cryptol
// Another (cleaner) specification of sha1_block processing
sha1_block' : [16][32] -> [5][32] -> [5][32]
sha1_block' Mblock [a0, b0, c0, d0, e0] = 
    [as@80, bs@80, cs@80, ds@80, es@80]
  where
    W  = sha1_W Mblock
    Ts = [ sha1_T W t [a, b, c, d, e]
           | a <- as | b <- bs | c <- cs | d <- ds | e <- es
           | t <- [0..79]
           ]
    es = [e0] # ds
    ds = [d0] # cs
    cs = [c0] # [ ROTL 30 b | b <- bs ]
    bs = [b0] # as
    as = [a0] # Ts

property sha1_blocks_equiv Mblock H =
  sha1_block Mblock H == sha1_block' Mblock H 
```

1.  Compute the *i*^th^ intermediate hash value *H*^(*i*)^:

> }

```cryptol
sha1_H : [5][32] -> [5][32] -> [5][32]
sha1_H H abcde = zipWith (+) abcde H

sha1_Hblock : [5][32] -> [512] -> [5][32]
sha1_Hblock H Mblock = sha1_H H (sha1_block (split Mblock) H)

sha1_Hblock' : [5][32] -> [512] -> [5][32]
sha1_Hblock' H Mblock = sha1_H H (sha1_block' (split Mblock) H)

property sha1_Hblocks_equiv Mblock H =
  sha1_Hblock Mblock H == sha1_Hblock' Mblock H 
```

After repeating steps one through four a total of *N* times (i.e., after
processing *M^(N)^*), the resulting 160-bit message digest of the
message, *M*, is

```cryptol
sha1parsed : {blocks} (fin blocks) => [blocks][512] -> [160]
sha1parsed Mparsed = join (Hs ! 0)
  where Hs = [sha1_H0] # [ sha1_Hblock H Mblock | H <- Hs | Mblock <- Mparsed]

sha1 : {n} (width (8*n) <= 64) => [n][8] -> [160]
sha1 M = sha1parsed (padparse512 (join M))
```

### 6.1.3 Alternate Method for Computing a SHA-1 Message Digest

The SHA-1 hash computation method described in Sec. 6.1.2 assumes that
the message schedule *W*~0~, *W*~1~,…, *W*~79~ is implemented as an
array of eighty 32-bit words. This is efficient from the standpoint of
the minimization of execution time, since the addresses of *W~t~*~-3~,…,
W~*t*-16~ in step (2) of Sec. 6.1.2 are easily computed.

However, if memory is limited, an alternative is to regard {*W~t~*} as a
circular queue that may be implemented using an array of sixteen 32-bit
words, *W*~0~, *W*~1~,…, *W*~15~. The alternate method that is described
in this section yields the same message digest as the SHA-1 computation
method described in Sec. 6.1.2. Although this alternate method saves
sixty-four 32-bit words of storage, it is likely to lengthen the
execution time due to the increased complexity of the address
computations for the {*W~t~*} in step (3).

For this alternate SHA-1 method, let *MASK*=0000000f (in hex). As in
Sec. 6.1.1, addition is performed modulo 2^32^. Assuming that the
preprocessing as described in Sec. 6.1.1 has been performed, the
processing of *M*^(*i*)^ is as follows:

> For *i*=1 to *N*:
>
> {

1.  For *t*=0 to 15:

> {
>
> }

1.  Initialize the five working variables, ***a***, ***b***, ***c***,
    > ***d***, and ***e***, with the (*i*-1)^st^ hash value:

2.  For *t*=0 to 79:

> {
>
> If then
>
> {
>
> }
>
> }

```cryptol
sha1_T_alt : [32] -> [8] -> [5][32] -> [32]
sha1_T_alt Ws t abcde = (ROTL 5 a) + (f t b c d) + e + (sha1_K @ t) + Ws
  where [a, b, c, d, e] = abcde

sha1_helper_alt : [16][32] -> [8] -> [6][32] -> ([16][32], [6][32])
sha1_helper_alt W t Tabcde = (W', [ T', a', b', c', d', e' ])
  where [T, a, b, c, d, e] = Tabcde
        MASK = 0x0000000f
        s    = ((zero:[24]) # t) && MASK
        Ws   = if t >= 16 then 
                 ROTL 1 (W @ ((s + 13) && MASK) ^
                         W @ ((s +  8) && MASK) ^
                         W @ ((s +  2) && MASK) ^
                         W @ s)
               else W @ t
        W'   = [ if s == i then Ws else W @ i | i <- [ 0 .. 15 ] ]
        T'   = sha1_T_alt Ws t [a', b', c', d', e']
        e'   = d
        d'   = c
        c'   = ROTL 30 b
        b'   = a
        a'   = T
```

```cryptol
sha1_block_alt : [16][32] -> [5][32] -> [5][32]
sha1_block_alt Mblock abcde = drop`{1} (WTabcdes ! 0).1
  where W        = Mblock
        Tabcde0  = [sha1_T_alt (W @ 0) 0 abcde] # abcde
        WTabcdes = [ (W, Tabcde0) ] # 
                   [ sha1_helper_alt Wt (t+1) Tabcde
                       where (Wt, Tabcde) = WTabcdes @ t 
                     | t <- [ 0 .. 79 ] ]

property sha1_block_alt_equiv Mblock H =
  sha1_block Mblock H == sha1_block_alt Mblock H
```

1.  Compute the *i*^th^ intermediate hash value *H*^(*i*)^:

```cryptol
sha1_Hblock_alt : [5][32] -> [512] -> [5][32]
sha1_Hblock_alt H Mblock = sha1_H H (sha1_block_alt (split Mblock) H)

property sha1_Hblock_alt_equiv Mblock H =
  sha1_Hblock Mblock H == sha1_Hblock_alt Mblock H
```

> }

After repeating steps one through four a total of *N* times (i.e., after
processing *M^(N)^*), the resulting 160-bit message digest of the
message, *M*, is

```cryptol
sha1parsed_alt : {blocks} (fin blocks) => [blocks][512] -> [160]
sha1parsed_alt Mparsed = join (Hs ! 0)
  where Hs = [sha1_H0] # [ sha1_Hblock_alt H Mblock | H <- Hs | Mblock <- Mparsed]

sha1_alt : {n} (width (8*n) <= 64) => [n][8] -> [160]
sha1_alt M = sha1parsed_alt (padparse512 (join M))

// (Can only check, instead of prove)
property sha1_alt_equiv M = sha1 M == sha1_alt M
```

6.2 SHA-256
-----------

SHA-256 may be used to hash a message, *M*, having a length of bits,
where . The algorithm uses 1) a message schedule of sixty-four 32-bit
words, 2) eight working variables of 32 bits each, and 3) a hash value
of eight 32-bit words. The final result of SHA-256 is a 256-bit message
digest.

The words of the message schedule are labeled *W*~0~, *W*~1~,…, *W*~63~.
The eight working variables are labeled ***a***, ***b***, ***c***,
***d***, ***e***, ***f***, ***g***, and ***h***. The words of the hash
value are labeled , which will hold the initial hash value, *H*^(0)^,
replaced by each successive intermediate hash value (after each message
block is processed), *H*^(*i*)^, and ending with the final hash value,
*H*^(*N*)^. SHA-256 also uses two temporary words, *T*~1~ and *T*~2~.

### 6.2.1 SHA-256 Preprocessing

1.  Set the initial hash value, *H*^(0)^, as specified in Sec. 5.3.3.

2.  The message is padded and parsed as specified in Section 5.

### 6.2.2 SHA-256 Hash Computation

The SHA-256 hash computation uses functions and constants previously
defined in Sec. 4.1.2 and Sec. 4.2.2, respectively. Addition (+) is
performed modulo 2^32^.

Each message block, *M*^(1)^, *M*^(2)^, …, *M*^(*N*)^, is processed in
order, using the following steps:

> For *i*=1 to *N*:
>
> {

1.  Prepare the message schedule, {*W~t~*}:

> =

```cryptol
sha256_W : [16][32] -> [64][32]
sha256_W Mblock = W
  where W = Mblock # [ s_1_256 (W @ (t -  2)) +
                                W @ (t -  7)  +
                       s_0_256 (W @ (t - 15)) +
                                W @ (t - 16) 
                       | t <- [ 16 .. 63 ] ]
```

1.  Initialize the eight working variables, ***a***, ***b***, ***c***,
    > ***d***, ***e***, ***f***, ***g***, and ***h***, with the
    > (*i*-1)^st^ hash value:

2.  For *t*=0 to 63:

> {
>
> }

```cryptol
sha256_T1 : [64][32] -> [8] -> [32] -> [32] -> [32] -> [32] -> [32]
sha256_T1 W t e f g h = h + (S_1_256 e) + (Ch e f g) + (K32 @ t) + (W @ t)

sha256_T2 : [32] -> [32] -> [32] -> [32]
sha256_T2 a b c = (S_0_256 a) + (Maj a b c)

sha256_helper : [16][32] -> [64][32] -> [8] -> [10][32] -> [10][32]
sha256_helper Mblock W t T1T2abcdefgh = [ T1', T2', a', b', c', d', e', f', g', h' ]
  where [T1, T2, a, b, c, d, e, f, g, h] = T1T2abcdefgh
        T1' = sha256_T1 W t e' f' g' h'
        T2' = sha256_T2 a' b' c'
        h'  = g
        g'  = f
        f'  = e
        e' = d + T1
        d' = c
        c' = b
        b' = a
        a' = T1 + T2
```

```cryptol
sha256_block : [16][32] -> [8][32] -> [8][32]
sha256_block Mblock abcdefgh = drop`{2}(T1T2abcdefghs ! 0)
  where W             = sha256_W Mblock
        sha256_h      = sha256_helper Mblock W
        T1T2abcdefgh0 = [sha256_T1 W 0 e f g h] # [sha256_T2 a b c] # abcdefgh
          where [a, b, c, d, e, f, g, h] = abcdefgh
        T1T2abcdefghs = [ T1T2abcdefgh0 ] # 
                        [ sha256_h (t+1) (T1T2abcdefghs @ t) 
                          | t <- [ 0 .. 63 ] ]
```

```cryptol
// Another (cleaner) specification of sha256_block processing
sha256_block' : [16][32] -> [8][32] -> [8][32]
sha256_block' Mblock abcdefgh = 
    [as@64, bs@64, cs@64, ds@64, es@64, fs@64, gs@64, hs@64]
  where
    [ a, b, c, d, e, f, g, h ] = abcdefgh 
    W  = sha256_W Mblock
    T1 = [ sha256_T1 W t e f g h | h <- hs | e <- es | f <- fs | g <- gs | t <- [ 0 .. 63 ] ]
    T2 = [ sha256_T2 a b c  | a <- as | b <- bs | c <- cs]
    hs = [h] # gs
    gs = [g] # fs
    fs = [f] # es
    es = [e] # [d + t1 | d <- ds | t1 <- T1]
    ds = [d] # cs
    cs = [c] # bs
    bs = [b] # as
    as = [a] # [t1 + t2 | t1 <- T1 | t2 <- T2]

property sha256_blocks_equiv Mblock H =
  sha256_block Mblock H == sha256_block' Mblock H 
```

1.  Compute the *i*^th^ intermediate hash value *H*^(*i*)^:

> }

```cryptol
sha256_H : [8][32] -> [8][32] -> [8][32]
sha256_H H abcdefgh = zipWith (+) abcdefgh H

sha256_Hblock : [8][32] -> [512] -> [8][32]
sha256_Hblock H Mblock = sha256_H H (sha256_block (split Mblock) H)

sha256_Hblock' : [8][32] -> [512] -> [8][32]
sha256_Hblock' H Mblock = sha256_H H (sha256_block' (split Mblock) H)

property sha256_Hblocks_equiv Mblock H =
  sha256_Hblock Mblock H == sha256_Hblock' Mblock H 
```

After repeating steps one through four a total of *N* times (i.e., after
processing *M^(N)^*), the resulting 256-bit message digest of the
message, *M*, is

```cryptol
sha256parsed : {blocks} (fin blocks) => [8][32] -> [blocks][512] -> [256]
sha256parsed H0 Mparsed = join (Hs ! 0)
  where Hs = [H0] # [ sha256_Hblock H Mblock | H <- Hs | Mblock <- Mparsed]

sha256 : {n} (width (8*n) <= 64) => [n][8] -> [256]
sha256 M = sha256parsed sha256_H0 (padparse512 (join M))
```

6.3 SHA-224
-----------

SHA-224 may be used to hash a message, *M,* having a length of bits,
where . The function is defined in the exact same manner as SHA-256
(Section 6.2), with the following two exceptions:

> 1\. The initial hash value, *H*^(0)^, shall be set as specified in Sec.
> 5.3.2; and

2\. The 224-bit message digest is obtained by truncating the final hash
value, *H*(*N)*, to its left-most 224 bits:

```cryptol
sha224 : {n} (width (8*n) <= 64) => [n][8] -> [224]
sha224 M = take`{224} (sha256parsed sha224_H0 (padparse512 (join M)))
```

6.4 SHA-512
-----------

SHA-512 may be used to hash a message, *M*, having a length of bits,
where . The algorithm uses 1) a message schedule of eighty 64-bit words,
2) eight working variables of 64 bits each, and 3) a hash value of eight
64-bit words. The final result of SHA-512 is a 512-bit message digest.

The words of the message schedule are labeled *W*~0~, *W*~1~,…, *W*~79~.
The eight working variables are labeled ***a***, ***b***, ***c***,
***d***, ***e***, ***f***, ***g***, and ***h***. The words of the hash
value are labeled , which will hold the initial hash value, *H*^(0)^,
replaced by each successive intermediate hash value (after each message
block is processed), *H*^(*i*)^, and ending with the final hash value,
*H*^(*N*)^. SHA-512 also uses two temporary words, *T*~1~ and *T*~2~.

### 6.4.1 SHA-512 Preprocessing

1.  Set the initial hash value, *H*^(0)^, as specified in Sec. 5.3.5.

2.  The message is padded and parsed as specified in Section 5.

### 6.4.2 SHA-512 Hash Computation

The SHA-512 hash computation uses functions and constants previously
defined in Sec. 4.1.3 and Sec. 4.2.3, respectively. Addition (+) is
performed modulo 2^64^.

Each message block, *M*^(1)^, *M*^(2)^, …, *M*^(*N*)^, is processed in
order, using the following steps:

> For *i*=1 to *N*:
>
> {

1.  Prepare the message schedule, {*W~t~*}:

> =

```cryptol
sha512_W : [16][64] -> [80][64]
sha512_W Mblock = W
  where W = Mblock # [ s_1_512 (W @ (t -  2)) +
                                W @ (t -  7)  +
                       s_0_512 (W @ (t - 15)) +
                                W @ (t - 16) 
                       | t <- [ 16 .. 79 ] ]
```

1.  Initialize the eight working variables, ***a***, ***b***, ***c***,
    > ***d***, ***e***, ***f***, ***g***, and ***h***, with the
    > (*i*-1)^st^ hash value:

2.  For *t*=0 to 79:

> {
>
> }

```cryptol
sha512_T1 : [80][64] -> [8] -> [64] -> [64] -> [64] -> [64] -> [64]
sha512_T1 W t e f g h = h + (S_1_512 e) + (Ch e f g) + (K64 @ t) + (W @ t)

sha512_T2 : [64] -> [64] -> [64] -> [64]
sha512_T2 a b c = (S_0_512 a) + (Maj a b c)

sha512_helper : [16][64] -> [80][64] -> [8] -> [10][64] -> [10][64]
sha512_helper Mblock W t T1T2abcdefgh = [ T1', T2', a', b', c', d', e', f', g', h' ]
  where [T1, T2, a, b, c, d, e, f, g, h] = T1T2abcdefgh
        T1' = sha512_T1 W t e' f' g' h'
        T2' = sha512_T2 a' b' c'
        h'  = g
        g'  = f
        f'  = e
        e' = d + T1
        d' = c
        c' = b
        b' = a
        a' = T1 + T2
```

```cryptol
sha512_block : [16][64] -> [8][64] -> [8][64]
sha512_block Mblock abcdefgh = drop`{2}(T1T2abcdefghs ! 0)
  where W             = sha512_W Mblock
        sha512_h      = sha512_helper Mblock W
        T1T2abcdefgh0 = [sha512_T1 W 0 e f g h] # [sha512_T2 a b c] # abcdefgh
          where [a, b, c, d, e, f, g, h] = abcdefgh
        T1T2abcdefghs = [ T1T2abcdefgh0 ] # 
                        [ sha512_h (t+1) (T1T2abcdefghs @ t) 
                          | t <- [ 0 .. 79 ] ]
```

```cryptol
// Another (cleaner) specification of sha256_block processing
sha512_block' : [16][64] -> [8][64] -> [8][64]
sha512_block' Mblock abcdefgh = 
    [as@80, bs@80, cs@80, ds@80, es@80, fs@80, gs@80, hs@80]
  where
    [ a, b, c, d, e, f, g, h ] = abcdefgh 
    W  = sha512_W Mblock
    T1 = [ sha512_T1 W t e f g h | h <- hs | e <- es | f <- fs | g <- gs | t <- [ 0 .. 79 ] ]
    T2 = [ sha512_T2 a b c  | a <- as | b <- bs | c <- cs]
    hs = [h] # gs
    gs = [g] # fs
    fs = [f] # es
    es = [e] # [d + t1 | d <- ds | t1 <- T1]
    ds = [d] # cs
    cs = [c] # bs
    bs = [b] # as
    as = [a] # [t1 + t2 | t1 <- T1 | t2 <- T2]

property sha512_blocks_equiv Mblock H =
  sha512_block Mblock H == sha512_block' Mblock H 
```

1.  Compute the *i*^th^ intermediate hash value *H*^(*i*)^:

> }

```cryptol
sha512_H : [8][64] -> [8][64] -> [8][64]
sha512_H H abcdefgh = zipWith (+) abcdefgh H

sha512_Hblock : [8][64] -> [1024] -> [8][64]
sha512_Hblock H Mblock = sha512_H H (sha512_block (split Mblock) H)

sha512_Hblock' : [8][64] -> [1024] -> [8][64]
sha512_Hblock' H Mblock = sha512_H H (sha512_block' (split Mblock) H)

property sha512_Hblocks_equiv Mblock H =
  sha512_Hblock Mblock H == sha512_Hblock' Mblock H 
```

After repeating steps one through four a total of *N* times (i.e., after
processing *M^(N)^*), the resulting 512-bit message digest of the
message, *M*, is

```cryptol
sha512parsed : {blocks} (fin blocks) => [8][64] -> [blocks][1024] -> [512]
sha512parsed H0 Mparsed = join (Hs ! 0)
  where Hs = [H0] # [ sha512_Hblock H Mblock | H <- Hs | Mblock <- Mparsed]

sha512t : {n} (width (8*n) <= 64) => [n][8] -> [8][64] -> [512]
sha512t M IV = sha512parsed IV (padparse1024 (join M))

sha512 : {n} (width (8*n) <= 64) => [n][8] -> [512]
sha512 M = sha512t M sha512_H0
```

6.5 SHA-384
-----------

SHA-384 may be used to hash a message, *M*, having a length of bits,
where. The algorithm is defined in the exact same manner as SHA-512
(Sec. 6.4), with the following two exceptions:

1.  The initial hash value, *H*^(0)^, shall be set as specified in Sec.
    > 5.3.4; and

2.  The 384-bit message digest is obtained by truncating the final hash
    > value, *H*^(*N*)^, to its left-most 384 bits:

```cryptol
sha384 : {n} (width (8*n) <= 64) => [n][8] -> [384]
sha384 M = take`{384} (sha512parsed sha384_H0 (padparse1024 (join M)))
```

6.6 SHA-512/224
---------------

SHA-512/224 may be used to hash a message, *M*, having a length of bits,
where. The algorithm is defined in the exact same manner as SHA-512
(Sec. 6.4), with the following two exceptions:

1.  The initial hash value, *H*^(0)^, shall be set as specified in Sec.
    5.3.6.1; and

2.  The 224-bit message digest is obtained by truncating the final hash
    > value, *H*^(*N*)^, to its left-most 224 bits.

```cryptol
sha512_224 : {n} (width (8*n) <= 64) => [n][8] -> [224]
sha512_224 M = take`{224} (sha512parsed sha512_224_H0 (padparse1024 (join M)))
```

6.7 SHA-512/256
---------------

SHA-512/256 may be used to hash a message, *M*, having a length of bits,
where. The algorithm is defined in the exact same manner as SHA-512
(Sec. 6.4), with the following two exceptions:

1.  The initial hash value, *H*^(0)^, shall be set as specified in Sec.
    5.3.6.2; and

2.  The 256-bit message digest is obtained by truncating the final hash
    value, *H*^(*N*)^, to its left-most 256 bits.


```cryptol
sha512_256 : {n} (width (8*n) <= 64) => [n][8] -> [256]
sha512_256 M = take`{256} (sha512parsed sha512_256_H0 (padparse1024 (join M)))
```

7. TRUNCATION OF A MESSAGE DIGEST
=================================

Some application may require a hash function with a message digest
length different than those provided by the hash functions in this
Standard. In such cases, a truncated message digest may be used, whereby
a hash function with a larger message digest length is applied to the
data to be hashed, and the resulting message digest is truncated by
selecting an appropriate number of the leftmost bits. For guidelines on
choosing the length of the truncated message digest and information
about its security implications for the cryptographic application that
uses it, see SP 800-107 \[SP 800-107\].

**\
**APPENDIX A: Additional Information
====================================

A.1 Security of the Secure Hash Algorithms
------------------------------------------

The security of the five hash algorithms, SHA-1, SHA-224, SHA-256,
SHA-384, SHA-512, SHA-512/224 and SHA-512/256 is discussed in \[SP
800-107\].

A.2 Implementation Notes 
-------------------------

Examples of SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, SHA-512/224 and
SHA-512/256 are available at
<http://csrc.nist.gov/groups/ST/toolkit/examples.html>.

A.3 Object Identifiers
----------------------

Object identifiers (OIDs) for the SHA-1, SHA-224, SHA-256, SHA-384,
SHA-512, SHA-512/224 and SHA-512/256 algorithms are posted at
<http://csrc.nist.gov/groups/ST/crypto_apps_infra/csor/algorithms.html>.

\
APPENDIX B: REFERENCES
======================

\[FIPS 180-3\] NIST, Federal Information Processing Standards
Publication 180-3, *Secure Hash Standards (SHS)*, October 2008.

\[SP 800-57\] NIST Special Publication (SP) 800-57, Part 1,
*Recommendation for Key Management: General*, (Draft) May 2011.

\[SP 800-107\] NIST Special Publication (SP) 800-107, *Recommendation
for Applications Using Approved Hash Algorithms*, (Revised), (Draft)
September 2011.

APPENDIX C: Technical Changes from FIPS 180-3
=============================================

1.  In FIPS 180-3, padding was inserted before hash computation begins.
    FIPS 140-4 removed this restriction. Padding can be inserted before
    hash computation begins or at any other time during the hash
    computation prior to processing the message block(s) containing
    the padding.

2.  FIPS 180-4 adds two additional algorithms: SHA-512/224 and
    SHA-512/256 to the Standard and the method for determining the
    initial value for SHA-512 / *t* for a given value of *t*.

\
<span id="_Toc261698857" class="anchor"><span id="_Toc261699161" class="anchor"></span></span>ERRATUM
=====================================================================================================

The following change has been incorporated into FIPS 180-4, as of the
date indicated in the table.

  **DATE**   **TYPE**    **CHANGE**                         **PAGE NUMBER**
  ---------- ----------- ---------------------------------- --------------------------------
  5/9/2014   Editorial   Change “*t* &lt; 79” to “*t* 79”   Page 10, Section 4.1.1, Line 1


```cryptol
gen_sha1_Hblock : [5][32] -> [64][8] -> [5][32]
gen_sha1_Hblock H Mblock = sha1_Hblock H (join Mblock)

gen_sha1_Hblock' : [5][32] -> [64][8] -> [5][32]
gen_sha1_Hblock' H Mblock = sha1_Hblock' H (join Mblock)

gen_sha1_Hblock_alt : [5][32] -> [64][8] -> [5][32]
gen_sha1_Hblock_alt H Mblock = sha1_Hblock_alt H (join Mblock)

gen_sha256_Hblock : [8][32] -> [64][8] -> [8][32]
gen_sha256_Hblock H Mblock = sha256_Hblock H (join Mblock)

gen_sha256_Hblock' : [8][32] -> [64][8] -> [8][32]
gen_sha256_Hblock' H Mblock = sha256_Hblock' H (join Mblock)

gen_sha512_Hblock : [8][64] -> [128][8] -> [8][64]
gen_sha512_Hblock H Mblock = sha512_Hblock H (join Mblock)

gen_sha512_Hblock' : [8][64] -> [128][8] -> [8][64]
gen_sha512_Hblock' H Mblock = sha512_Hblock' H (join Mblock)
```