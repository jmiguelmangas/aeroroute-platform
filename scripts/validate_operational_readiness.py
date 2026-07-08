from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_GATES = {
    "simulator_guardrail",
    "operator_profile",
    "licensed_operational_data",
    "safety_case",
    "requirements_traceability",
    "manual_acceptance",
    "independent_validation",
}


def validate_operational_readiness(
    evidence_path: Path, hazard_log_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    hazard_log = json.loads(hazard_log_path.read_text(encoding="utf-8"))

    if evidence.get("contract_version") != "1.0.0":
        raise ValueError("operational evidence contract version must be 1.0.0")
    if hazard_log.get("contract_version") != "1.0.0":
        raise ValueError("hazard log contract version must be 1.0.0")
    if evidence.get("ops_mode") != "simulator":
        raise ValueError(
            "operational readiness baseline must stay in simulator mode"
        )
    if evidence.get("operational_use_enabled") is not False:
        raise ValueError("operational use must remain disabled")

    gates = {
        gate.get("id"): gate for gate in evidence.get("evidence_gates", [])
    }
    if set(gates) != REQUIRED_GATES:
        raise ValueError("operational evidence gates are incomplete")
    for gate_id, gate in gates.items():
        if gate.get("required_before_ops") is not True:
            raise ValueError(f"{gate_id}: gate must be required before ops")
    for blocked_gate in REQUIRED_GATES - {"simulator_guardrail"}:
        if gates[blocked_gate].get("status") not in {"missing", "partial"}:
            raise ValueError(f"{blocked_gate}: gate must still block ops")
    if gates["simulator_guardrail"].get("status") != "present":
        raise ValueError("simulator guardrail evidence must be present")

    requirements = evidence.get("requirements", [])
    if not any(
        item.get("id") == "OPS-REQ-001" and item.get("status") == "implemented"
        for item in requirements
    ):
        raise ValueError("implemented simulator guardrail requirement missing")
    for requirement in requirements:
        if requirement.get("blocking_for_operational_use") is not True:
            raise ValueError(
                f"{requirement.get('id')}: must block operational use"
            )
        if not requirement.get("verification"):
            raise ValueError(f"{requirement.get('id')}: verification missing")

    hazards = hazard_log.get("hazards", [])
    if len(hazards) < 6:
        raise ValueError("hazard log must include the baseline safety concerns")
    for hazard in hazards:
        hazard_id = hazard.get("id")
        if hazard.get("status") == "accepted":
            raise ValueError(f"{hazard_id}: cannot be accepted in baseline")
        if hazard.get("blocking_for_operational_use") is not True:
            raise ValueError(f"{hazard_id}: must block operational use")
        if not hazard.get("mitigations"):
            raise ValueError(f"{hazard_id}: mitigations missing")
        if not hazard.get("verification"):
            raise ValueError(f"{hazard_id}: verification missing")

    return evidence, hazard_log


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    validate_operational_readiness(
        root / "reference" / "operational-readiness-evidence-2026-07-08.json",
        root / "reference" / "operational-hazard-log-2026-07-08.json",
    )


if __name__ == "__main__":
    main()
