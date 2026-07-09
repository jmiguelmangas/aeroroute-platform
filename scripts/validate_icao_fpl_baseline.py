from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ITEMS = {"7", "8", "9", "10", "13", "15", "16", "18", "19"}
REQUIRED_BLOCKERS = {
    "filing_gateway_not_configured",
    "notam_rad_atc_restrictions_missing",
    "operator_aircraft_capability_not_accepted",
}


def validate_icao_fpl_baseline(path: Path) -> dict[str, Any]:
    baseline = json.loads(path.read_text(encoding="utf-8"))
    if baseline.get("contract_version") != "1.0.0":
        raise ValueError("ICAO FPL baseline contract version must be 1.0.0")
    if baseline.get("baseline") != "icao-fpl-validation-2026-07-09":
        raise ValueError("ICAO FPL baseline identifier mismatch")
    if baseline.get("operational_use_enabled") is not False:
        raise ValueError("ICAO FPL baseline must not enable operational use")
    if baseline.get("filing_enabled") is not False:
        raise ValueError("ICAO FPL baseline must not enable filing")
    if set(baseline.get("required_items", [])) != REQUIRED_ITEMS:
        raise ValueError("ICAO FPL required item coverage is incomplete")
    if set(baseline.get("required_blockers", [])) != REQUIRED_BLOCKERS:
        raise ValueError("ICAO FPL operational blockers are incomplete")
    if baseline.get("status") != "blocked":
        raise ValueError("ICAO FPL baseline must remain blocked")
    return baseline


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    validate_icao_fpl_baseline(
        root / "reference" / "icao-fpl-validation-2026-07-09.json"
    )


if __name__ == "__main__":
    main()
