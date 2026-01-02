"""Reflex emotion computation utilities."""

from __future__ import annotations

import random
from dataclasses import dataclass

from core.emotion_feedback_v2 import EmotionFeedbackEngine

__all__ = [
    "ReflexEmotionResult",
    "ReflexEmotionCore",
    "compute_reflex_emotion",
    "evaluate_emotion",
    "reflex_check",
]


@dataclass(frozen=True)
class ReflexEmotionResult:
    """Encapsulates reflex coherence metrics."""

    reflex_coherence: float
    emotion_delta: float
    alignment: str


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def compute_reflex_emotion(
    stimulus: float | None = None, *, rng: random.Random | None = None
) -> ReflexEmotionResult:
    """Compute reflex coherence from an optional stimulus value."""

    generator = rng or random.Random()
    base_value = stimulus if stimulus is not None else generator.random()
    coherence = _clamp(0.5 + (base_value - 0.5) * 1.2, 0.0, 1.0)
    emotion_delta = round(1.0 - coherence * 0.6, 4)
    alignment = "SYNCED" if coherence >= 0.75 and emotion_delta <= 0.35 else "DESYNCED"
    return ReflexEmotionResult(
        reflex_coherence=round(coherence, 4),
        emotion_delta=emotion_delta,
        alignment=alignment,
    )


def reflex_check(reflex_coherence: float, emotion_delta: float) -> str:
    """Evaluate whether the reflex-emotion gate is passable."""

    if reflex_coherence >= 0.8 and emotion_delta <= 0.3:
        return "PASS"
    if reflex_coherence >= 0.75 and emotion_delta <= 0.35:
        return "REVIEW"
    return "LOCKOUT"


def evaluate_emotion(state: str) -> str:
    """Return placeholder emotion evaluation string for backwards compatibility."""

    return f"emotion evaluation pending: {state}"


class ReflexEmotionCore:
    """Bridge reflex metrics to the emotion feedback engine."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.feedback = EmotionFeedbackEngine(
            baseline_emotion=self.config.get("baseline_emotion", 0.25),
            smoothing=self.config.get("emotion_smoothing", 0.1),
            delay_reference_ms=self.config.get("reflex_delay_reference_ms", 320.0),
        )

    def get_metrics(
        self,
        *,
        fallback_reaction_delay_ms: float = 310.0,
        fallback_emotion_level: float = 0.35,
        fallback_focus_index: float = 0.72,
    ) -> tuple[float, float]:
        """Return the latest reflex coherence and emotion delta metrics.

        The method first attempts to reuse the most recent cycle computed by
        the underlying :class:`EmotionFeedbackEngine`. If the core has not been
        primed yet, a fallback cycle is executed using conservative defaults to
        provide sane metrics for downstream consumers.
        """

        if hasattr(self.feedback, "last_cycle"):
            last_cycle = self.feedback.last_cycle()
            if last_cycle:
                return (
                    float(last_cycle["coherence"]),
                    float(last_cycle["emotion_delta"]),
                )

        cycle = self.feedback.run_cycle(
            emotion_now=fallback_emotion_level,
            focus_index=fallback_focus_index,
            reaction_delay_ms=fallback_reaction_delay_ms,
        )
        return float(cycle["coherence"]), float(cycle["emotion_delta"])

    def evaluate_reflex(
        self,
        *,
        reaction_delay_ms: float,
        emotion_level: float,
        focus_index: float,
    ) -> dict[str, float | str]:
        """Run reflex evaluation and expose the normalized metrics."""

        result = self.feedback.run_cycle(
            emotion_now=emotion_level,
            focus_index=focus_index,
            reaction_delay_ms=reaction_delay_ms,
        )
        return {
            "reflex_coherence": result["coherence"],
            "emotion_delta": result["emotion_delta"],
            "gate": result["gate"],
            "psych_confidence": result["psych_confidence"],
        }
