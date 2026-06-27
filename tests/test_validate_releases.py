from pathlib import Path

import pytest

from scripts.validate_releases import validate_release_manifest


def test_repository_release_manifest_is_valid() -> None:
    validate_release_manifest(Path("RELEASES.yaml"))


def test_missing_component_is_rejected(tmp_path: Path) -> None:
    manifest = tmp_path / "RELEASES.yaml"
    manifest.write_text("components:\n  api: 0.1.0\n")

    with pytest.raises(ValueError, match="Missing release components"):
        validate_release_manifest(manifest)
