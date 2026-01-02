"""
🧠 TUYUL FX ULTIMATE — TWMS–EMA–FRPC Neural Integration v6.0r∞
Layer 8–10 Reflective Momentum Analyzer

Fungsi utama:
- Hitung TWMS + EMA multi-layer (20/50/200)
- Integrasi FRPC (Fusion Reflective Propagation Coefficient)
- Kirim hasil ke Reflective Engine via NeuralConnector
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict

import numpy as np

from core_meta.neural_connector_v6_production import (
    NeuralConnector,
    NeuralEventType,
    RepoMetadata,
)
from core_reflective.reflective_logger import log_reflective_event
from server_api.services.cloud_logger_service import cloud_log_event

TWMS_LOG_PATH = "data/logs/ema_smc_fusion_log.json"


class TWMSEMAStrengthAnalyzer:
    """TWMS–EMA–FRPC Integrator (Layer 8–10)."""

    def __init__(self, redis_url: str = "redis://localhost:6379") -> None:
        self.neural = NeuralConnector(
            RepoMetadata(
                repo_id="core-twms-ema-001",
                repo_name="TWMS–EMA Strength Engine",
                repo_type="fusion",
                version="6.0r∞",
                layer="L8",
                capabilities=[],
            ),
            redis_url=redis_url,
            channel_prefix="tuyul_neural",
        )

    async def start(self) -> None:
        """Mulai koneksi ke jaringan Neural TUYUL."""
        await self.neural.connect()

    async def stop(self) -> None:
        """Matikan koneksi ke Neural Network."""
        await self.neural.disconnect()

    def compute_strength(
        self,
        ema20: float,
        ema50: float,
        ema200: float,
        price: float,
        volume: float,
        volatility: float,
        wlwci: float,
    ) -> Dict[str, Any]:
        """Hitung kekuatan TWMS–EMA + WLWCI Reflective Bias."""

        if any(value <= 0 for value in [ema20, ema50, ema200, price, volume]):
            return {"status": "invalid_input"}

        ema_diff_short = (ema20 - ema50) / ema50
        ema_diff_long = (ema50 - ema200) / ema200
        ema_trend_bias = np.tanh((ema_diff_short + ema_diff_long) * 3)

        momentum_weight = np.log1p(volume) * (volatility + 1)
        wl_coherence = wlwci * 0.7 + ema_trend_bias * 0.3

        twms_strength = np.clip(
            (ema_trend_bias * 0.6 + wl_coherence * 0.4) * momentum_weight,
            -3.0,
            3.0,
        )

        trend_state = (
            "BULLISH"
            if twms_strength > 0.8
            else "BEARISH"
            if twms_strength < -0.8
            else "NEUTRAL"
        )

        result: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "twms_strength": round(float(twms_strength), 4),
            "ema_trend_bias": round(float(ema_trend_bias), 4),
            "wl_coherence": round(float(wl_coherence), 4),
            "trend_state": trend_state,
            "ema20": ema20,
            "ema50": ema50,
            "ema200": ema200,
            "volume": volume,
            "volatility": volatility,
            "wlwci": wlwci,
        }

        self._save_log(result)
        log_reflective_event("TWMS_EMA_STRENGTH", result)
        cloud_log_event("fusion.twms_ema_strength", result)
        return result

    async def export_frpc(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ekspor TWMS hasil ke FRPC Layer (L10 Reflective Propagation)."""
        payload = {
            "R3D_ENERGY": round(result["twms_strength"] * 1.1, 5),
            "GRADIENT": round(result["ema_trend_bias"], 5),
            "FRPC_PROP": (
                "50%"
                if abs(result["twms_strength"]) < 1.0
                else "75%"
                if abs(result["twms_strength"]) < 2.0
                else "90%"
            ),
            "trend_state": result["trend_state"],
            "timestamp": result["timestamp"],
        }

        log_reflective_event("FRPC_EXPORT", payload)
        cloud_log_event("frpc.propagation", payload)

        await self.neural.publish(
            event_type=NeuralEventType.REFLECTIVE_SYNC,
            payload=payload,
        )

        return payload

    @staticmethod
    def _save_log(data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(TWMS_LOG_PATH), exist_ok=True)
        with open(TWMS_LOG_PATH, "a", encoding="utf-8") as logfile:
            json.dump(data, logfile)
            logfile.write("\n")


if __name__ == "__main__":
    import asyncio

    async def run_test() -> None:
        analyzer = TWMSEMAStrengthAnalyzer()
        await analyzer.start()
        result = analyzer.compute_strength(
            ema20=1.1045,
            ema50=1.1032,
            ema200=1.0999,
            price=1.1050,
            volume=135000,
            volatility=0.0025,
            wlwci=0.873,
        )
        frpc = await analyzer.export_frpc(result)
        print("TWMS–EMA Result:", json.dumps(result, indent=2))
        print("FRPC Exported:", json.dumps(frpc, indent=2))
        await analyzer.stop()

    asyncio.run(run_test())
