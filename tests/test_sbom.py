import json
from pathlib import Path


def test_committed_sboms_are_normalized_cyclonedx() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = sorted(
        path
        for path in (root / "sbom").glob("*.cdx.json")
        if not path.name.startswith("._")
    )

    assert len(paths) == 6
    for path in paths:
        document = json.loads(path.read_text())
        assert document["bomFormat"] == "CycloneDX"
        assert document["specVersion"] == "1.5"
        assert "serialNumber" not in document
        assert "timestamp" not in document["metadata"]
