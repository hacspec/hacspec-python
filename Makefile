#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

SPECS=poly1305 chacha20 aead_chacha20poly1305 sha2 sha3 \
curve25519 ed25519 p256 curve448 aes gf128 aead_aes128gcm
SLOW_SPECS=wots kyber frodo
FAILING_SPECS=argon2i blake2
BROKEN_SPECS=vrf rsapss

.PHONY: test $(SPECS) all

all: run check test

run: $(SPECS) $(FAILING_SPECS)
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
