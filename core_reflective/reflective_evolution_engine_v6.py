"""Minimal Reflective Evolution Engine v6 implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Mapping


@dataclass
class EvolutionSnapshot:
    """Structured REE snapshot for downstream consumers."""

    timestamp: str
    reflective_integrity: float
    meta_weights: Dict[str, float]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "reflective_integrity": self.reflective_integrity,
            "meta_weights": self.meta_weights,
        }


class ReflectiveEvolutionEngine:
    """Track reflective evolution feedback and provide normalized snapshots."""

    def __init__(self) -> None:
        self.snapshots: List[EvolutionSnapshot] = []

    def ingest_feedback(self, feedback: Mapping[str, Any]) -> EvolutionSnapshot:
        reflective_integrity = self._as_float(feedback.get("reflective_integrity"), default=0.0)
        weights = self._extract_weights(feedback)

        snapshot = EvolutionSnapshot(
            timestamp=self._timestamp(),
            reflective_integrity=round(reflective_integrity, 6),
            meta_weights=weights,
        )
        self.snapshots.append(snapshot)
        return snapshot

    def latest_snapshot(self) -> EvolutionSnapshot | None:
        if not self.snapshots:
            return None
        return self.snapshots[-1]

    @staticmethod
    def _extract_weights(payload: Mapping[str, Any]) -> Dict[str, float]:
        return {
            "alpha": ReflectiveEvolutionEngine._as_float(payload.get("alpha"), default=1.0),
            "beta": ReflectiveEvolutionEngine._as_float(payload.get("beta"), default=1.0),
            "gamma": ReflectiveEvolutionEngine._as_float(payload.get("gamma"), default=1.0),
        }

    @staticmethod
    def _as_float(value: Any, *, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _timestamp() -> str:
        return f"{datetime.utcnow().isoformat()}Z"
