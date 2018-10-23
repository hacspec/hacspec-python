#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

# CHECK_TEST_FILES: check_lists.py

.PHONY: test all speclib_test build publish

all:

test: install speclib_test check_test check_fail_test

speclib_test:
	$(PYTHON) hacspec/tests/speclib_test.py
	$(PYTHON) hacspec/tests/check_test_run.py

check_test:
	hacspec-check hacspec/tests/check_test.py

check_fail_test:
	if hacspec-check hacspec/tests/check_test_fail.py; then \
		echo check_fail should have failed!; \
		exit 1; \
	else \
		echo check_fail failed as expected; \
	fi

copy: clean
	cp ../lib/check.py hacspec
	cp ../lib/speclib.py hacspec

build: copy
	$(PYTHON) setup.py sdist

install: build
	pip install .

publish: build
	twine upload dist/*

docs: copy
	sphinx-apidoc -o docs hacspec hacspec/check.py -f
	$(MAKE) -C docs html

clean:
	# pip uninstall hacspec
	rm -rf dist hacspec/check.py hacspec/speclib.py
	rm -rf hacspec.egg-info
	rm -rf MANIFEST
	rm -rf hacspec/__pycache__
	rm -rf hacspec/tests/__pycache__
	rm -rf docs/_build
	rm -rf __pycache__
