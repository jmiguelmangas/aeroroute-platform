import sys
import re
from pathlib import Path

import yaml


def main(path: str) -> None:
    document = yaml.safe_load(Path(path).read_text())
    required = {"contracts", "optimizer", "api", "data", "mlx", "mlx_training", "web"}
    actual = set(document.get("components", {}))
    missing = required - actual
    if missing:
        raise SystemExit(f"Missing release components: {', '.join(sorted(missing))}")
    for name, component in document["components"].items():
        commit = component.get("source_commit")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise SystemExit(f"{name} must pin a 40-character source_commit")
    bundle_checksum = document["components"]["data"].get("bundle_sha256")
    if not isinstance(bundle_checksum, str) or not re.fullmatch(
        r"[0-9a-f]{64}", bundle_checksum
    ):
        raise SystemExit("data must pin a 64-character bundle_sha256")
    print("Release manifest is structurally valid.")


if __name__ == "__main__":
    main(sys.argv[1])
