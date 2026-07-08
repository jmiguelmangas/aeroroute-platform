from __future__ import annotations

import argparse
import json
from pathlib import Path


def normalize(path: Path) -> None:
    document = json.loads(path.read_text())
    document.pop("serialNumber", None)
    metadata = document.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("timestamp", None)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    arguments = parser.parse_args()
    for path in sorted(arguments.directory.glob("*.cdx.json")):
        normalize(path)


if __name__ == "__main__":
    main()
