"""Summarize request counts and per-route nearest-rank p95 latency."""

from collections import Counter, defaultdict
from math import ceil
from typing import TypedDict


class LogStats(TypedDict):
    """The three results required by the W3-2 analysis contract."""

    counts: Counter[str]
    p95: dict[str, float]
    slowest: str | None


def analyse(pairs: list[tuple[str, float]]) -> LogStats:
    """Count routes and compute p95 as sorted_values[ceil(0.95 * n) - 1].

    Empty input returns empty counts/percentiles and slowest=None. Equal p95
    values select the alphabetically first route. Input order is preserved.
    Latencies are assumed to be finite, nonnegative milliseconds.
    """
    counts: Counter[str] = Counter()
    latencies: defaultdict[str, list[float]] = defaultdict(list)
    for route, latency in pairs:
        counts[route] += 1
        latencies[route].append(latency)
    p95 = {route: sorted(values)[ceil(0.95 * len(values)) - 1] for route, values in latencies.items()}
    slowest = min(p95, key=lambda route: (-p95[route], route)) if p95 else None
    return {"counts": counts, "p95": p95, "slowest": slowest}
