The specs are currently written in a typed subset of python.
There's a library `speclib.py` that provides common functionality that can be used in any specification written in hacspec.

```
Types t ::= int | uint32 | uint64 | uint128 | Tuple[t1,...,tn] | array[t] | bytes
```

```
Expressions e ::= x                    (variables)
            |  0x... | n               (integer constants in hex or decimal)
            |  e binop e               (operators on int and uintN)

    uintN
            |  uintN(e)                (convert int to uintN)
            |  uintN.to_int(e)e        (convert uintN to int)
            |  uintN.from_bytes_le     (bytes to uintN)
            |  uintN.to_bytes_le       (uintN to bytes)

    array[T]
            |  array([e0,...,en])      (make array)
            |  array.copy(e)           (copy array)
            |  array.create(d,len)     (make array of len ds)
            |  array(x for x in e)     (make array from generator)
            |  array.len(a)            (get length of array)
            |  array.uint32s_from_bytes_le(b) (create array[uint32] from array[bytes])
            |  array.uint32s_to_bytes_le(ints) (create bytes from array[uint32])
            |  array.concat_bytes(blocks) (convert array[bytes] to bytes)
            |  array.split_bytes(a,blocksize) (convert bytes into array[bytes] with blocksize)
	    |  array.zip(a1,a2)	
            |  e[i]                    (array access)
            |  e[i:j]                  (array slice)
```

```
Statements s ::= x : t = e            (variable declaration)
           | def f(x1:t1,...,xn:tn) -> t : s (function declaration)
	   | x = e            (assignment)
           | x[i] = e             (array update)
           | x[i:j] = e           (array slice update)
           | return e             (return)
           | if e: s else: s      (conditional)
           | for (s; e; s) \n s   (for loop)
           | s \n s               (sequential composition)
           | from x import x1,x2,...,xn (import from module)
```

Test vectors are define in [JSON](http://json-schema.org/specification.html) following some schema.

MAC test vector scheme
```
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "input_len": {
        "type": "string"
      },
      "input": {
        "type": "string"
      },
      "key": {
        "type": "string"
      },
      "tag": {
        "type": "string"
      }
    },
    "required": [
      "input_len",
      "input",
      "key",
      "tag"
    ]
  },
  "maxProperties": 4
}
```
