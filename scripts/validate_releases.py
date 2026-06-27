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


def main(path: str) -> None:
    try:
        validate_release_manifest(Path(path))
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print("Release manifest is structurally valid.")


if __name__ == "__main__":
    main(sys.argv[1])
