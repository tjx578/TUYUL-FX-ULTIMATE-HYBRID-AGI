"""Concept Identifier – Enhanced AGI-aware concept detection."""
from __future__ import annotations

from typing import Dict, List

from core.agi.confidence_scorer import ConfidenceScorer


class ConceptIdentifier:
    """Identify trading concepts and score them with AGI feedback."""

    def __init__(self, scorer: ConfidenceScorer | None = None) -> None:
        self.confidence = scorer or ConfidenceScorer()

    def identify(self, data: Dict[str, float]) -> Dict[str, object]:
        """Detect active trading concepts from signal data."""

        concepts: List[str] = []
        price = float(data.get("price", 0.0))
        support = float(data.get("support_level", price))
        resistance = float(data.get("resistance_level", price))

        if data.get("momentum", 0.0) > 0.7:
            concepts.append("Bullish Momentum")
        if data.get("momentum", 0.0) < -0.7:
            concepts.append("Bearish Momentum")
        if data.get("volatility", 0.0) > 0.5:
            concepts.append("High Volatility Zone")
        if price <= support * 1.01:
            concepts.append("Support Retest")
        if price >= resistance * 0.99:
            concepts.append("Breakout Threat")
        if abs(data.get("divergence", 0.0)) > 0.6:
            concepts.append("Momentum Divergence")

        unique_concepts = sorted(set(concepts))
        score = self.confidence.calculate(len(unique_concepts))
        return {"concepts": unique_concepts, "confidence": score}

