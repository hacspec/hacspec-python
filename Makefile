#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

SPECS=poly1305 chacha20 aead_chacha20poly1305 sha2 keccak \
curve25519 ed25519 p256 curve448 rsapss aes gf128 aead_aes128gcm blake2
SLOW_SPECS=wots kyber
FAILING_SPECS=argon2i
BROKEN_SPECS=vrf

.PHONY: test $(SPECS) all

all: run check test

run: $(SPECS) $(SLOW_SPECS) $(FAILING_SPECS)
test: $(addsuffix -test, $(SPECS))
check: $(addsuffix -check, $(SPECS)) 
parse: $(addsuffix -parse, $(SPECS))

$(SPECS) $(SLOW_SPECS) $(FAILING_SPECS):
	PYTHONPATH=. $(PYTHON) -O tests/$@_test.py

%-parse: specs/%.py
	cat $< | spec-checker-ocaml/main.native

%-check: specs/%.py
	PYTHONPATH=. $(PYTHON) lib/check.py $<
%-test: tests/%_test.py 
	PYTHONPATH=. $(PYTHON) $<
