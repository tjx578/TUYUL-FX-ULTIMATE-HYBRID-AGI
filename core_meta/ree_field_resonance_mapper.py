"""Map reflective field resonance into normalized stability metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ResonanceVector:
    alpha: float
    beta: float
    gamma: float

    @property
    def drift(self) -> float:
        return abs(self.alpha - 1.0) + abs(self.beta - 1.0) + abs(self.gamma - 1.0)


class REEFieldResonanceMapper:
    """Translate REE alpha/beta/gamma weights into resonance stability signals."""

    def __init__(self, base_resonance: float = 1.0) -> None:
        self.base_resonance = base_resonance

    def map_resonance(self, alpha: float, beta: float, gamma: float) -> Dict[str, float | str]:
        weights = self._normalize(alpha, beta, gamma)
        stability = self._calculate_stability(weights)
        lorentzian_phase = round(weights.gamma + (weights.alpha - weights.beta), 3)
        state = self._derive_state(stability, lorentzian_phase)

        return {
            "state": state,
            "stability": stability,
            "lorentzian_phase": lorentzian_phase,
        }

    def _normalize(self, alpha: float, beta: float, gamma: float) -> ResonanceVector:
        return ResonanceVector(
            alpha=float(alpha) if alpha is not None else self.base_resonance,
            beta=float(beta) if beta is not None else self.base_resonance,
            gamma=float(gamma) if gamma is not None else self.base_resonance,
        )

    @staticmethod
    def _calculate_stability(weights: ResonanceVector) -> float:
        drift = weights.drift
        stability = 1.0 - min(1.0, drift * 0.8)
        return round(max(0.0, min(1.0, stability)), 6)

    @staticmethod
    def _derive_state(stability: float, lorentzian_phase: float) -> str:
        if stability >= 0.9 and 0.5 <= lorentzian_phase <= 1.5:
            return "harmonic"
        if stability >= 0.8:
            return "modulated"
        if lorentzian_phase < 0.5 or lorentzian_phase > 1.5:
            return "turbulent"
        return "attenuated"
