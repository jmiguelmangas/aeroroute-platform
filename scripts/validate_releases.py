import json
import sys
import tomllib
from pathlib import Path

import yaml


REQUIRED_COMPONENTS = {
    "contracts",
    "optimizer",
    "api",
    "data",
    "mlx",
    "mlx_training",
    "web",
}

# Maps each top-level component to the sibling repo directory (relative to
# the multi-repo checkout root, i.e. the parent of aeroroute-platform) that
# owns the version-of-record for that component.
COMPONENT_REPO_DIRS = {
    "contracts": "aeroroute-contracts",
    "optimizer": "aeroroute-optimizer",
    "api": "aeroroute-api",
    "data": "aeroroute-data",
    "mlx": "aeroroute-mlx",
    "mlx_training": "aeroroute-mlx-training",
    "web": "aeroroute-web",
}


def validate_release_manifest(path: Path) -> None:
    root = path.resolve().parent
    document = yaml.safe_load(path.read_text())
    if not isinstance(document, dict):
        raise ValueError("Release manifest must be a mapping")
    components = document.get("components")
    if not isinstance(components, dict):
        raise ValueError("Release manifest components must be a mapping")
    missing = REQUIRED_COMPONENTS - set(components)
    if missing:
        raise ValueError(
            f"Missing release components: {', '.join(sorted(missing))}"
        )
    _validate_component_versions(root, components)
    references = document.get("references")
    if not isinstance(references, dict):
        raise ValueError("Release manifest references must be a mapping")
    _validate_reference(
        root,
        references,
        "flight_plan_scenarios",
        required_keys=("airac_cycle", "airport_bundle_sha256"),
    )
    _validate_reference(
        root,
        references,
        "route_coverage",
        required_keys=("airac_cycle", "airport_bundle_sha256"),
    )


def _pinned_component_version(components: dict[str, object], name: str) -> str:
    entry = components.get(name)
    version = entry.get("version") if isinstance(entry, dict) else entry
    if not isinstance(version, str) or not version:
        raise ValueError(f"Component '{name}' is missing a pinned version")
    return version


def _read_version_file(path: Path) -> str:
    return path.read_text().strip()


def _read_pyproject_version(path: Path) -> str:
    data = tomllib.loads(path.read_text())
    version = data.get("project", {}).get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"Could not find [project].version in {path}")
    return version


def _read_package_json_version(path: Path) -> str:
    data = json.loads(path.read_text())
    version = data.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"Could not find \"version\" field in {path}")
    return version


def _actual_component_version(repo_dir: Path, component: str) -> str:
    if component == "contracts":
        return _read_version_file(repo_dir / "VERSION")
    if component == "web":
        return _read_package_json_version(repo_dir / "package.json")
    return _read_pyproject_version(repo_dir / "pyproject.toml")


def _validate_component_versions(root: Path, components: dict[str, object]) -> None:
    """Cross-check RELEASES.yaml pins against the real sibling repo checkouts.

    CI only checks out aeroroute-platform (no sibling repos), so a missing
    sibling directory is treated as a graceful skip with a warning rather
    than a hard failure. When a sibling checkout IS present (always true in
    this multi-repo workspace), a version mismatch is a hard failure — this
    is the guardrail against the drift that Phase 1 had to fix by hand.
    """
    multi_repo_root = root.parent
    for component, repo_dir_name in sorted(COMPONENT_REPO_DIRS.items()):
        repo_dir = multi_repo_root / repo_dir_name
        if not repo_dir.is_dir():
            print(
                f"WARNING: sibling checkout '{repo_dir_name}' not found; "
                f"skipping version cross-check for component '{component}'. "
                "This is expected in CI, which only checks out "
                "aeroroute-platform.",
                file=sys.stderr,
            )
            continue
        pinned = _pinned_component_version(components, component)
        actual = _actual_component_version(repo_dir, component)
        if pinned != actual:
            raise ValueError(
                f"Release manifest version drift for '{component}': "
                f"RELEASES.yaml pins {pinned!r} but {repo_dir_name} is "
                f"actually at {actual!r}"
            )


def _validate_reference(
    root: Path,
    references: dict[str, object],
    name: str,
    *,
    required_keys: tuple[str, ...],
) -> None:
    reference = references.get(name)
    if not isinstance(reference, dict):
        raise ValueError(f"Missing release reference: {name}")
    path_value = reference.get("path")
    if not isinstance(path_value, str) or not path_value:
        raise ValueError(f"{name} reference must include a path")
    target = root / path_value
    if not target.is_file():
        raise ValueError(f"{name} reference file does not exist: {path_value}")
    document = json.loads(target.read_text())
    for key in required_keys:
        if reference.get(key) != document.get(key):
            raise ValueError(f"{name} reference {key} does not match artifact")


def main(path: str) -> None:
    try:
        validate_release_manifest(Path(path))
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print("Release manifest is structurally valid.")


if __name__ == "__main__":
    main(sys.argv[1])
