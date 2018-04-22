#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

SPECS=speclib poly1305 chacha20 aead_chacha20poly1305 sha2 keccak blake2b \
blake2s argon2i curve25519 ed25519 p256 curve448 rsapss wots
# vrf is currently broken on this branch

.PHONY: test $(SPECS) all test

all: test

test: $(SPECS)

$(SPECS):
	@echo $@
	$(PYTHON) $@_test.py

check-specs:
	$(PYTHON) ../spec-checker/spec-checker.py blake2b.py
	$(PYTHON) ../spec-checker/spec-checker.py blake2s.py
	$(PYTHON) ../spec-checker/spec-checker.py chacha20.py
	$(PYTHON) ../spec-checker/spec-checker.py poly1305.py
	$(PYTHON) ../spec-checker/spec-checker.py aead_chacha20poly1305.py
	$(PYTHON) ../spec-checker/spec-checker.py sha2.py
	$(PYTHON) ../spec-checker/spec-checker.py keccak.py
	$(PYTHON) ../spec-checker/spec-checker.py curve25519.py
	$(PYTHON) ../spec-checker/spec-checker.py curve448.py
	$(PYTHON) ../spec-checker/spec-checker.py wots.py
	$(PYTHON) ../spec-checker/spec-checker.py argon2i.py
	$(PYTHON) ../spec-checker/spec-checker.py ed25519.py
	$(PYTHON) ../spec-checker/spec-checker.py vrf.py
	$(PYTHON) ../spec-checker/spec-checker.py rsapss.py
