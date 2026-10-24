"""Additional behavior checks for Minh W3-2 log analysis."""

from collections import Counter


def test_analyse_groups_routes_and_uses_nearest_rank_p95() -> None:
    """Catch global percentiles, dropped counts and off-by-one ranks."""
    from members.mikaelvo639.w3.log_stats import analyse

    pairs = [("chat", float(n)) for n in range(20, 0, -1)] + [("search", 50.0), ("search", 100.0)]
    result = analyse(pairs)

    assert isinstance(result["counts"], Counter)
    assert result == {
        "counts": Counter({"chat": 20, "search": 2}),
        "p95": {"chat": 19.0, "search": 100.0},
        "slowest": "search",
    }
    assert pairs[0] == ("chat", 20.0)


def test_analyse_empty_input() -> None:
    """Catch percentile indexing on an empty log."""
    from members.mikaelvo639.w3.log_stats import analyse

    assert analyse([]) == {"counts": Counter(), "p95": {}, "slowest": None}


def test_analyse_singletons_and_ties() -> None:
    """Catch insertion-order-dependent selection of equally slow routes."""
    from members.mikaelvo639.w3.log_stats import analyse

    assert analyse([("z", 3.5), ("a", 3.5)]) == {
        "counts": Counter({"z": 1, "a": 1}),
        "p95": {"z": 3.5, "a": 3.5},
        "slowest": "a",
    }
