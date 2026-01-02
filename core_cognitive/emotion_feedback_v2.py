"""Emotion Feedback Engine v2.1r — Reflexive Emotional Stability Engine

This module provides the reflective emotional computation layer for TUYUL FX Ultimate
Hybrid AGI. It simulates emotional coherence, reaction latency, and psychological
confidence for reflective decision cycles (L3–L9).
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class EmotionFeedbackCycle:
    """Container for a single emotional feedback iteration."""

    coherence: float
    emotion_delta: float
    gate: str
    psych_confidence: float
    timestamp: float


class EmotionFeedbackEngine:
    """Simulates emotion–reflex coherence feedback cycles."""

    def __init__(
        self,
        *,
        baseline_emotion: float = 0.3,
        smoothing: float = 0.1,
        delay_reference_ms: float = 320.0,
        seed: int | None = None,
    ) -> None:
        self.baseline_emotion = baseline_emotion
        self.smoothing = max(0.0, min(smoothing, 1.0))
        self.delay_reference_ms = delay_reference_ms
        self._rng = random.Random(seed)
        self._last_cycle: Optional[EmotionFeedbackCycle] = None

    def _clamp(self, value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

    def _calc_coherence(
        self, emotion_now: float, focus_index: float, reaction_delay_ms: float
    ) -> float:
        """Compute the reflexive coherence level."""
        delay_factor = self._clamp(
            1.0 - abs(reaction_delay_ms - self.delay_reference_ms) / 500.0
        )
        base = 0.6 * focus_index + 0.4 * delay_factor
        coherence = self._clamp((emotion_now * 0.5 + base * 0.5), 0.0, 1.0)
        return round(coherence, 4)

    def _calc_emotion_delta(self, coherence: float, emotion_now: float) -> float:
        """Calculate emotional deviation from baseline."""
        delta = abs(emotion_now - (self.baseline_emotion + (coherence - 0.5) * 0.3))
        smoothed = self._clamp(delta * (1.0 - self.smoothing))
        return round(smoothed, 4)

    def _evaluate_gate(self, coherence: float, emotion_delta: float) -> str:
        """Classify gate state."""
        if coherence >= 0.85 and emotion_delta <= 0.25:
            return "PASS"
        if coherence >= 0.75 and emotion_delta <= 0.35:
            return "REVIEW"
        return "LOCKOUT"

    def _psych_confidence(self, coherence: float, emotion_delta: float) -> float:
        """Estimate psychological confidence."""
        confidence = (coherence * (1.0 - emotion_delta)) ** 0.8
        return round(self._clamp(confidence), 4)

    def run_cycle(
        self,
        *,
        emotion_now: float,
        focus_index: float,
        reaction_delay_ms: float,
    ) -> Dict[str, float | str]:
        """Run a single feedback cycle and return normalized metrics."""
        coherence = self._calc_coherence(emotion_now, focus_index, reaction_delay_ms)
        emotion_delta = self._calc_emotion_delta(coherence, emotion_now)
        gate = self._evaluate_gate(coherence, emotion_delta)
        psych_conf = self._psych_confidence(coherence, emotion_delta)

        self._last_cycle = EmotionFeedbackCycle(
            coherence=coherence,
            emotion_delta=emotion_delta,
            gate=gate,
            psych_confidence=psych_conf,
            timestamp=time.time(),
        )

        return {
            "coherence": coherence,
            "emotion_delta": emotion_delta,
            "gate": gate,
            "psych_confidence": psych_conf,
            "timestamp": self._last_cycle.timestamp,
        }

    def last_cycle(self) -> Optional[Dict[str, float | str]]:
        """Return the most recent feedback cycle, if available."""
        if not self._last_cycle:
            return None
        return {
            "coherence": self._last_cycle.coherence,
            "emotion_delta": self._last_cycle.emotion_delta,
            "gate": self._last_cycle.gate,
            "psych_confidence": self._last_cycle.psych_confidence,
            "timestamp": self._last_cycle.timestamp,
        }

    def reset(self) -> None:
        """Clear the stored emotional feedback state."""
        self._last_cycle = None
