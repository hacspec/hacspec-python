#To run these specs in Python you need to install Python >= 3.6.4
PYTHON?=python3.6

# hacspecs that pass all checks and can be used in any make target.
SPECS=poly1305 chacha20 aead_chacha20poly1305 sha2 sha3 \
curve25519 ed25519 p256 curve448 aes gf128 aead_aes128gcm rsapss blake2

# Don't use these in test. They take too long.
SLOW_SPECS=wots kyber

# Like SLOW_SPECS and they fail the spec checker.
SLOW_SPECS_FAILING_SPECHECK=frodo argon2i

# These specs run just fine but don't pass the spec checker.
SPECS_FAILING_SPECHECK=

# These specs are broken or work in progress.
BROKEN_SPECS=vrf xmss

.PHONY: test $(SPECS) all

all: run check test

run: $(SPECS) $(SPECS_FAILING_SPECHECK) $(SLOW_SPECS)
test: $(addsuffix -test, $(SPECS) $(SPECS_FAILING_SPECHECK))
check: $(addsuffix -check, $(SPECS) $(SLOW_SPECS)) 
parse: $(addsuffix -parse, $(SPECS))

$(SPECS) $(SLOW_SPECS) $(SPECS_FAILING_SPECHECK):
	PYTHONPATH=. $(PYTHON) -O tests/$@_test.py

%-parse: specs/%.py
	cat $< | spec-checker-ocaml/main.native

%-check: specs/%.py
	PYTHONPATH=. $(PYTHON) lib/check.py $<
%-test: tests/%_test.py 
	PYTHONPATH=. $(PYTHON) $<
