from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reference" / "flight-plan-scenarios-2026-06-29.json"


def validate_scenario(
    scenario: dict[str, Any], document: dict[str, Any], airac_cycle: str
) -> None:
    expected = scenario["expected"]
    optimization = document["optimization"]
    terminal = optimization["terminal_selection"]
    alternate = optimization["destination_alternate"]
    diversions = optimization["enroute_diversions"]
    actual = {
        "departure_runway": terminal["departure_runway"],
        "sid": terminal["sid_identifier"],
        "arrival_runway": terminal["arrival_runway"],
        "star": terminal["star_identifier"],
        "alternate": alternate["icao_code"],
    }
    for key, value in actual.items():
        if value != expected[key]:
            raise AssertionError(
                f"{scenario['name']}: expected {key}={expected[key]}, got {value}"
            )
    if terminal["airac_cycle"] != airac_cycle:
        raise AssertionError(
            f"{scenario['name']}: AIRAC cycle changed to "
            f"{terminal['airac_cycle']}"
        )
    if len(diversions) < expected["minimum_diversions"]:
        raise AssertionError(
            f"{scenario['name']}: expected at least "
            f"{expected['minimum_diversions']} diversions, got {len(diversions)}"
        )
    if not optimization["fuel_plan"]["mass_converged"]:
        raise AssertionError(f"{scenario['name']}: fuel mass did not converge")
    if document["operationally_approved"]:
        raise AssertionError(
            f"{scenario['name']}: operational flag must be false"
        )
    if "not an ICAO-fileable" not in document["disclaimer"]:
        raise AssertionError(
            f"{scenario['name']}: mandatory disclaimer missing"
        )


def verify(base_url: str) -> None:
    manifest = json.loads(MANIFEST.read_text())
    for index, scenario in enumerate(manifest["scenarios"], start=1):
        payload = {
            **scenario["request"],
            "departure_time_utc": f"2026-06-30T{10 + index:02d}:00:00Z",
            "profile": "minimum_fuel",
            "extra_fuel_kg": 1_000,
            "callsign": f"VRF{index:03d}",
        }
        created = _json_request(
            f"{base_url}/api/v1/flight-plans", method="POST", payload=payload
        )
        validate_scenario(scenario, created, manifest["airac_cycle"])
        plan_id = created["flight_plan_id"]
        stored = _json_request(f"{base_url}/api/v1/flight-plans/{plan_id}")
        if stored["coded_route"] != created["coded_route"]:
            raise AssertionError(f"{scenario['name']}: stored route changed")
        pdf = _bytes_request(f"{base_url}/api/v1/flight-plans/{plan_id}/pdf")
        if not pdf.startswith(b"%PDF"):
            raise AssertionError(f"{scenario['name']}: invalid PDF export")
        print(f"PASS {scenario['name']} {plan_id}")


def _json_request(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
) -> dict[str, Any]:
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=60) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(
            f"{method} {url} failed: {error.code} {detail}"
        ) from error


def _bytes_request(url: str) -> bytes:
    with urlopen(url, timeout=30) as response:
        return response.read()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    arguments = parser.parse_args()
    verify(arguments.base_url.rstrip("/"))


if __name__ == "__main__":
    main()
