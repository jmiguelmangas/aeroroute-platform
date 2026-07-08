import pytest

from scripts.check_http_budget import _json_get, percentile


def test_percentile_uses_nearest_rank() -> None:
    assert percentile([5, 1, 4, 2, 3], 0.95) == 5
    assert percentile([5, 1, 4, 2, 3], 0.50) == 3


def test_percentile_rejects_invalid_input() -> None:
    with pytest.raises(ValueError):
        percentile([], 0.95)


def test_http_budget_reports_unreachable_api() -> None:
    with pytest.raises(RuntimeError, match="aeroroute-api"):
        _json_get("http://127.0.0.1:9/api/v1/flight-plans")
