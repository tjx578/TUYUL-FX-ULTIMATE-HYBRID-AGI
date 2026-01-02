"""Monte Carlo validation utilities."""

from __future__ import annotations

import random
import statistics
from typing import Sequence

__all__ = ["montecarlo_validate", "validate_with_montecarlo"]

_DEFAULT_SEED = 42


def _ensure_positive_iterations(iterations: int) -> None:
    if iterations <= 0:
        msg = "Number of Monte Carlo iterations must be positive"
        raise ValueError(msg)


def _ensure_results(data: Sequence[float]) -> None:
    if not data:
        msg = "Results sequence cannot be empty"
        raise ValueError(msg)


def montecarlo_validate(
    data: Sequence[float], iterations: int = 1_000, *, seed: int | None = _DEFAULT_SEED
) -> dict[str, float]:
    """Run a deterministic Monte Carlo bootstrap over the supplied returns."""

    _ensure_positive_iterations(iterations)
    _ensure_results(data)

    rng = random.Random(seed)
    simulations = [sum(rng.choices(data, k=len(data))) for _ in range(iterations)]
    mean_return = statistics.fmean(simulations)
    std_dev = statistics.pstdev(simulations)
    win_probability = sum(1 for value in simulations if value > 0) / iterations * 100

    return {
        "mean_return": round(mean_return, 4),
        "std_dev": round(std_dev, 4),
        "win_probability_%": round(win_probability, 2),
        "iterations": iterations,
    }


def validate_with_montecarlo(results: Sequence[float], runs: int = 1_000) -> dict[str, float]:
    """Backward compatible wrapper around :func:`montecarlo_validate`."""

    summary = montecarlo_validate(results, iterations=runs)
    return {
        "mean": summary["mean_return"],
        "stdev": summary["std_dev"],
        "win_probability_%": summary["win_probability_%"],
        "simulations": summary["iterations"],
    }
