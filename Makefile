#To run these specs in Python you need to install Python >= 3.6.4
PYTHON?=python3

# hacspecs passing compiler checks
FINISHED_SPECS=poly1305 chacha20 aead_chacha20poly1305 curve25519 curve448 \
               aes gf128 aead_aes128gcm

# hacspecs that pass all python checks and can be used in any make target.
SPECS=$(FINISHED_SPECS) sha2 sha3 ed25519 p256 rsapss blake2

# Don't use these in test. They take too long.
SLOW_SPECS=wots kyber kyber2

# Like SLOW_SPECS and they fail the spec checker.
SLOW_SPECS_FAILING_SPECHECK=frodo argon2i

# These specs run just fine but don't pass the spec checker.
SPECS_FAILING_SPECHECK=

# These specs are broken or work in progress.
BROKEN_SPECS=vrf xmss

.PHONY: test $(SPECS) all compiler

# Python targets. These only require Python.
all: run check test

run: $(SPECS) $(SPECS_FAILING_SPECHECK) $(SLOW_SPECS)
test: $(addsuffix -test, $(SPECS) $(SPECS_FAILING_SPECHECK))
check: $(addsuffix -check, $(SPECS) $(SLOW_SPECS))

$(SPECS) $(SLOW_SPECS) $(SPECS_FAILING_SPECHECK):
	PYTHONPATH=. $(PYTHON) -O tests/$@_test.py

%-check: specs/%.py
	PYTHONPATH=. $(PYTHON) lib/check.py $<
%-test: tests/%_test.py
	PYTHONPATH=. $(PYTHON) $<

# Compiler targets
# NOTE that this requires OCAML.
compiler: checker fstar parse
checker:
	make -C compiler
fstar:
	make -C compiler
parse: $(addsuffix -parse, $(FINISHED_SPECS))
%-parse: specs/%.py
	compiler/checker.native $<

# Documentation targets
# NOTE that this requires hugo (https://gohugo.io)
website:
	cd doc/website/ && hugo
	cd doc/poly-slides && hugo
website-dev:
	cd doc/website/ && hugo serve -D
website-slides-dev:
	cd doc/poly-slides && hugo serve -D

python-docs:
	make -C build/ docs
