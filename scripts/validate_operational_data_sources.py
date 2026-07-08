from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_DOMAINS = {
    "navdata",
    "weather",
    "notam",
    "airspace_restrictions",
    "airport_status",
    "terrain_obstacle",
    "aircraft_performance",
    "filing",
}
REQUIRED_BLOCKING_FALLBACKS = {
    "notam",
    "airspace_restrictions",
    "terrain_obstacle",
    "filing",
}


def validate_operational_data_sources(path: Path) -> dict[str, Any]:
    baseline = json.loads(path.read_text(encoding="utf-8"))
    if baseline.get("contract_version") != "1.0.0":
        raise ValueError("data-source baseline contract version must be 1.0.0")
    if baseline.get("operational_use_enabled") is not False:
        raise ValueError("operational data sources must not enable ops")

    sources = baseline.get("sources", [])
    by_domain = {source.get("domain"): source for source in sources}
    if set(by_domain) != REQUIRED_DOMAINS:
        raise ValueError("operational data-source domains are incomplete")

    for domain, source in by_domain.items():
        if source.get("contract_version") != "1.0.0":
            raise ValueError(f"{domain}: source contract version mismatch")
        if source.get("operational_ready") is not False:
            raise ValueError(f"{domain}: cannot be operational in baseline")
        license_info = source.get("license", {})
        if license_info.get("approved_for_operational_use") is not False:
            raise ValueError(f"{domain}: operational license cannot be present")
        if source.get("status") == "operational":
            raise ValueError(f"{domain}: status cannot be operational")
        quality = source.get("quality", {})
        if quality.get("grade") == "operational":
            raise ValueError(f"{domain}: quality grade cannot be operational")
        if domain in REQUIRED_BLOCKING_FALLBACKS and (
            source.get("fallback_behavior") != "block_operational_use"
        ):
            raise ValueError(f"{domain}: missing fail-closed fallback")

    return baseline


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    validate_operational_data_sources(
        root / "reference" / "operational-data-sources-2026-07-09.json"
    )


if __name__ == "__main__":
    main()
