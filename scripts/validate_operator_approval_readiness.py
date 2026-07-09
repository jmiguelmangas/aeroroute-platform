from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_GATES = {
    "operator_acceptance",
    "regulator_submission_pack",
    "manuals_training",
    "parallel_run_campaign",
    "go_no_go_decision",
}


def validate_operator_approval_readiness(path: Path) -> dict[str, Any]:
    baseline = json.loads(path.read_text(encoding="utf-8"))
    if baseline.get("contract_version") != "1.0.0":
        raise ValueError("operator approval contract version must be 1.0.0")
    if baseline.get("baseline") != "operator-approval-readiness-2026-07-09":
        raise ValueError("operator approval baseline identifier mismatch")
    if baseline.get("operational_use_enabled") is not False:
        raise ValueError("operator approval must not enable operational use")
    if baseline.get("operator_approval_enabled") is not False:
        raise ValueError("operator approval must not be enabled")
    if baseline.get("rollout_state") != "blocked":
        raise ValueError("operator approval rollout must remain blocked")
    if baseline.get("ops_mode") != "simulator":
        raise ValueError(
            "operator approval baseline must remain simulator mode"
        )
    gates = {gate.get("id"): gate for gate in baseline.get("gates", [])}
    if set(gates) != REQUIRED_GATES:
        raise ValueError("operator approval gates are incomplete")
    if {gate.get("status") for gate in gates.values()} != {"missing"}:
        raise ValueError("operator approval gates must remain missing")
    return baseline


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    validate_operator_approval_readiness(
        root / "reference" / "operator-approval-readiness-2026-07-09.json"
    )


if __name__ == "__main__":
    main()
