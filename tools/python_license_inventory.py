"""Emit a deterministic inventory of licenses visible in the uv environment."""

from __future__ import annotations

import json
from importlib.metadata import distributions
from typing import TypedDict


class PackageLicense(TypedDict):
    name: str
    version: str
    license: str


def inventory() -> list[PackageLicense]:
    """Return installed distributions with their declared license metadata."""
    packages: list[PackageLicense] = []
    for distribution in distributions():
        name = distribution.metadata.get("Name")
        if not name:
            continue
        declared_license = (
            distribution.metadata.get("License-Expression")
            or distribution.metadata.get("License")
            or "UNKNOWN"
        )
        packages.append(
            {
                "name": name,
                "version": distribution.version,
                "license": declared_license,
            }
        )
    return sorted(packages, key=lambda package: package["name"].casefold())


if __name__ == "__main__":
    print(json.dumps(inventory(), indent=2, ensure_ascii=False))
