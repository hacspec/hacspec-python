.PHONY: all fstar

HACL_HOME?=../../hacl-star
PYTHON?=python3.6

# argon2i.fst aead_chacha20poly1305.fst look pretty broken.
FSPECS=chacha20.fst poly1305.fst sha2.fst curve25519.fst ed25519.fst blake2.fst
SPECS=$(FSPECS)

all: fstar

fstar: $(SPECS)

%.fst: ../specs/%.py
	$(PYTHON) hacspec_to_fstar.py $< > fstar/$@

typecheck: $(addsuffix -verify, $(addprefix fstar/, $(SPECS)))

%-verify: %
	fstar.exe --include $(HACL_HOME)/specs/lib --include fstar/ $<

clean:
	rm -f $(addprefix fstar/, $(SPECS)) *~ *.hints *.checked
