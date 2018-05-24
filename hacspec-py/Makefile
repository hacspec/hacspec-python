#To run these specs in Python you need to install Python >= 3.6
PYTHON?=python3.6

# CHECK_TEST_FILES: check_lists.py

.PHONY: test all speclib_test build publish

all: test

test: speclib_test check check_fail

speclib_test:
	$(PYTHON) hacspec/tests/speclib_test.py
	$(PYTHON) hacspec/tests/check_test.py

check:
	hacspec-check hacspec/tests/check.py

check_fail:
	if hacspec-check hacspec/tests/check_fail.py; then \
		echo check_fail should have failed!; \
		exit 1; \
	else \
		echo check_fail failed as expected; \
	fi

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
