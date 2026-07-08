import pytest

from scripts.verify_live_release import validate_scenario


def _fixture() -> tuple[dict[str, object], dict[str, object]]:
    scenario = {
        "name": "MAD-JFK",
        "expected": {
            "departure_runway": "36L",
            "sid": "BARD3N",
            "arrival_runway": "13R",
            "star": "PAWLN1",
            "alternate": "CYYZ",
            "minimum_diversions": 1,
        },
    }
    document = {
        "operationally_approved": False,
        "disclaimer": "Results are not an ICAO-fileable flight plan.",
        "optimization": {
            "terminal_selection": {
                "departure_runway": "36L",
                "sid_identifier": "BARD3N",
                "arrival_runway": "13R",
                "star_identifier": "PAWLN1",
                "airac_cycle": "2606",
            },
            "destination_alternate": {"icao_code": "CYYZ"},
            "enroute_diversions": [{"icao_code": "CYQX"}],
            "fuel_plan": {"mass_converged": True},
        },
    }
    return scenario, document


def test_live_release_validator_accepts_traceable_snapshot() -> None:
    scenario, document = _fixture()

    validate_scenario(scenario, document, "2606")


def test_live_release_validator_rejects_terminal_regression() -> None:
    scenario, document = _fixture()
    optimization = document["optimization"]
    optimization["terminal_selection"]["sid_identifier"] = "SYN-1"

    with pytest.raises(AssertionError, match="expected sid"):
        validate_scenario(scenario, document, "2606")
