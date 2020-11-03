TESTARGS := ${testargs}

SHELL := /bin/bash

.PHONY: docs

all: format mypy test

format:
	venv/bin/black dwork/
	venv/bin/black examples/
mypy:
	venv/bin/mypy dwork/
	venv/bin/mypy dwork_tests/
test:
	venv/bin/py.test dwork_tests ${TESTARGS}

setup: venv requirements

docs-setup: venv docs-requirements

teardown:
	rm -rf venv
	rm -rf docs/build/*

venv:
	virtualenv --python python3 venv

docs-requirements:
	venv/bin/pip install -r docs/requirements.txt

requirements:
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r requirements-optional.txt
	venv/bin/pip install -r requirements-test.txt

update:
	venv/bin/pip install pur
	venv/bin/pur -r requirements.txt
	venv/bin/pur -r requirements-test.txt

release: venv
	venv/bin/pip install twine
	venv/bin/python setup.py sdist
	venv/bin/twine upload --skip-existing dist/* -u ${TWINE_USER} -p ${TWINE_PASSWORD}
