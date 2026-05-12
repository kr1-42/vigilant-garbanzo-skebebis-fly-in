NAME = fly-in.py
FILE = .base.txt
PYTHON := ./venv/bin/python3

MAP_DIR = maps/files
MAPS = $(wildcard $(MAP_DIR)/*.txt)

SHELL := /bin/bash

all: run

run: $(NAME)
	@$(PYTHON) $(NAME) $(FILE)

test: $(NAME)
	source ./venv/bin/activate
	@for file in $(MAPS); do \
		echo "==================================="; \
		echo "Running with $$file"; \
		echo "==================================="; \
		$(PYTHON) $(NAME) $$file; \
		echo ""; \
	done


install:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict


