from pathlib import Path

import pytest

from scripts.validate_operational_data_sources import (
    validate_operational_data_sources,
)


BASELINE = Path("reference/operational-data-sources-2026-07-09.json")


def test_operational_data_sources_baseline_is_fail_closed() -> None:
    baseline = validate_operational_data_sources(BASELINE)

    assert baseline["operational_use_enabled"] is False
    assert len(baseline["sources"]) == 8
    assert {source["operational_ready"] for source in baseline["sources"]} == {
        False
    }


def test_operational_data_sources_reject_enabled_ops(tmp_path: Path) -> None:
    target = tmp_path / "sources.json"
    target.write_text(
        BASELINE.read_text().replace(
            '"operational_use_enabled": false',
            '"operational_use_enabled": true',
        )
    )

    with pytest.raises(ValueError, match="must not enable ops"):
        validate_operational_data_sources(target)


def test_operational_data_sources_reject_operational_license(
    tmp_path: Path,
) -> None:
    target = tmp_path / "sources.json"
    target.write_text(
        BASELINE.read_text().replace(
            '"approved_for_operational_use": false',
            '"approved_for_operational_use": true',
            1,
        )
    )

    with pytest.raises(ValueError, match="operational license"):
        validate_operational_data_sources(target)
