#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

.PHONY: test all speclib_test build publish

all: test

test: speclib_test

speclib_test:
	$(PYTHON) hacspec/tests/speclib_test.py

build:
	rm -rf dist
	$(PYTHON) setup.py sdist

publish: build
	twine upload dist\*

clean:
	rm -rf dist
	rm -rf hacspec.egg-info
	rm -rf MANIFEST
	rm -rf hacspec/__pycache__
