from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate_releases import validate_release_manifest  # noqa: E402
from scripts.validate_route_coverage import validate_route_coverage  # noqa: E402


REFERENCE_SCENARIOS = (
    ROOT / "reference" / "flight-plan-scenarios-2026-07-09.json"
)
ROUTE_COVERAGE = ROOT / "reference" / "supported-route-coverage-2026-07-09.json"

REQUIRED_SCENARIOS = {"MAD-JFK", "JFK-MAD", "DXB-MAD", "NRT-SFO"}
REQUIRED_PROBLEM_CODES = {
    "airport_not_supported",
    "navigation_provider_unavailable",
    "runway_procedure_coverage_missing",
}
REQUIRED_SBOMS = {
    "aeroroute-api.cdx.json",
    "aeroroute-data.cdx.json",
    "aeroroute-mlx-training.cdx.json",
    "aeroroute-mlx.cdx.json",
    "aeroroute-optimizer.cdx.json",
    "aeroroute-platform.cdx.json",
}
REQUIRED_RUNBOOK_PHRASES = {
    "operational flight-planning system",
    "make verify-live",
    "make performance-live",
    "Provider degradation",
    "Restore drill",
    "Security and dependency review",
    "X-Request-ID",
}
REQUIRED_SCRIPT_PATHS = {
    "scripts/verify_live_release.py",
    "scripts/check_http_budget.py",
    "scripts/validate_releases.py",
    "scripts/validate_route_coverage.py",
    "scripts/generate_sbom.sh",
    "scripts/normalize_sbom.py",
}
REQUIRED_MAKE_TARGETS = {
    "release-verify:",
    "route-coverage:",
    "verify-live:",
    "performance-live:",
    "sbom:",
    "phase14-release:",
}


def validate_phase14_release(root: Path = ROOT) -> None:
    """Validate the local evidence required to declare Phase 14 complete."""

    _require_file(root / "RELEASES.yaml")
    validate_release_manifest(root / "RELEASES.yaml")

    scenarios = _load_json(root / REFERENCE_SCENARIOS.relative_to(ROOT))
    coverage = _load_json(root / ROUTE_COVERAGE.relative_to(ROOT))
    validate_route_coverage(root / ROUTE_COVERAGE.relative_to(ROOT))

    _validate_non_operational_boundary(scenarios, "flight plan scenarios")
    _validate_non_operational_boundary(coverage, "route coverage")
    _validate_scenarios(scenarios, coverage)
    _validate_coverage(coverage)
    _validate_runbook(root)
    _validate_release_scripts(root)
    _validate_sboms(root)


def _require_file(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"Missing required Phase 14 artifact: {path}")


