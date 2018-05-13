#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

SPECS=poly1305 chacha20 aead_chacha20poly1305 sha2 keccak \
argon2i curve25519 ed25519 p256 curve448 rsapss wots aes aead_aes128gcm
# vrf and blake2 are currently broken

.PHONY: test $(SPECS) all

all: check test

test: $(SPECS)
check: $(addsuffix -check, $(SPECS))

$(SPECS):
	$(PYTHON) $@_test.py

%-check: %.py
	hacspec-check $<
