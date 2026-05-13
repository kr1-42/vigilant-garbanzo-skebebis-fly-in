from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, cast

# Valid zone types as per specification
VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


@dataclass(frozen=True)
class Hub:
    """
    @wrapper dataclass(frozen=True) makes object immutable
    Represents a hub in the drone delivery network. The 'kind' field indicates
    whether it's a start hub, end hub, or regular hub.
    @param kind: "start_hub", "end_hub", or "hub"
    @param name: Unique identifier for the hub
    @param x: X-coordinate of the hub
    @param y: Y-coordinate of the hub
    @param zone: zone type (normal, blocked, restricted, priority)
    @param max_drones: Maximum number of drones that can be at the hub
    simultaneously (default is 1)
    @param color: Optional color for the hub
    """

    kind: str
    name: str
    x: float
    y: float
    zone: str = "normal"
    max_drones: int = 1
    color: str | None = None

    def __post_init__(self) -> None:
        if self.zone not in VALID_ZONE_TYPES:
            raise ValueError(
                f"invalid zone type '{self.zone}'.",
                f" Must be one of: {VALID_ZONE_TYPES}"
            )
        if self.max_drones <= 0:
            raise ValueError(
                f"max_drones must be positive, got {self.max_drones}"
            )


@dataclass(frozen=True)
class Connection:
    """
    Represents a bidirectional connection between two hubs.
    @param hub_a: Name of the first hub
    @param hub_b: Name of the second hub
    @param max_link_capacity: Maximum drones that can traverse
    this connection simultaneously (default is 1)
    """

    hub_a: str
    hub_b: str
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        if self.max_link_capacity <= 0:
            raise ValueError(
                "max_link_capacity must be",
                f" positive, got {self.max_link_capacity}"
            )

    def contains(self, hub_a: str, hub_b: str) -> bool:
        """Check if this connection links the two hubs (bidirectional)."""
        return (self.hub_a == hub_a and self.hub_b == hub_b) or (
            self.hub_a == hub_b and self.hub_b == hub_a
        )


@dataclass(frozen=True)
class Data:
    """Represents the entire configuration of the drone delivery network.
    @param nb_drones: Total number of drones available
    @param hubs: Dictionary mapping hub names to Hub objects
    @param connections: List of Connection objects
        representing the links between hubs
    @param start_hub: Name of the starting hub
    @param end_hub: Name of the ending hub"""

    nb_drones: int
    hubs: dict[str, Hub]
    connections: list[Connection]
    start_hub: str
    end_hub: str

    def __post_init__(self) -> None:
        """Validate the integrity of the data after
        initialization. Checks include:
        - nb_drones must be a positive integer
        - start_hub and end_hub must be defined in hubs
        - start_hub must be declared as a start_hub and end_hub as an end_hub
        - All connections must reference valid hubs and cannot be self-loops
        - No duplicate connections (bidirectional) are allowed
        """
        if not isinstance(self.nb_drones, int) or self.nb_drones <= 0:
            raise ValueError("nb_drones must be a positive integer")
        if self.start_hub not in self.hubs:
            raise ValueError(f"start_hub '{self.start_hub}' not defined")
        if self.end_hub not in self.hubs:
            raise ValueError(f"end_hub '{self.end_hub}' not defined")
        if self.hubs[self.start_hub].kind != "start_hub":
            raise ValueError(
                f"'{self.start_hub}' must be declared as start_hub"
            )
        if self.hubs[self.end_hub].kind != "end_hub":
            raise ValueError(f"'{self.end_hub}' must be declared as end_hub")
        seen: set[tuple[str, str]] = set()
        for conn in self.connections:
            hub_a, hub_b = conn.hub_a, conn.hub_b
            if hub_a not in self.hubs:
                raise ValueError(
                    f"connection references unknown hub '{hub_a}'"
                )
            if hub_b not in self.hubs:
                raise ValueError(
                    f"connection references unknown hub '{hub_b}'"
                )
            if hub_a == hub_b:
                raise ValueError("self-loop connections are not allowed")
            # Check for duplicate connections (bidirectional)
            normalized: tuple[str, str] = cast(tuple[str, str],
                                               tuple(sorted([hub_a, hub_b])))
            if normalized in seen:
                raise ValueError(f"duplicate connection: {hub_a}-{hub_b}")
            seen.add(normalized)

    @classmethod
    def from_parts(
        cls,
        *,
        nb_drones: int,
        hubs: Iterable[Hub],
        connections: Iterable[Connection],
    ) -> Data:
        """Factory that accepts variable-size inputs (any
        number of hubs/connections).
        Validates the data and constructs the Data object.
         This is useful for parsing
        from text input where the number of hubs and conne
        ctions is not known in advance.
        @var nb_drones: Total number of drones available
        @var hubs: Iterable of Hub objects
        @var connections: Iterable of Connection objects
        @returns: A validated Data object containing the entire configuration
        """
        hubs_dict: dict[str, Hub] = {}
        start_name: str | None = None
        end_name: str | None = None

        for h in hubs:
            if h.name in hubs_dict:
                raise ValueError(f"duplicate hub name '{h.name}'")
            hubs_dict[h.name] = h
            if h.kind == "start_hub":
                if start_name is not None:
                    raise ValueError("multiple start_hub declarations")
                start_name = h.name
            elif h.kind == "end_hub":
                if end_name is not None:
                    raise ValueError("multiple end_hub declarations")
                end_name = h.name

        if start_name is None:
            raise ValueError("missing start_hub")
        if end_name is None:
            raise ValueError("missing end_hub")

        return cls(
            nb_drones=nb_drones,
            hubs=hubs_dict,
            connections=list(connections),
            start_hub=start_name,
            end_hub=end_name,
        )