def _load_json(path: Path) -> dict[str, object]:
    _require_file(path)
    document = json.loads(path.read_text())
    if not isinstance(document, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return document


def _validate_non_operational_boundary(
    document: dict[str, object], name: str
) -> None:
    if document.get("operationally_approved") is not False:
        raise ValueError(f"{name} must remain explicitly non-operational")


def _validate_scenarios(
    scenarios: dict[str, object], coverage: dict[str, object]
) -> None:
    raw_scenarios = scenarios.get("scenarios")
    if not isinstance(raw_scenarios, list):
        raise ValueError("flight plan scenarios must contain a scenarios list")
    names = {
        scenario.get("name")
        for scenario in raw_scenarios
        if isinstance(scenario, dict)
    }
    if names != REQUIRED_SCENARIOS:
        raise ValueError(
            "flight plan scenarios changed: "
            f"expected {sorted(REQUIRED_SCENARIOS)}, got {sorted(names)}"
        )

    coverage_by_name = {
        pair["name"]: pair
        for pair in coverage.get("reference_pairs", [])
        if isinstance(pair, dict) and isinstance(pair.get("name"), str)
    }
    for scenario in raw_scenarios:
        if not isinstance(scenario, dict):
            raise ValueError("scenario entries must be JSON objects")
        name = str(scenario["name"])
        expected = scenario.get("expected")
        if not isinstance(expected, dict):
            raise ValueError(f"{name}: missing expected values")
        for key in (
            "departure_runway",
            "sid",
            "arrival_runway",
            "star",
            "alternate",
            "route_status",
        ):
            if not isinstance(expected.get(key), str) or not expected[key]:
                raise ValueError(f"{name}: expected.{key} must be populated")
        if expected["route_status"] not in {"complete", "degraded"}:
            raise ValueError(
                f"{name}: route_status must be complete or degraded"
            )
        if not isinstance(expected.get("minimum_diversions"), int):
            raise ValueError(f"{name}: minimum_diversions must be an integer")

        pair = coverage_by_name.get(name)
        if not isinstance(pair, dict):
            raise ValueError(f"{name}: missing matching route coverage pair")
        terminal = pair.get("terminal_coverage")
        if not isinstance(terminal, dict):
            raise ValueError(f"{name}: missing terminal coverage")
        for key in ("departure_runway", "sid", "arrival_runway", "star"):
            if terminal.get(key) != expected[key]:
                raise ValueError(f"{name}: {key} differs between references")
        if pair.get("route_status") != expected["route_status"]:
            raise ValueError(f"{name}: route status differs between references")
        if pair.get("alternate") != expected["alternate"]:
            raise ValueError(f"{name}: alternate differs between references")


def _validate_coverage(coverage: dict[str, object]) -> None:
    summary = coverage.get("summary")
    pairs = coverage.get("reference_pairs")
    modes = coverage.get("stable_problem_modes")
    policy = coverage.get("coverage_policy")
    if not isinstance(summary, dict) or not isinstance(pairs, list):
        raise ValueError(
            "route coverage must include summary and reference_pairs"
        )
    if not isinstance(modes, list) or not isinstance(policy, dict):
        raise ValueError("route coverage must include policy and problem modes")

    complete = sum(
        1 for pair in pairs if pair.get("route_status") == "complete"
    )
    degraded = sum(
        1 for pair in pairs if pair.get("route_status") == "degraded"
    )
    if summary.get("evaluated_reference_pairs") != len(pairs):
        raise ValueError("route coverage summary pair count is stale")
    if summary.get("complete_pairs") != complete:
        raise ValueError("route coverage complete count is stale")
    if summary.get("degraded_pairs") != degraded:
        raise ValueError("route coverage degraded count is stale")
    if "never invented identifiers" not in str(policy.get("route_outcome", "")):
        raise ValueError(
            "route coverage policy must forbid invented identifiers"
        )

    codes = {
        mode.get("code")
        for mode in modes
        if isinstance(mode, dict) and isinstance(mode.get("code"), str)
    }
    if codes != REQUIRED_PROBLEM_CODES:
        raise ValueError(
            "stable problem modes changed: "
            f"expected {sorted(REQUIRED_PROBLEM_CODES)}, got {sorted(codes)}"
        )


def _validate_runbook(root: Path) -> None:
    runbook = root / "docs" / "OPERATIONS_RUNBOOK.md"
    _require_file(runbook)
    text = runbook.read_text()
    missing = sorted(
        phrase for phrase in REQUIRED_RUNBOOK_PHRASES if phrase not in text
    )
    if missing:
        raise ValueError(f"operations runbook missing: {', '.join(missing)}")


def _validate_release_scripts(root: Path) -> None:
    makefile = root / "Makefile"
    _require_file(makefile)
    makefile_text = makefile.read_text()
    missing_targets = sorted(
        target
        for target in REQUIRED_MAKE_TARGETS
        if target not in makefile_text
    )
    if missing_targets:
        raise ValueError(
            f"Makefile missing targets: {', '.join(missing_targets)}"
        )
    for relative in REQUIRED_SCRIPT_PATHS:
        _require_file(root / relative)


def _validate_sboms(root: Path) -> None:
    sbom_root = root / "sbom"
    paths = {
        path.name: path
        for path in sbom_root.glob("*.cdx.json")
        if not path.name.startswith("._")
    }
    if set(paths) != REQUIRED_SBOMS:
        raise ValueError(
            f"SBOM inventory changed: expected {sorted(REQUIRED_SBOMS)}, "
            f"got {sorted(paths)}"
        )
    for name, path in paths.items():
        document = json.loads(path.read_text())
        if document.get("bomFormat") != "CycloneDX":
            raise ValueError(f"{name}: expected CycloneDX bomFormat")
        if document.get("specVersion") != "1.5":
            raise ValueError(f"{name}: expected CycloneDX 1.5")
        if "serialNumber" in document:
            raise ValueError(f"{name}: serialNumber must be normalized away")
        metadata = document.get("metadata")
        if not isinstance(metadata, dict) or "timestamp" in metadata:
            raise ValueError(f"{name}: timestamp must be normalized away")

    licenses = _load_json(root / "sbom" / "aeroroute-web-licenses.json")
    if not licenses:
        raise ValueError("web license inventory must not be empty")


def main() -> None:
    try:
        validate_phase14_release()
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print("Phase 14 release evidence is complete.")


if __name__ == "__main__":
    main()
