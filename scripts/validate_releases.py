import json
import sys
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
