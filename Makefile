NAME = fly-in.py
FILE = .base.txt

all: run

run: $(NAME)
	@python3 $(NAME) $(FILE)

run-all: $(NAME)
	@python3 $(NAME) maps/easy/01_linear_path.txt
	@python3 $(NAME) maps/easy/02_simple_fork.txt
	@python3 $(NAME) maps/hard/01_maze_nightmare.txt
	@python3 $(NAME) maps/hard/02_capacity_hell.txt
	@python3 $(NAME) maps/easy/03_basic_capacity.txt
	@python3 $(NAME) maps/hard/03_ultimate_challenge.txt
	@python3 $(NAME) maps/medium/01_dead_end_trap.txt
	@python3 $(NAME) maps/medium/02_circular_loop.txt
	@python3 $(NAME) maps/medium/03_priority_puzzle.txt

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict


