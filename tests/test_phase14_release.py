from pathlib import Path

import pytest

from scripts.verify_phase14_release import validate_phase14_release


def test_phase14_release_evidence_is_complete() -> None:
    validate_phase14_release(Path(__file__).resolve().parents[1])


def test_phase14_release_rejects_missing_evidence(tmp_path: Path) -> None:
    (tmp_path / "RELEASES.yaml").write_text("release: test\n")

    with pytest.raises(ValueError, match="Release manifest components"):
        validate_phase14_release(tmp_path)
