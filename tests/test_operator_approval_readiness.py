from pathlib import Path

import pytest

from scripts.validate_operator_approval_readiness import (
    validate_operator_approval_readiness,
)


BASELINE = Path("reference/operator-approval-readiness-2026-07-09.json")


def test_operator_approval_readiness_baseline_blocks_rollout() -> None:
    baseline = validate_operator_approval_readiness(BASELINE)

    assert baseline["operator_approval_enabled"] is False
    assert baseline["operational_use_enabled"] is False
    assert baseline["rollout_state"] == "blocked"
    assert baseline["ops_mode"] == "simulator"


def test_operator_approval_readiness_rejects_enabled_rollout(
    tmp_path: Path,
) -> None:
    target = tmp_path / "operator-approval.json"
    target.write_text(
        BASELINE.read_text().replace(
            '"operator_approval_enabled": false',
            '"operator_approval_enabled": true',
        )
    )

    with pytest.raises(ValueError, match="must not be enabled"):
        validate_operator_approval_readiness(target)
