#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

# CHECK_TEST_FILES: check_lists.py

.PHONY: test all speclib_test build publish

all: test build publish

test: speclib_test check_test check_fail_test

speclib_test:
	$(PYTHON) hacspec/tests/speclib_test.py
	$(PYTHON) hacspec/tests/check_test_run.py

check_test:
	hacspec-check hacspec/tests/check.py

check_fail_test:
	if hacspec-check hacspec/tests/check_fail.py; then \
		echo check_fail should have failed!; \
		exit 1; \
	else \
		echo check_fail failed as expected; \
	fi

copy: clean
	cp ../lib/speclib/check.py .
	cp ../lib/speclib/speclib.py .

build: copy
	$(PYTHON) setup.py sdist

install: copy
	pip install .

publish: build
	twine upload dist\*

clean:
	rm -rf dist check.py speclib.py
	rm -rf hacspec.egg-info
	rm -rf MANIFEST
	rm -rf hacspec/__pycache__
