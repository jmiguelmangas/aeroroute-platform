from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_GATES = {
    "requirements_traceability",
    "independent_validation",
    "release_data_cycle_control",
    "audit_slo_observability",
    "security_incident_response",
    "fallback_procedures",
}


def validate_assurance_readiness(path: Path) -> dict[str, Any]:
    baseline = json.loads(path.read_text(encoding="utf-8"))
    if baseline.get("contract_version") != "1.0.0":
        raise ValueError("assurance baseline contract version must be 1.0.0")
    if baseline.get("baseline") != "assurance-readiness-2026-07-09":
        raise ValueError("assurance baseline identifier mismatch")
    if baseline.get("operational_use_enabled") is not False:
        raise ValueError("assurance baseline must not enable operational use")
    if baseline.get("assurance_enabled") is not False:
        raise ValueError("assurance baseline must not enable assurance")
    if baseline.get("status") != "blocked":
        raise ValueError("assurance baseline must remain blocked")
    gates = {gate.get("id"): gate for gate in baseline.get("gates", [])}
    if set(gates) != REQUIRED_GATES:
        raise ValueError("assurance readiness gates are incomplete")
    if {gate.get("status") for gate in gates.values()} != {"missing"}:
        raise ValueError("assurance gates must remain missing in baseline")
    return baseline


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    validate_assurance_readiness(
        root / "reference" / "assurance-readiness-2026-07-09.json"
    )


if __name__ == "__main__":
    main()
