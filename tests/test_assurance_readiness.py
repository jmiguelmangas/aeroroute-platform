from pathlib import Path

import pytest

from scripts.validate_assurance_readiness import validate_assurance_readiness


BASELINE = Path("reference/assurance-readiness-2026-07-09.json")


def test_assurance_readiness_baseline_blocks_assurance() -> None:
    baseline = validate_assurance_readiness(BASELINE)

    assert baseline["assurance_enabled"] is False
    assert baseline["operational_use_enabled"] is False
    assert baseline["status"] == "blocked"


def test_assurance_readiness_rejects_enabled_assurance(tmp_path: Path) -> None:
    target = tmp_path / "assurance.json"
    target.write_text(
        BASELINE.read_text().replace(
            '"assurance_enabled": false',
            '"assurance_enabled": true',
        )
    )

    with pytest.raises(ValueError, match="must not enable assurance"):
        validate_assurance_readiness(target)
