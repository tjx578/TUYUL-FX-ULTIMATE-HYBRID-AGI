from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


@dataclass(frozen=True)
class FusionOutput:
    fundamental_score: float
    volatility_index: float
    weekly_regime: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "fundamental_score": self.fundamental_score,
            "volatility_index": self.volatility_index,
            "weekly_regime": self.weekly_regime,
        }


@dataclass(frozen=True)
class FusionSynthesis:
    fusion_integrity: float
    alignment_score: float
    fusion_summary: str
    macro_theme: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "fusion_integrity": self.fusion_integrity,
            "alignment_score": self.alignment_score,
            "fusion_summary": self.fusion_summary,
            "macro_theme": self.macro_theme,
        }


class FusionIntegrator:
    """
    Layer 12 macro-context integrator.

    The integrator simulates macro and micro signals to prepare inputs for the downstream
    reflective fusion pipeline.
    """

    def __init__(
        self, macro_signals: Sequence[float] | None = None, risk_sentiment: float = 0.52
    ):
        self.macro_signals = list(macro_signals) if macro_signals else [0.64, 0.58, 0.61]
        self.risk_sentiment = _clamp(risk_sentiment, 0.0, 1.0)

    def fuse_reflective_context(self) -> Dict[str, Any]:
        macro_bias = self._compute_macro_bias(self.macro_signals)
        fundamental_score = _clamp(0.52 + macro_bias * 0.3, 0.0, 1.0)
        volatility_index = _clamp(
            0.32 - macro_bias * 0.08 + (1 - self.risk_sentiment) * 0.05,
            0.05,
            0.95,
        )

        alignment_score = _clamp(
            72.0 + macro_bias * 14.0 + (1 - volatility_index) * 12.0,
            55.0,
            96.0,
        )
        fusion_integrity = round(
            _clamp(0.8 + alignment_score / 250 - volatility_index * 0.12, 0.65, 0.98), 3
        )

        weekly_regime = self._derive_weekly_regime(fundamental_score, volatility_index)
        macro_theme = self._macro_theme_from_regime(weekly_regime)
        fusion_summary = f"{weekly_regime.upper()} - Multi-asset blend"

        fusion_output = FusionOutput(
            fundamental_score=round(fundamental_score, 4),
            volatility_index=round(volatility_index, 4),
            weekly_regime=weekly_regime,
        )
        synthesis = FusionSynthesis(
            fusion_integrity=fusion_integrity,
            alignment_score=round(alignment_score, 2),
            fusion_summary=fusion_summary,
            macro_theme=macro_theme,
        )

        return {
            "status": "OK",
            "fusion_output": fusion_output.as_dict(),
            "synthesis": synthesis.as_dict(),
        }

    def _compute_macro_bias(self, signals: Sequence[float]) -> float:
        if not signals:
            return 0.0
        normalized = [_clamp(value, 0.0, 1.0) for value in signals]
        macro_bias = sum(normalized) / len(normalized)
        return _clamp(macro_bias, 0.0, 1.0)

    def _derive_weekly_regime(self, fundamental_score: float, volatility_index: float) -> str:
        if fundamental_score >= 0.62 and volatility_index < 0.35:
            return "Risk-on"
        if fundamental_score <= 0.45 or volatility_index > 0.55:
            return "Risk-off"
        return "Neutral"

    def _macro_theme_from_regime(self, regime: str) -> List[str]:
        if regime == "Risk-on":
            return ["Credit Bid", "JPY Dovish", "Carry Friendly"]
        if regime == "Risk-off":
            return ["USD Demand", "Oil Strength", "Defensive Flows"]
        return ["Balanced", "Range Trading", "Selective Risk"]
