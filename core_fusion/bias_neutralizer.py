"""
⚖️ TUYUL FX – Bias Neutralizer Engine v5.3+

Layer 12.1 – Fusion Bias Stabilization Core

Tujuan:
--------
Menstabilkan bias makro & teknikal sebelum digunakan
oleh sistem reasoning reflektif (CONF₁₂ & L13 Meta Logic).

Input:
  - Fundamental bias score (L11.5)
  - Fusion bias output (L12)
  - Market sentiment index (VIX, WLWCI, etc.)

Output:
  - Neutralized bias (0.0–1.0)
  - Reflective Coherence Factor (0–100)
  - Final Fusion Confidence (CONF₁₂_adj)

Author : TUYUL-KARTEL-FX AGI Dev Team
Version: 5.3+
Date   : 2026-01-02
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict


# ===========================================================
# 🧩 Data Structure
# ===========================================================


@dataclass(slots=True)
class BiasNeutralizationResult:
    """Hasil perhitungan bias yang sudah dinetralisir"""

    neutralized_bias: float
    reflective_coherence: float
    fusion_confidence: float
    bias_state: str
    timestamp: str

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ===========================================================
# ⚙️ Bias Neutralizer Engine
# ===========================================================


class BiasNeutralizer:
    """Core Bias Neutralizer untuk Layer 12.1"""

    def __init__(self, *, damping_factor: float = 0.6, coherence_gain: float = 1.2):
        self.damping_factor = damping_factor
        self.coherence_gain = coherence_gain

    # -------------------------------------------------------
    def neutralize(
        self,
        fundamental_bias: float,
        fusion_bias: float,
        sentiment_index: float,
        *,
        volatility_index: float = 17.0,
    ) -> BiasNeutralizationResult:
        """
        Jalankan penetralan bias multi-layer.

        Args:
            fundamental_bias: Skor fundamental (0–1)
            fusion_bias: Skor fusion layer (0–1)
            sentiment_index: Skor sentimen pasar global (0–1)
            volatility_index: Indeks VIX (default 17.0)
        """

        # Step 1 — Hitung bias rata-rata dasar
        base_mean = (fundamental_bias + fusion_bias + sentiment_index) / 3
        volatility_factor = max(0.1, 1.0 - ((volatility_index - 15) * 0.03))
        damped = base_mean * self.damping_factor * volatility_factor

        # Step 2 — Hitung koherensi reflektif (RCF)
        coherence = self._compute_reflective_coherence(
            fundamental_bias, fusion_bias, sentiment_index
        )
        reflective_coherence = round(coherence * self.coherence_gain * 100, 2)

        # Step 3 — Hitung bias ter-normalisasi
        neutralized_bias = max(0.0, min(1.0, damped + (reflective_coherence / 1000)))
        bias_state = self._bias_state(neutralized_bias)

        # Step 4 — Hitung fusion confidence
        fusion_confidence = round(
            (neutralized_bias * 0.7 + (reflective_coherence / 100) * 0.3) * 100, 2
        )

        return BiasNeutralizationResult(
            neutralized_bias=round(neutralized_bias, 4),
            reflective_coherence=reflective_coherence,
            fusion_confidence=fusion_confidence,
            bias_state=bias_state,
            timestamp=datetime.utcnow().isoformat(),
        )

    # -------------------------------------------------------
    def _compute_reflective_coherence(self, f1: float, f2: float, s: float) -> float:
        """Koherensi reflektif antara 3 lapisan logika"""

        std_dev = math.sqrt(((f1 - f2) ** 2 + (f2 - s) ** 2 + (s - f1) ** 2) / 3)
        coherence = 1.0 - min(std_dev * 1.5, 1.0)
        return round(coherence, 4)

    # -------------------------------------------------------
    def _bias_state(self, val: float) -> str:
        """Tentukan kategori bias setelah dinetralisir"""

        if val >= 0.66:
            return "BULLISH"
        if val <= 0.33:
            return "BEARISH"
        return "NEUTRAL"


# ===========================================================
# 🧪 Test Mode
# ===========================================================

if __name__ == "__main__":
    print("🧠 TUYUL FX – Bias Neutralizer v5.3+ (Test Mode)")
    neutralizer = BiasNeutralizer(damping_factor=0.65, coherence_gain=1.1)

    # Sample test input
    result = neutralizer.neutralize(
        fundamental_bias=0.72,
        fusion_bias=0.68,
        sentiment_index=0.55,
        volatility_index=18.2,
    )

    print("\n--- Bias Neutralization Result ---")
    for k, v in result.as_dict().items():
        print(f"{k:25s}: {v}")
