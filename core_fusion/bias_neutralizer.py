from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


@dataclass(frozen=True)
class BiasNeutralizationResult:
    neutralized_bias: float
    bias_state: str
    reflective_coherence: float
    fusion_confidence: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "neutralized_bias": self.neutralized_bias,
            "bias_state": self.bias_state,
            "reflective_coherence": self.reflective_coherence,
            "fusion_confidence": self.fusion_confidence,
        }


class BiasNeutralizer:
    """
    Normalize fusion bias and derive reflective coherence for downstream Monte Carlo analysis.
    """

    def neutralize(
        self,
        *,
        fundamental_bias: float,
        fusion_bias: float,
        sentiment_index: float,
        volatility_index: float,
    ) -> BiasNeutralizationResult:
        normalized_fundamental = _clamp(fundamental_bias, 0.0, 1.0)
        normalized_fusion = _clamp(fusion_bias, 0.0, 1.0)
        normalized_sentiment = _clamp(sentiment_index, 0.0, 1.0)
        normalized_volatility = _clamp(volatility_index, 0.0, 1.0)

        blended_bias = (
            normalized_fundamental * 0.5
            + normalized_fusion * 0.3
            + normalized_sentiment * 0.2
        )
        volatility_dampener = 1 - normalized_volatility * 0.28
        neutralized_bias = _clamp(blended_bias * volatility_dampener, 0.0, 1.0)

        divergence_penalty = abs(normalized_fundamental - normalized_fusion) * 40
        reflective_coherence = _clamp(
            90 - divergence_penalty - normalized_volatility * 15,
            50,
            96,
        )
        fusion_confidence = _clamp(
            reflective_coherence * 0.92 + (1 - normalized_volatility) * 9,
            30,
            99,
        )

        bias_state = self._determine_bias_state(neutralized_bias)

        return BiasNeutralizationResult(
            neutralized_bias=round(neutralized_bias, 4),
            bias_state=bias_state,
            reflective_coherence=round(reflective_coherence, 2),
            fusion_confidence=round(fusion_confidence, 2),
        )

    def _determine_bias_state(self, neutralized_bias: float) -> str:
        if neutralized_bias >= 0.62:
            return "BULLISH"
        if neutralized_bias <= 0.38:
            return "BEARISH"
        return "NEUTRAL"
