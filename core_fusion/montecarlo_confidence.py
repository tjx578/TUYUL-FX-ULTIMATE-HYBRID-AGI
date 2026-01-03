"""
🎲 TUYUL FX – Monte Carlo Confidence Engine v5.3+

Layer 12.3 – Reflective Probability Core

Tujuan:
--------
Menjalankan simulasi Monte Carlo untuk mengukur keandalan bias
yang dihasilkan oleh Fusion dan Bias Neutralizer.

Output:
  - CONF₁₂ Monte Carlo score
  - Risk-Weighted Reliability (RWR)
  - Fusion Stability Index (FSI)

Author : TUYUL-KARTEL-FX AGI Dev Team
Version: 5.3+
Date   : 2026-01-02
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict


# ===========================================================
# 📈 Data Structure
# ===========================================================


@dataclass(slots=True)
class MonteCarloResult:
    """Hasil akhir simulasi Monte Carlo untuk fusion layer."""

    mean_confidence: float
    reliability_score: float
    stability_index: float
    total_simulations: int
    bias_mean: float
    volatility_mean: float
    reflective_integrity: float
    timestamp: str

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ===========================================================
# 🧩 Monte Carlo Confidence Engine
# ===========================================================


class MonteCarloConfidence:
    """Simulasi Monte Carlo untuk menilai konsistensi bias reflektif."""

    def __init__(self, simulations: int = 5000, seed: int | None = None):
        self.simulations = simulations
        self.random = random.Random(seed)

    # -------------------------------------------------------
    def run(
        self,
        *,
        base_bias: float,
        coherence: float,
        volatility_index: float,
        confidence_weight: float = 1.0,
    ) -> MonteCarloResult:
        """
        Jalankan simulasi ribuan kali untuk mengestimasi keandalan bias.

        Args:
            base_bias: bias netral hasil dari BiasNeutralizer (0–1)
            coherence: reflective coherence factor (0–100)
            volatility_index: indeks VIX (10–40)
            confidence_weight: bobot keyakinan reflektif (default=1.0)
        """

        samples: list[float] = []
        vol_samples: list[float] = []

        for _ in range(self.simulations):
            noise = self.random.gauss(0, 0.08)
            volatility_effect = max(0.4, 1 - (volatility_index - 15) * 0.03)
            adjusted = base_bias + (noise * volatility_effect)
            normalized = max(0.0, min(1.0, adjusted))
            samples.append(normalized)
            vol_samples.append(volatility_effect)

        mean_conf = round(sum(samples) / len(samples), 4)
        bias_mean = round(base_bias, 4)
        volatility_mean = round(sum(vol_samples) / len(vol_samples), 4)

        std_dev = math.sqrt(sum([(x - mean_conf) ** 2 for x in samples]) / len(samples))
        reliability_score = round(max(0.0, 1.0 - std_dev * 3.5), 4)

        stability_index = round(
            (reliability_score * 0.6 + (coherence / 100) * 0.4) * 100,
            2,
        )

        reflective_integrity = round(
            ((mean_conf * reliability_score) * confidence_weight) * 100,
            2,
        )

        return MonteCarloResult(
            mean_confidence=mean_conf,
            reliability_score=reliability_score,
            stability_index=stability_index,
            total_simulations=self.simulations,
            bias_mean=bias_mean,
            volatility_mean=volatility_mean,
            reflective_integrity=reflective_integrity,
            timestamp=datetime.utcnow().isoformat(),
        )


# ===========================================================
# 🧪 Test Mode
# ===========================================================

if __name__ == "__main__":
    print("🎲 TUYUL FX – Monte Carlo Confidence Engine v5.3+ (Test Mode)")

    engine = MonteCarloConfidence(simulations=5000, seed=42)
    result = engine.run(
        base_bias=0.58,
        coherence=83.5,
        volatility_index=18.7,
        confidence_weight=1.1,
    )

    print("\n--- Monte Carlo Simulation Result ---")
    for k, v in result.as_dict().items():
        print(f"{k:25s}: {v}")
