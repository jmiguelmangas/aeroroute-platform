import sys
from pathlib import Path

import yaml


def main(path: str) -> None:
    document = yaml.safe_load(Path(path).read_text())
    required = {"contracts", "optimizer", "api", "data", "mlx", "mlx_training", "web"}
    actual = set(document.get("components", {}))
    missing = required - actual
    if missing:
        raise SystemExit(f"Missing release components: {', '.join(sorted(missing))}")
    print("Release manifest is structurally valid.")


if __name__ == "__main__":
    main(sys.argv[1])
