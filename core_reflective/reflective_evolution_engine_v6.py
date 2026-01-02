from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from core_reflective.reflective_logger import ReflectiveLogger, log_reflective_event


REFLECTIVE_HISTORY_PATH = Path("data/logs/ree_feedback_history.jsonl")


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


@dataclass
class FeedbackSnapshot:
    pair: str
    reflective_integrity: float
    meta_state: str
    alpha: float
    beta: float
    gamma: float
    bias: str
    source_timestamp: str
    evaluated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pair": self.pair,
            "reflective_integrity": self.reflective_integrity,
            "meta_state": self.meta_state,
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
            "bias": self.bias,
            "source_timestamp": self.source_timestamp,
            "evaluated_at": self.evaluated_at,
        }


class ReflectiveEvolutionEngine:
    """Layer-17 engine that tunes adaptive weights from feedback cycles."""

    def __init__(
        self,
        history_path: Path = REFLECTIVE_HISTORY_PATH,
        logger: Optional[ReflectiveLogger] = None,
    ) -> None:
        self.history_path = history_path
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logger or ReflectiveLogger("REE.Engine")

    def run_feedback_cycle(
        self,
        pair: str,
        fusion_conf: float,
        fundamental_score: float,
        bias: str,
        timestamp: str,
    ) -> Dict[str, Any]:
        integrity = self._compute_reflective_integrity(fusion_conf, fundamental_score)
        meta_state = self._derive_meta_state(integrity)
        alpha, beta, gamma = self._update_adaptive_coefficients(integrity, bias)

        snapshot = FeedbackSnapshot(
            pair=pair,
            reflective_integrity=integrity,
            meta_state=meta_state,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            bias=bias,
            source_timestamp=timestamp,
            evaluated_at=datetime.now(timezone.utc).isoformat(),
        )

        self._persist(snapshot)
        self.logger.info(
            (
                "REE feedback | %s | integrity=%.3f | state=%s | α=%.3f β=%.3f γ=%.3f"
            )
            % (
                pair,
                snapshot.reflective_integrity,
                snapshot.meta_state,
                snapshot.alpha,
                snapshot.beta,
                snapshot.gamma,
            )
        )
        log_reflective_event("REE_FEEDBACK", snapshot.to_dict())
        return snapshot.to_dict()

    @staticmethod
    def _compute_reflective_integrity(
        fusion_conf: float, fundamental_score: float
    ) -> float:
        weighted = (fusion_conf * 0.65) + (fundamental_score * 0.35)
        baseline = 0.55 + (weighted - 0.5) * 0.6
        return round(_clamp(baseline, 0.0, 1.0), 3)

    @staticmethod
    def _derive_meta_state(integrity: float) -> str:
        if integrity >= 0.9:
            return "synchronized"
        if integrity >= 0.75:
            return "coherent"
        if integrity >= 0.5:
            return "learning"
        return "drift_detected"

    @staticmethod
    def _update_adaptive_coefficients(
        integrity: float, bias: str
    ) -> tuple[float, float, float]:
        bias_shift = 0.03 if bias.upper().startswith("BULL") else -0.03
        adaptive_gain = 1.0 + (integrity - 0.5) * 0.4
        alpha = _clamp(adaptive_gain + bias_shift, 0.85, 1.2)
        beta = _clamp(1.0 - (integrity - 0.5) * 0.25, 0.8, 1.1)
        gamma = _clamp(adaptive_gain + (bias_shift * 0.5), 0.85, 1.25)
        return round(alpha, 3), round(beta, 3), round(gamma, 3)

    def _persist(self, snapshot: FeedbackSnapshot) -> None:
        with open(self.history_path, "a", encoding="utf-8") as handle:
            json.dump(snapshot.to_dict(), handle, ensure_ascii=False)
            handle.write("\n")
