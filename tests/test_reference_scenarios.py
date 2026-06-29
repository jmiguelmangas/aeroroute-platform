import json
from pathlib import Path


def test_flight_plan_release_scenarios_are_complete_and_real() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (
            root / "reference" / "flight-plan-scenarios-2026-06-29.json"
        ).read_text()
    )
    scenarios = manifest["scenarios"]

    assert manifest["operationally_approved"] is False
    assert manifest["airac_cycle"]
    assert len(manifest["airport_bundle_sha256"]) == 64
    assert {scenario["name"] for scenario in scenarios} == {
        "MAD-JFK",
        "JFK-MAD",
        "DXB-MAD",
        "NRT-SFO",
    }
    for scenario in scenarios:
        expected = scenario["expected"]
        identifiers = [expected["sid"], expected["star"]]
        assert all(
            identifier and not identifier.startswith("SYN-")
            for identifier in identifiers
        )
        assert expected["minimum_diversions"] >= 1
        assert expected["route_status"] in {"complete", "degraded"}
