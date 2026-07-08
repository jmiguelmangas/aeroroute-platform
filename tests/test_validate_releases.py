from pathlib import Path
import shutil

import pytest

from scripts.validate_releases import validate_release_manifest


def test_repository_release_manifest_is_valid() -> None:
    validate_release_manifest(Path("RELEASES.yaml"))


def test_missing_component_is_rejected(tmp_path: Path) -> None:
    manifest = tmp_path / "RELEASES.yaml"
    manifest.write_text("components:\n  api: 0.1.0\n")

    with pytest.raises(ValueError, match="Missing release components"):
        validate_release_manifest(manifest)


def test_missing_reference_is_rejected(tmp_path: Path) -> None:
    manifest = tmp_path / "RELEASES.yaml"
    manifest.write_text(
        """
components:
  contracts: { version: 0.6.0 }
  optimizer: { version: 0.2.1 }
  api: { version: 0.6.0 }
  data: { version: 0.1.0 }
  mlx: { version: 0.2.0 }
  mlx_training: { version: 0.1.0 }
  web: { version: 0.1.0 }
references: {}
"""
    )

    with pytest.raises(ValueError, match="Missing release reference"):
        validate_release_manifest(manifest)


def test_reference_metadata_mismatch_is_rejected(tmp_path: Path) -> None:
    reference_root = tmp_path / "reference"
    reference_root.mkdir()
    shutil.copy(
        Path("reference/flight-plan-scenarios-2026-06-29.json"),
        reference_root / "flight-plan-scenarios-2026-06-29.json",
    )
    shutil.copy(
        Path("reference/supported-route-coverage-2026-07-08.json"),
        reference_root / "supported-route-coverage-2026-07-08.json",
    )
    manifest = tmp_path / "RELEASES.yaml"
    manifest.write_text(
        """
components:
  contracts: { version: 0.6.0 }
  optimizer: { version: 0.2.1 }
  api: { version: 0.6.0 }
  data: { version: 0.1.0 }
  mlx: { version: 0.2.0 }
  mlx_training: { version: 0.1.0 }
  web: { version: 0.1.0 }
references:
  flight_plan_scenarios:
    path: reference/flight-plan-scenarios-2026-06-29.json
    airac_cycle: "9999"
    airport_bundle_sha256: f5d0d51de0c1b9bf0c2ed5ab2f98d7a8dc6d7ebf26ff2797a6f0f76337a41bff
  route_coverage:
    path: reference/supported-route-coverage-2026-07-08.json
    airac_cycle: "2606"
    airport_bundle_sha256: f5d0d51de0c1b9bf0c2ed5ab2f98d7a8dc6d7ebf26ff2797a6f0f76337a41bff
"""
    )

    with pytest.raises(ValueError, match="airac_cycle does not match"):
        validate_release_manifest(manifest)
