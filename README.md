This project has been created as part of the 42 curriculum by *chrilomb* — login: chrilomb — 2025-12-12 17:18:40 — login: chrilomb — 2025-12-17 13:51:03 — login: chrilomb — 2025-12-17 13:53:50

# *fly-in*
[](https://github.com/kr1-42/vigilant-garbanzo-skebebis-fly-in/blob/master/README.md#fly-in)

## description
[](https://github.com/kr1-42/vigilant-garbanzo-skebebis-fly-in/blob/master/README.md#description)
*simulate drone traffic between hubs* with parsing, pathfinding, scheduling and visualization.

- Parse a map format with hubs, connections, and metadata.
- Validate map integrity (duplicates, missing hubs, invalid capacities, etc).
- Compute optimal route strategies (single path or multi-path).
- Simulate drone movement with zone costs and capacity constraints.
- Render the simulation in pygame with animated sprites and map selection.

## *instructions*
[](https://github.com/kr1-42/vigilant-garbanzo-skebebis-fly-in/blob/master/README.md#compilation)
in a terminal in the root of the project

```bash
make install
```

*this creates the virtual environment and installs all python dependencies*

## running the project
[](https://github.com/kr1-42/vigilant-garbanzo-skebebis-fly-in/blob/master/README.md#running-the-project)
*in a terminal*

```bash
make run FILE=maps/easy/01_linear_path.txt
```

*this starts the simulation with the selected map*

## to test the maps
[](https://github.com/kr1-42/vigilant-garbanzo-skebebis-fly-in/blob/master/README.md#to-test-the-maps)
*in a terminal*

```bash
make test
```

*this runs the simulation on all files in maps/files/*

## strict checks
[](https://github.com/kr1-42/vigilant-garbanzo-skebebis-fly-in/blob/master/README.md#strict-checks)
*in a terminal*

```bash
make lint-strict
```

*this runs flake8 and strict mypy over the project*

# *resources*
[](https://github.com/kr1-42/vigilant-garbanzo-skebebis-fly-in/blob/master/README.md#sources)
- *me*

# technicalities
[](https://github.com/kr1-42/vigilant-garbanzo-skebebis-fly-in/blob/master/README.md#technicalities)
*i used dataclasses and dedicated scheduler classes to keep parsing, simulation and rendering separated*

```python
@dataclass(frozen=True)
class Hub:
	kind: str
	name: str
	x: float
	y: float
	zone: str = "normal"
	max_drones: int = 1
	color: str | None = None
```

*i also use a drone state object plus schedulers for single-path and multi-path movement rules*

```python
@dataclass
class Drone:
	drone_id: int
	current_hub: str
	path_index: int
	turns_at_hub: int
	completed: bool = False
	initial_stagger: int = 0
```
