NAME = fly-in.py
FILE = .base.txt

all: $(NAME)

$(NAME):
	@python3 $(NAME) $(FILE)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict


