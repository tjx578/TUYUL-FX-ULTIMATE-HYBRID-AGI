"""Fusion Precision Engine v5.3+ core logic."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np

from core_reflective.reflective_logger import log_reflective_event
from server_api.services.cloud_logger_service import cloud_log_event


FUSION_LOG_PATH = Path("data/logs/fusion_precision_log.json")


class FusionPrecisionEngine:
    """Main fusion engine combining EMA, VWAP, and reflex factors."""

    def __init__(self, ema_fast: float = 21, ema_slow: float = 50) -> None:
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow

    def compute_fusion(
        self,
        price: float,
        ema_fast_val: float,
        ema_slow_val: float,
        vwap: float,
        atr: float,
        reflex_strength: float,
        volatility: float,
        rsi: float,
    ) -> Dict[str, Any]:
        """
        Compute fusion precision strength by blending:
        - EMA momentum
        - VWAP deviation
        - Reflex synchronization with volatility adjustment
        """

        if atr <= 0:
            return {"status": "invalid_atr"}

        ema_diff = ema_fast_val - ema_slow_val
        ema_ratio = ema_diff / (ema_slow_val + 1e-6)
        ema_strength = float(np.tanh(ema_ratio * 5.0))

        vwap_dev = (price - vwap) / (vwap if vwap else 1.0)
        vwap_signal = float(np.tanh(vwap_dev * 4.5))

        reflex_weight = float(np.clip(reflex_strength, -1.0, 1.0))
        volatility_adj = float(np.clip(1.0 - (volatility / (atr * 2.5)), 0.4, 1.0))
        fusion_raw = (
            (ema_strength * 0.45) + (vwap_signal * 0.35) + (reflex_weight * 0.2)
        )
        fusion_strength = fusion_raw * volatility_adj

        if rsi >= 65 and fusion_strength > 0:
            confidence = min(1.0, abs(fusion_strength) * 1.1)
        elif rsi <= 35 and fusion_strength < 0:
            confidence = min(1.0, abs(fusion_strength) * 1.1)
        else:
            confidence = abs(fusion_strength) * 0.8

        if fusion_strength > 0.25:
            bias_mode = "BULLISH"
        elif fusion_strength < -0.25:
            bias_mode = "BEARISH"
        else:
            bias_mode = "NEUTRAL"

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "fusion_strength": round(float(fusion_strength), 4),
            "confidence": round(float(confidence), 3),
            "ema_strength": round(float(ema_strength), 4),
            "vwap_signal": round(float(vwap_signal), 4),
            "reflex_weight": round(float(reflex_weight), 3),
            "volatility_adj": round(float(volatility_adj), 3),
            "bias_mode": bias_mode,
        }

        self._save_fusion_log(result)
        log_reflective_event("FUSION_PRECISION_CYCLE", result)
        cloud_log_event("fusion.precision", result)

        return result

    @staticmethod
    def _save_fusion_log(data: Dict[str, Any]) -> None:
        FUSION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(FUSION_LOG_PATH, "a", encoding="utf-8") as log_file:
            json.dump(data, log_file)
            log_file.write("\n")


if __name__ == "__main__":
    fusion = FusionPrecisionEngine()

    result = fusion.compute_fusion(
        price=1.0875,
        ema_fast_val=1.0854,
        ema_slow_val=1.0838,
        vwap=1.0860,
        atr=0.0018,
        reflex_strength=0.42,
        volatility=0.0015,
        rsi=62.0,
    )

    print("Fusion Precision Output:")
    print(json.dumps(result, indent=2))
