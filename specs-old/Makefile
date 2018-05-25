#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

SPECS=poly1305 chacha20 aead_chacha20poly1305 sha2 keccak \
curve25519 ed25519 p256 curve448 rsapss aes aead_aes128gcm argon2i 
OTHER_SPECS=wots
# vrf and blake2 are currently broken

.PHONY: test $(SPECS) all

all: run check 

run: $(addsuffix _test.py, $(SPECS))
	$(PYTHON) -O $^

check: $(addsuffix -check, $(SPECS)) $(SPECS)

$(SPECS):
	$(PYTHON) -O $@_test.py

%-check: %.py
	hacspec-check $<
