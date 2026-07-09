from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_GATES = {
    "approved_performance_data",
    "fuel_policy_acceptance",
    "runway_weight_balance_limits",
    "minima_alternate_suitability",
    "dispatcher_signoff",
}


def validate_dispatch_readiness(path: Path) -> dict[str, Any]:
    baseline = json.loads(path.read_text(encoding="utf-8"))
    if baseline.get("contract_version") != "1.0.0":
        raise ValueError("dispatch baseline contract version must be 1.0.0")
    if baseline.get("baseline") != "dispatch-readiness-2026-07-09":
        raise ValueError("dispatch baseline identifier mismatch")
    if baseline.get("operational_use_enabled") is not False:
        raise ValueError("dispatch baseline must not enable operational use")
    if baseline.get("dispatch_release_enabled") is not False:
        raise ValueError("dispatch baseline must not enable release")
    if baseline.get("status") != "blocked":
        raise ValueError("dispatch baseline must remain blocked")
    gates = {gate.get("id"): gate for gate in baseline.get("gates", [])}
    if set(gates) != REQUIRED_GATES:
        raise ValueError("dispatch readiness gates are incomplete")
    if {gate.get("status") for gate in gates.values()} != {"missing"}:
        raise ValueError("dispatch gates must remain missing in baseline")
    return baseline


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    validate_dispatch_readiness(
        root / "reference" / "dispatch-readiness-2026-07-09.json"
    )


if __name__ == "__main__":
    main()
