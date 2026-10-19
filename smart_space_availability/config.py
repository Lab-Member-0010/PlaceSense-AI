"""Configuration and validation helpers."""

from __future__ import annotations

import json
from typing import Any


def parse_zones(raw: str) -> list[dict[str, Any]]:
    """Parse and validate normalized polygon zone configuration."""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Zone configuration is not valid JSON: {exc.msg}") from exc
    zones = payload.get("zones") if isinstance(payload, dict) else None
    if not isinstance(zones, list) or not zones:
        raise ValueError("Configuration must contain a non-empty 'zones' list.")

    validated: list[dict[str, Any]] = []
    for index, zone in enumerate(zones, start=1):
        if not isinstance(zone, dict):
            raise ValueError(f"Zone {index} must be an object.")
        name = str(zone.get("name", f"Zone {index}")).strip() or f"Zone {index}"
        points = zone.get("points")
        try:
            capacity = int(zone.get("capacity", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name}: capacity must be an integer.") from exc
        if not isinstance(points, list) or len(points) < 3:
            raise ValueError(f"{name}: points must contain at least three coordinates.")
        if capacity < 0:
            raise ValueError(f"{name}: capacity cannot be negative.")
        normalized_points = []
        for point in points:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError(f"{name}: each point must be [x, y].")
            try:
                x, y = float(point[0]), float(point[1])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{name}: point coordinates must be numeric.") from exc
            if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                raise ValueError(f"{name}: point coordinates must be between 0 and 1.")
            normalized_points.append([x, y])
        validated.append({"name": name, "capacity": capacity, "points": normalized_points})
    return validated
