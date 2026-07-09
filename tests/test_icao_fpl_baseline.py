from pathlib import Path

import pytest

from scripts.validate_icao_fpl_baseline import validate_icao_fpl_baseline


BASELINE = Path("reference/icao-fpl-validation-2026-07-09.json")


def test_icao_fpl_baseline_blocks_filing() -> None:
    baseline = validate_icao_fpl_baseline(BASELINE)

    assert baseline["filing_enabled"] is False
    assert baseline["operational_use_enabled"] is False
    assert baseline["status"] == "blocked"


def test_icao_fpl_baseline_rejects_enabled_filing(tmp_path: Path) -> None:
    target = tmp_path / "icao.json"
    target.write_text(
        BASELINE.read_text().replace(
            '"filing_enabled": false',
            '"filing_enabled": true',
        )
    )

    with pytest.raises(ValueError, match="must not enable filing"):
        validate_icao_fpl_baseline(target)


def test_icao_fpl_baseline_rejects_operator_aircraft_approval(
    tmp_path: Path,
) -> None:
    target = tmp_path / "icao-fpl.json"
    target.write_text(
        BASELINE.read_text().replace(
            '"operator_aircraft_capability_approval": "missing"',
            '"operator_aircraft_capability_approval": "accepted"',
        )
    )

    with pytest.raises(ValueError, match="approval must be missing"):
        validate_icao_fpl_baseline(target)
