from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def percentile(values: list[float], quantile: float) -> float:
    if not values:
        raise ValueError("values cannot be empty")
    if not 0 < quantile <= 1:
        raise ValueError("quantile must be in (0, 1]")
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * quantile) - 1)
    return ordered[index]


def measure(url: str, requests: int, concurrency: int) -> list[float]:
    def fetch(_: int) -> float:
        started = perf_counter()
        with urlopen(url, timeout=5) as response:
            if response.status != 200:
                raise RuntimeError(f"unexpected HTTP {response.status}")
            response.read()
        return (perf_counter() - started) * 1000

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        return list(executor.map(fetch, range(requests)))


def check(base_url: str, requests: int, concurrency: int) -> None:
    plans = _json_get(f"{base_url}/api/v1/flight-plans")
    if not plans:
        raise RuntimeError("at least one stored flight plan is required")
    cases = [
        (
            "airport_search",
            f"{base_url}/api/v1/airports?query=MAD&limit=8",
            150.0,
        ),
        (
            "flight_plan_read",
            f"{base_url}/api/v1/flight-plans/{plans[0]['flight_plan_id']}",
            200.0,
        ),
    ]
    for name, url, budget_ms in cases:
        measure(url, 3, 1)
        timings = measure(url, requests, concurrency)
        p95 = percentile(timings, 0.95)
        print(f"{name} p95={p95:.2f}ms budget={budget_ms:.0f}ms")
        if p95 > budget_ms:
            raise RuntimeError(f"{name} exceeded P95 budget")


def _json_get(url: str) -> list[dict[str, object]]:
    try:
        with urlopen(url, timeout=5) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read().decode(errors="replace")
        try:
            payload = json.loads(detail)
        except json.JSONDecodeError:
            payload = {}
        if (
            isinstance(payload, dict)
            and payload.get("code") == "database_unavailable"
        ):
            raise RuntimeError(
                "performance-live requires PostGIS. Start it with "
                "`make dev-up` in aeroroute-platform and run "
                "`uv run alembic upgrade head` in aeroroute-api first."
            ) from None
        raise RuntimeError(f"GET {url} failed: {error.code} {detail}") from None
    except URLError as error:
        raise RuntimeError(
            "performance-live requires aeroroute-api to be reachable."
        ) from error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--requests", type=int, default=30)
    parser.add_argument("--concurrency", type=int, default=6)
    arguments = parser.parse_args()
    try:
        check(
            arguments.base_url.rstrip("/"),
            arguments.requests,
            arguments.concurrency,
        )
    except RuntimeError as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
