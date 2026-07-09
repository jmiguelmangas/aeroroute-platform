from pathlib import Path

import pytest

from scripts.validate_dispatch_readiness import validate_dispatch_readiness


BASELINE = Path("reference/dispatch-readiness-2026-07-09.json")


def test_dispatch_readiness_baseline_blocks_release() -> None:
    baseline = validate_dispatch_readiness(BASELINE)

    assert baseline["dispatch_release_enabled"] is False
    assert baseline["operational_use_enabled"] is False
    assert baseline["status"] == "blocked"


def test_dispatch_readiness_rejects_enabled_release(tmp_path: Path) -> None:
    target = tmp_path / "dispatch.json"
    target.write_text(
        BASELINE.read_text().replace(
            '"dispatch_release_enabled": false',
            '"dispatch_release_enabled": true',
        )
    )

    with pytest.raises(ValueError, match="must not enable release"):
        validate_dispatch_readiness(target)
