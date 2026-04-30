# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    file_parse.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: chrilomb <chrilomb@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/03/29 17:03:49 by chrilomb          #+#    #+#              #
#    Updated: 2026/04/30 17:44:25 by chrilomb         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from ..cls_data import Hub, Connection, Data
from typing import TextIO

def _parse_metadata(metadata_str: str) -> dict[str, str]:
    """Parse metadata from a bracketed string like "[zone=normal color=red max_drones=2]"
    Returns a dict of key-value pairs."""
    result: dict[str, str] = {}
    metadata_str = metadata_str.strip()
    if not metadata_str:
        return result
    metadata_str = metadata_str.removeprefix("[").removesuffix("]").strip()
    for part in metadata_str.split():
        if "=" not in part:
            raise ValueError(f"invalid metadata format: '{part}' (expected key=value)")
        key, value = part.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def parse_text(text: list[str]) -> Data:
    """
    Parse drone network configuration from text format.
    Raises ValueError with line information on parsing errors.
    @param text: List of strings containing the configuration
    @returns: A Data object representing the parsed configuration
    """
    nb_drones: int | None = None
    hubs: list[Hub] = []
    connections: list[Connection] = []
    line_num = 0
    for raw in text:
        line_num += 1
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            if line.startswith("nb_drones:"):
                nb_drones = int(line.split(":", 1)[1].strip())
                continue
            if line.startswith(("start_hub:", "hub:", "end_hub:")):
                kind, rest = line.split(":", 1)
                parts = rest.strip().split(maxsplit=3)
                if len(parts) < 3:
                    raise ValueError(f"expected at least 3 parts (name x y), got {len(parts)}")
                name, x_str, y_str = parts[0], parts[1], parts[2]
                metadata_str = parts[3] if len(parts) > 3 else ""
                try:
                    x = float(x_str)
                    y = float(y_str)
                except ValueError:
                    raise ValueError(f"invalid coordinates: x='{x_str}', y='{y_str}' (expected floats)")
                metadata = _parse_metadata(metadata_str)
                zone = metadata.get("zone", "normal")
                try:
                    max_drones = int(metadata.get("max_drones", "1"))
                except ValueError:
                    raise ValueError(f"invalid max_drones value: '{metadata['max_drones']}' (expected integer)")
                color = metadata.get("color", None)
                hub = Hub(kind=kind, name=name, x=x, y=y, zone=zone, max_drones=max_drones, color=color)
                hubs.append(hub)
                continue
            if line.startswith("connection:"):
                rest = line.split(":", 1)[1].strip()
                if "[" in rest:
                    conn_str, metadata_str = rest.split("[", 1)
                    metadata_str = "[" + metadata_str
                else:
                    conn_str = rest
                    metadata_str = ""
                conn_str = conn_str.strip()
                if "-" not in conn_str:
                    raise ValueError(f"invalid connection format: '{conn_str}' (expected format: hub_a-hub_b)")
                parts = conn_str.split("-", 1)
                hub_a, hub_b = parts[0].strip(), parts[1].strip()
                if not hub_a or not hub_b:
                    raise ValueError(f"invalid connection: empty hub names in '{conn_str}'")
                metadata = _parse_metadata(metadata_str)
                try:
                    max_link_capacity = int(metadata.get("max_link_capacity", "1"))
                except ValueError:
                    raise ValueError(f"invalid max_link_capacity value: '{metadata['max_link_capacity']}' (expected integer)")
                conn = Connection(hub_a=hub_a, hub_b=hub_b, max_link_capacity=max_link_capacity)
                connections.append(conn)
                continue
        except ValueError as e:
            raise ValueError(f"Line {line_num}: {str(e)}")
    if nb_drones is None:
        raise ValueError("nb_drones is required")
    return Data.from_parts(nb_drones=nb_drones, hubs=hubs, connections=connections)


def parse_file(file: TextIO) -> list:
    """ Parse the file and return a list of non-empty, non-comment lines.
    @param file: A file-like object to read from
    @returns data:list : A list of strings, each representing a meaningful line from the file
    """
    data = []
    for line in file:
        line = line.strip()
        if line and not line.startswith('#'):
            data.append(line)
    return data
