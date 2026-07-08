from pathlib import Path

import pytest

from scripts.validate_operational_readiness import (
    validate_operational_readiness,
)


EVIDENCE = Path("reference/operational-readiness-evidence-2026-07-08.json")
HAZARDS = Path("reference/operational-hazard-log-2026-07-08.json")


def test_operational_readiness_baseline_blocks_operational_use() -> None:
    evidence, hazard_log = validate_operational_readiness(EVIDENCE, HAZARDS)

    assert evidence["ops_mode"] == "simulator"
    assert evidence["operational_use_enabled"] is False
    assert {hazard["status"] for hazard in hazard_log["hazards"]} == {"open"}


def test_operational_readiness_rejects_enabled_ops(tmp_path: Path) -> None:
    target = tmp_path / "evidence.json"
    target.write_text(
        EVIDENCE.read_text().replace(
            '"operational_use_enabled": false',
            '"operational_use_enabled": true',
        )
    )

    with pytest.raises(ValueError, match="operational use"):
        validate_operational_readiness(target, HAZARDS)


def test_hazard_log_rejects_accepted_baseline_hazard(tmp_path: Path) -> None:
    target = tmp_path / "hazards.json"
    target.write_text(
        HAZARDS.read_text().replace(
            '"status": "open"', '"status": "accepted"', 1
        )
    )

    with pytest.raises(ValueError, match="cannot be accepted"):
        validate_operational_readiness(EVIDENCE, target)
