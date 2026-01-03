from __future__ import annotations

import random
import statistics
from dataclasses import dataclass
from typing import Any, Dict, List


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


@dataclass(frozen=True)
class MonteCarloResult:
    mean_confidence: float
    reliability_score: float
    stability_index: float
    reflective_integrity: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "mean_confidence": self.mean_confidence,
            "reliability_score": self.reliability_score,
            "stability_index": self.stability_index,
            "reflective_integrity": self.reflective_integrity,
        }


class MonteCarloConfidence:
    """Run Monte Carlo simulations to estimate bias stability and reliability."""

    def __init__(self, simulations: int = 3000, seed: int | None = None) -> None:
        self.simulations = max(100, simulations)
        self.seed = seed if seed is not None else 42

    def run(
        self,
        *,
        base_bias: float,
        coherence: float,
        volatility_index: float,
        confidence_weight: float = 1.0,
    ) -> MonteCarloResult:
        rng = random.Random(self.seed)
        normalized_volatility = _clamp(volatility_index, 0.0, 1.0)
        normalized_coherence = _clamp(coherence / 100, 0.0, 1.0)
        weighted_bias = _clamp(base_bias * confidence_weight, 0.0, 1.0)

        samples = self._simulate_samples(
            rng=rng,
            weighted_bias=weighted_bias,
            coherence=normalized_coherence,
            volatility=normalized_volatility,
        )

        mean_confidence = statistics.fmean(samples)
        variance = statistics.pvariance(samples)

        reliability_score = _clamp(1 - variance * 3.5, 0.0, 1.0)
        stability_index = _clamp(
            (1 - variance) * 100 * (1 - normalized_volatility * 0.2),
            0.0,
            100.0,
        )
        reflective_integrity = _clamp(mean_confidence * reliability_score * 120, 0.0, 100.0)

        return MonteCarloResult(
            mean_confidence=round(mean_confidence, 4),
            reliability_score=round(reliability_score, 4),
            stability_index=round(stability_index, 2),
            reflective_integrity=round(reflective_integrity, 2),
        )

    def _simulate_samples(
        self,
        *,
        rng: random.Random,
        weighted_bias: float,
        coherence: float,
        volatility: float,
    ) -> List[float]:
        samples: List[float] = []
        volatility_sigma = 0.05 + volatility * 0.08
        coherence_lift = (coherence - 0.5) * 0.2

        for _ in range(self.simulations):
            perturbation = rng.gauss(0.0, volatility_sigma)
            sample = weighted_bias + coherence_lift + perturbation
            bounded_sample = _clamp(sample, 0.0, 1.0)
            samples.append(bounded_sample)

        return samples
