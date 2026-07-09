from pathlib import Path

import pytest

from scripts.validate_route_coverage import validate_route_coverage


def test_supported_route_coverage_report_is_complete() -> None:
    report = validate_route_coverage(
        Path("reference/supported-route-coverage-2026-07-09.json")
    )

    assert report["summary"]["complete_pairs"] == 1
    assert report["summary"]["degraded_pairs"] == 3
    assert report["coverage_policy"]["preflight_endpoint"].endswith(
        "/route-support"
    )


def test_route_coverage_rejects_missing_problem_modes(tmp_path: Path) -> None:
    source = Path("reference/supported-route-coverage-2026-07-09.json")
    target = tmp_path / "coverage.json"
    text = source.read_text()
    target.write_text(
        text.replace('"stable_problem_modes": 3', '"stable_problem_modes": 2')
    )

    with pytest.raises(ValueError, match="problem-mode summary"):
        validate_route_coverage(target)
