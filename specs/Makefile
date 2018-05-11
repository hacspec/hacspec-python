#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

SPECS=speclib poly1305 chacha20 aead_chacha20poly1305 sha2 keccak \
argon2i curve25519 ed25519 p256 curve448 rsapss wots aes aead_aes128gcm
# vrf and blake2 are currently broken

.PHONY: test $(SPECS) all test

all: test


test: $(SPECS)

$(SPECS):
	@echo $@
	$(PYTHON) $@_test.py

# This isn't doing anything useful right now. It should be enabled again when
# the speck-checker does something.
# check-specs:
# 	$(PYTHON) ../spec-checker/python/spec_checker.py blake2.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py chacha20.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py poly1305.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py aead_chacha20poly1305.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py aes.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py gf128.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py aead_aes128gcm.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py sha2.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py keccak.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py curve25519.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py curve448.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py wots.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py argon2i.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py ed25519.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py vrf.py
# 	$(PYTHON) ../spec-checker/python/spec_checker.py rsapss.py
