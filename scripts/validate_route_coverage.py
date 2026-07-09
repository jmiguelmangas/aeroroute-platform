from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_PROBLEM_CODES = {
    "airport_not_supported",
    "navigation_provider_unavailable",
    "runway_procedure_coverage_missing",
}
REQUIRED_REFERENCE_PAIRS = {"MAD-JFK", "JFK-MAD", "DXB-MAD", "NRT-SFO"}


def validate_route_coverage(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("operationally_approved") is not False:
        raise ValueError("route coverage report must be non-operational")
    if len(str(report.get("airport_bundle_sha256", ""))) != 64:
        raise ValueError("route coverage report must pin an airport bundle")
    if not report.get("airac_cycle"):
        raise ValueError("route coverage report must pin an AIRAC cycle")

    pairs = report.get("reference_pairs", [])
    names = {pair.get("name") for pair in pairs}
    if names != REQUIRED_REFERENCE_PAIRS:
        raise ValueError(
            "route coverage report must include all reference pairs"
        )
    if report.get("summary", {}).get("evaluated_reference_pairs") != len(pairs):
        raise ValueError("route coverage summary does not match pair count")

    complete = 0
    degraded = 0
    for pair in pairs:
        if pair.get("preflight_status") != "supported":
            raise ValueError(f"{pair.get('name')}: preflight must be supported")
        status = pair.get("route_status")
        if status == "complete":
            complete += 1
            if pair.get("degradation", {}).get("present"):
                raise ValueError(
                    f"{pair.get('name')}: complete route is degraded"
                )
        elif status == "degraded":
            degraded += 1
            if not pair.get("degradation", {}).get("present"):
                raise ValueError(f"{pair.get('name')}: degradation missing")
        else:
            raise ValueError(f"{pair.get('name')}: invalid route status")
        terminal = pair.get("terminal_coverage", {})
        for key in ("departure_runway", "sid", "arrival_runway", "star"):
            value = str(terminal.get(key, ""))
            if not value or value.startswith("SYN-"):
                raise ValueError(f"{pair.get('name')}: invalid {key}")
        if int(pair.get("minimum_diversions", 0)) < 1:
            raise ValueError(f"{pair.get('name')}: diversion floor missing")

    summary = report.get("summary", {})
    if summary.get("complete_pairs") != complete:
        raise ValueError("complete pair summary does not match")
    if summary.get("degraded_pairs") != degraded:
        raise ValueError("degraded pair summary does not match")

    problem_codes = {
        problem.get("code")
        for problem in report.get("stable_problem_modes", [])
    }
    if problem_codes != REQUIRED_PROBLEM_CODES:
        raise ValueError("route coverage report problem modes are incomplete")
    if summary.get("stable_problem_modes") != len(problem_codes):
        raise ValueError("problem-mode summary does not match")
    return report


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    validate_route_coverage(
        root / "reference" / "supported-route-coverage-2026-07-09.json"
    )


if __name__ == "__main__":
    main()
