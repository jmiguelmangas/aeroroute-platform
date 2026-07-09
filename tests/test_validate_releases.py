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


_ACTUAL_VERSIONS = {
    "contracts": "0.14.0",
    "optimizer": "0.2.1",
    "api": "0.14.0",
    "data": "0.1.0",
    "mlx": "0.2.0",
    "mlx_training": "0.1.0",
    "web": "0.1.0",
}

_PYPROJECT_COMPONENT_DIRS = {
    "optimizer": "aeroroute-optimizer",
    "api": "aeroroute-api",
    "data": "aeroroute-data",
    "mlx": "aeroroute-mlx",
    "mlx_training": "aeroroute-mlx-training",
}


def _write_sibling_repos(multi_repo_root: Path, versions: dict[str, str]) -> None:
    contracts_dir = multi_repo_root / "aeroroute-contracts"
    contracts_dir.mkdir()
    (contracts_dir / "VERSION").write_text(versions["contracts"] + "\n")

    for component, repo_dir_name in _PYPROJECT_COMPONENT_DIRS.items():
        repo_dir = multi_repo_root / repo_dir_name
        repo_dir.mkdir()
        (repo_dir / "pyproject.toml").write_text(
            f'[project]\nname = "{repo_dir_name}"\n'
            f'version = "{versions[component]}"\n'
        )

    web_dir = multi_repo_root / "aeroroute-web"
    web_dir.mkdir()
    (web_dir / "package.json").write_text(
        f'{{\n  "name": "aeroroute-web",\n  "version": "{versions["web"]}"\n}}\n'
    )


def _write_platform_manifest(platform_dir: Path, versions: dict[str, str]) -> Path:
    platform_dir.mkdir()
    reference_dir = platform_dir / "reference"
    reference_dir.mkdir()
    shutil.copy(
        Path("reference/flight-plan-scenarios-2026-06-29.json"),
        reference_dir / "flight-plan-scenarios-2026-06-29.json",
    )
    shutil.copy(
        Path("reference/supported-route-coverage-2026-07-08.json"),
        reference_dir / "supported-route-coverage-2026-07-08.json",
    )
    manifest = platform_dir / "RELEASES.yaml"
    manifest.write_text(
        f"""
components:
  contracts: {{ version: {versions['contracts']} }}
  optimizer: {{ version: {versions['optimizer']} }}
  api: {{ version: {versions['api']} }}
  data: {{ version: {versions['data']} }}
  mlx: {{ version: {versions['mlx']} }}
  mlx_training: {{ version: {versions['mlx_training']} }}
  web: {{ version: {versions['web']} }}
references:
  flight_plan_scenarios:
    path: reference/flight-plan-scenarios-2026-06-29.json
    airac_cycle: "2606"
    airport_bundle_sha256: f5d0d51de0c1b9bf0c2ed5ab2f98d7a8dc6d7ebf26ff2797a6f0f76337a41bff
  route_coverage:
    path: reference/supported-route-coverage-2026-07-08.json
    airac_cycle: "2606"
    airport_bundle_sha256: f5d0d51de0c1b9bf0c2ed5ab2f98d7a8dc6d7ebf26ff2797a6f0f76337a41bff
"""
    )
    return manifest


def test_component_versions_matching_siblings_pass(tmp_path: Path) -> None:
    _write_sibling_repos(tmp_path, _ACTUAL_VERSIONS)
    manifest = _write_platform_manifest(
        tmp_path / "aeroroute-platform", _ACTUAL_VERSIONS
    )

    validate_release_manifest(manifest)


def test_component_version_drift_is_rejected(tmp_path: Path) -> None:
    # Reproduces the real Phase 1 bug: contracts drifted to 0.14.0 in the
    # sibling repo while RELEASES.yaml still pinned 0.6.0.
    _write_sibling_repos(tmp_path, _ACTUAL_VERSIONS)
    pinned_versions = dict(_ACTUAL_VERSIONS, contracts="0.6.0")
    manifest = _write_platform_manifest(
        tmp_path / "aeroroute-platform", pinned_versions
    )

    with pytest.raises(
        ValueError,
        match=r"version drift for 'contracts'.*'0\.6\.0'.*'0\.14\.0'",
    ):
        validate_release_manifest(manifest)


def test_missing_sibling_checkout_skips_gracefully(tmp_path: Path) -> None:
    # CI only checks out aeroroute-platform, so no sibling repos exist on
    # disk there. A missing sibling directory must not crash the check --
    # it should be skipped with a warning, letting the rest of the
    # structural validation run normally.
    manifest = _write_platform_manifest(
        tmp_path / "aeroroute-platform", _ACTUAL_VERSIONS
    )

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
