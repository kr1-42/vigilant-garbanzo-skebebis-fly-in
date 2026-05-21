from ..cls_data import Hub, Connection, Data, VALID_ZONE_TYPES
from typing import TextIO


def _parse_metadata(metadata_str: str) -> dict[str, str]:
    """Parse metadata from a bracketed string like
    "[zone=normal color=red max_drones=2]"
    Returns a dict of key-value pairs. Raises ValueError on invalid format."""
    result: dict[str, str] = {}
    metadata_str = metadata_str.strip()
    if not metadata_str:
        return result
    metadata_str = metadata_str.removeprefix("[").removesuffix("]").strip()
    if not metadata_str:
        return result
    for part in metadata_str.split():
        if "=" not in part:
            raise ValueError(
                f"invalid metadata format: '{part}' (expected key=value)"
            )
        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise ValueError(
                f"invalid metadata: empty key or value in '{part}'"
            )
        result[key] = value
    return result


def parse_text(text: list[str]) -> Data:
    """
    Parse drone network configuration from text format.
    Performs comprehensive validation at parse-time and post-parse.

    Raises ValueError with detailed line information on parsing errors.

    @param text: List of strings containing the configuration
    @returns: A Data object representing the parsed configuration
    @raises ValueError: On any validation error with line number and context
    """
    nb_drones: int | None = None
    hubs: list[Hub] = []
    connections: list[Connection] = []
    line_num = 0
    hub_names_seen: set[str] = set()

    for raw in text:
        line_num += 1
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        try:
            if line.startswith("nb_drones:"):
                value_str = line.split(":", 1)[1].strip()
                if not value_str:
                    raise ValueError("nb_drones value is missing")
                try:
                    nb_drones = int(value_str)
                except ValueError:
                    raise ValueError(
                        f"nb_drones must be an integer, got '{value_str}'"
                    )
                if nb_drones <= 0:
                    raise ValueError(
                        f"nb_drones must be positive, got {nb_drones}"
                    )
                continue

            if line.startswith(("start_hub:", "hub:", "end_hub:")):
                kind, rest = line.split(":", 1)
                parts = rest.strip().split(maxsplit=3)
                if len(parts) < 3:
                    raise ValueError(
                        f"expected at 3 parts (name x y), got {len(parts)}"
                    )

                name, x_str, y_str = parts[0], parts[1], parts[2]
                metadata_str = parts[3] if len(parts) > 3 else ""

                # Validate hub name
                if not name or name.startswith("-"):
                    raise ValueError(f"invalid hub name: '{name}'")
                if name in hub_names_seen:
                    raise ValueError(f"duplicate hub name: '{name}'")
                hub_names_seen.add(name)

                # Parse and validate coordinates
                try:
                    x = int(x_str)
                    y = int(y_str)
                except ValueError:
                    raise ValueError(
                        f"invalid coordinates: x='{x_str}', y='{y_str}'",
                        " (expected integers)",
                    )

                if not (-1e6 <= x <= 1e6 and -1e6 <= y <= 1e6):
                    raise ValueError(
                        f"coordinates out of reasonable bounds: x={x}, y={y}"
                    )

                # Parse and validate metadata
                metadata = _parse_metadata(metadata_str)

                # Validate and get zone
                zone = metadata.get("zone", "normal")
                if zone not in VALID_ZONE_TYPES:
                    raise ValueError(
                        f"invalid zone type '{zone}'.",
                        f" Must be one of: {VALID_ZONE_TYPES}",
                    )

                # Validate and get max_drones
                try:
                    max_drones = int(metadata.get("max_drones", "1"))
                except ValueError:
                    raise ValueError(
                        f"invalid max_drones value: {metadata['max_drones']}",
                        " (expected positive integer)",
                    )
                if max_drones <= 0:
                    raise ValueError(
                        f"max_drones must be positive, got {max_drones}"
                    )

                # Get optional color
                color = metadata.get("color", None)

                # Create hub
                hub = Hub(
                    kind=kind,
                    name=name,
                    x=x,
                    y=y,
                    zone=zone,
                    max_drones=max_drones,
                    color=color,
                )
                hubs.append(hub)
                continue

            if line.startswith("connection:"):
                rest = line.split(":", 1)[1].strip()
                if not rest:
                    raise ValueError("connection definition is missing")

                # Split connection and metadata
                if "[" in rest:
                    conn_str, metadata_str = rest.split("[", 1)
                    metadata_str = "[" + metadata_str
                else:
                    conn_str = rest
                    metadata_str = ""

                conn_str = conn_str.strip()

                # Parse connection
                if "-" not in conn_str:
                    raise ValueError(
                        f"invalid connection format: '{conn_str}'",
                        " (expected: hub_a-hub_b)",
                    )

                parts = conn_str.split("-", 1)
                hub_a, hub_b = parts[0].strip(), parts[1].strip()

                if not hub_a or not hub_b:
                    raise ValueError(
                        f"invalid connection: empty hub names in '{conn_str}'"
                    )
                if hub_a == hub_b:
                    raise ValueError(
                        f"self-loop connection not allowed: '{hub_a}-{hub_b}'"
                    )

                # Parse and validate metadata
                metadata = _parse_metadata(metadata_str)

                try:
                    max_link_capacity = int(
                        metadata.get("max_link_capacity", "1")
                    )
                except ValueError:
                    raise ValueError(
                        "invalid max_link_capacity: ",
                        f"'{metadata['max_link_capacity']}'",
                        " (expected positive integer)",
                    )
                if max_link_capacity <= 0:
                    raise ValueError(
                        "max_link_capacity must be positive,",
                        f" got {max_link_capacity}",
                    )

                conn = Connection(
                    hub_a=hub_a,
                    hub_b=hub_b,
                    max_link_capacity=max_link_capacity,
                )
                connections.append(conn)
                continue

            # Unknown line format
            raise ValueError(f"unrecognized line format: '{line}'")

        except ValueError as e:
            raise ValueError(f"Line {line_num}: {str(e)}")

    # Final validation of required fields
    if nb_drones is None:
        raise ValueError("missing nb_drones")

    # Validate all referenced hubs exist before creating Data
    for conn in connections:
        if conn.hub_a not in hub_names_seen:
            raise ValueError(
                f"connection references undefined hub: '{conn.hub_a}'"
            )
        if conn.hub_b not in hub_names_seen:
            raise ValueError(
                f"connection references undefined hub: '{conn.hub_b}'"
            )

    # Create and return Data object (validates start/end hub)
    return Data.from_parts(
        nb_drones=nb_drones, hubs=hubs, connections=connections
    )


def parse_file(file: TextIO) -> list[str]:
    """
    Parse the file and return a list of non-empty, non-comment lines.
    Preserves line order and handles various whitespace formats.

    @param file: A file-like object to read from
    @returns: A list of configuration line strings
    @raises ValueError: If there's an error reading the file
    """
    data: list[str] = []
    try:
        for line in file:
            # Strip leading/trailing whitespace
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                data.append(line)
    except IOError as e:
        raise ValueError(f"Error reading configuration file: {e}")
    return data
