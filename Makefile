NAME = src/fly-in.py
FILE = .base.txt
PYTHON := ./venv/bin/python3

MAP_DIR = maps/files
MAPS = $(wildcard $(MAP_DIR)/*.txt)

SHELL := /bin/bash

all: run

run:
	@if [  -f "venv/bin/python3" ]; then \
		source ./venv/bin/activate; \
	else \
		echo "Warning: venv not found, running venv"; \
		python3 -m venv venv; \
		source ./venv/bin/activate; \
		pip install -r requirements.txt; \
	fi
	@$(PYTHON) -m src $(FILE)

test:
	@source ./venv/bin/activate
	@for file in $(MAPS); do \
		echo "==================================="; \
		echo "Running with $$file"; \
		echo "==================================="; \
		$(PYTHON) -m src $$file; \
		echo ""; \
	done


install:
	@if [ ! -f "venv/bin/python3" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
	else \
		echo "venv already exists"; \
	fi
	@./venv/bin/pip install -r requirements.txt

lint:
	flake8 src/ fly-in.py
	mypy src fly-in.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 src/
	mypy . --strict


clean:
	rm -rf venv __pycache__ .mypy_cache .flake8_cache

