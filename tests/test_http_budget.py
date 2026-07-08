import pytest

from scripts.check_http_budget import percentile


def test_percentile_uses_nearest_rank() -> None:
    assert percentile([5, 1, 4, 2, 3], 0.95) == 5
    assert percentile([5, 1, 4, 2, 3], 0.50) == 3


def test_percentile_rejects_invalid_input() -> None:
    with pytest.raises(ValueError):
        percentile([], 0.95)
