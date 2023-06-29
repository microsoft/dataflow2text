SHELL = /bin/bash
SOURCE_DIR = src
TESTS_DIR = tests
SOURCE_AND_TESTS_DIRS = $(SOURCE_DIR) $(TESTS_DIR)
# Each folder in the the source/tests directory is a python package.
# Cannot use the GNU find because we may accidentally include cache directories (e.g., `__pycache__`, `.mypy_cache`, `.pytest_cache`).
PYTHON_PACKAGE_NAMES = src/dataflow2text src/pylint_dataflow2text src/dataflow2text_domains
PYTHON_PACKAGE_NAMES += tests/test_dataflow2text

.PHONY: all format format-check pylint mypy test git-status

all: format-check pylint mypy

# initializes repo
init:
	conda develop $(SOURCE_DIR)
	conda develop $(TESTS_DIR)

# sort imports and auto-format python code
format:
	isort $(SOURCE_AND_TESTS_DIRS)
	black -t py310 $(SOURCE_AND_TESTS_DIRS)

format-check:
	@(isort --check-only $(SOURCE_AND_TESTS_DIRS)) && (black -t py310 --check $(SOURCE_AND_TESTS_DIRS)) || (echo "run \"make format\" to format the code"; exit 1)

pylint:
	pylint $(PYTHON_PACKAGE_NAMES)

mypy:
	mypy --show-error-codes $(SOURCE_AND_TESTS_DIRS)

test:
	python -m pytest -n auto --durations=0 $(TESTS_DIR)
