FILES=speclib.py poly1305.py ctr.py chacha20.py aead_chacha20poly1305.py sha2.py

#To run these specs in Python you need to install Python >= 3.6
PYTHON=python3.6

#To typecheck these specs you need to install mypy
MYPY=mypy

all: typecheck test

typecheck:
	$(MYPY) $(FILES)

test:
	$(PYTHON) poly1305_test.py
	$(PYTHON) chacha20_test.py
	$(PYTHON) aead_chacha20poly1305_test.py
	$(PYTHON) sha2_test.py

