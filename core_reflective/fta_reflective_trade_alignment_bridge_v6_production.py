"""
🧠 TUYUL FX ULTIMATE — FTA–Reflective Trade Alignment Bridge v6.0r∞
Layer 14: Trade Bias Consolidation before Plan Generation

Menghubungkan:
- FTAIntegrationEngine (Layer 7–10)
- ReflectiveCycleManager (Layer 11–12)
- RTPG (Layer 15)

Output:
- Final Bias Strength
- Trade Mode (ACCUMULATION, DISTRIBUTION, EXPANSION)
- Confidence Index
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


BRIDGE_LOG_PATH = "data/logs/reflective_trade_alignment_log.json"


class FTAReflectiveTradeAlignmentBridge:
    """FTA–Reflective Trade Alignment Consolidator (Layer-14)."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.neural = NeuralConnector(
            RepoMetadata(
                repo_id="fta-trade-align-001",
                repo_name="FTA–Reflective Trade Alignment Bridge",
                repo_type="alignment_bridge",
                version="6.0r∞",
                layer="L14",
                capabilities=[],
            ),
            redis_url=redis_url,
            channel_prefix="tuyul_neural",
        )

    async def start(self):
        await self.neural.connect()

    async def stop(self):
        await self.neural.disconnect()

    # ================================================================
    # MAIN ALIGNMENT LOGIC
    # ================================================================

    def consolidate_alignment(
        self,
        fta_alignment_index: float,
        fta_confidence: float,
        reflective_bias: float,
        trade_integrity_index: float,
        coherence_index: float,
    ) -> Dict[str, Any]:
        """
        Satukan FTA + Reflective + Integrity untuk final bias.
        Semua input berada dalam range [-1, 1] kecuali confidence [0–1].
        """

        weighted_bias = (
            (fta_alignment_index * 0.45)
            + (reflective_bias * 0.35)
            + (trade_integrity_index * 0.15)
            + (coherence_index * 0.05)
        )

        confidence = np.clip(abs(weighted_bias) * fta_confidence, 0, 1)
        regime_state = (
            "EXPANSION"
            if confidence > 0.75
            else "ACCUMULATION"
            if confidence > 0.5
            else "DISTRIBUTION"
        )

        trade_mode = (
            "BUY" if weighted_bias > 0.25 else "SELL" if weighted_bias < -0.25 else "WAIT"
        )

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "weighted_bias": round(float(weighted_bias), 4),
            "confidence": round(float(confidence), 3),
            "regime_state": regime_state,
            "trade_mode": trade_mode,
            "integrity_reference": round(float(trade_integrity_index), 4),
            "coherence_reference": round(float(coherence_index), 4),
        }

        self._save_log(result)
        log_reflective_event("FTA_TRADE_ALIGNMENT", result)
        cloud_log_event("fta.reflective_alignment", result)

        return result

    # ================================================================
    # BROADCAST TO TRADE PLAN (Layer-15)
    # ================================================================

    async def broadcast_to_tradeplan(self, result: Dict[str, Any]) -> None:
        """
        Kirim hasil alignment ke Layer-15 (RTPG) via NeuralConnector.
        """
        payload = {
            "bias_strength": result["weighted_bias"],
            "confidence": result["confidence"],
            "trade_mode": result["trade_mode"],
            "regime_state": result["regime_state"],
            "timestamp": result["timestamp"],
        }

        await self.neural.publish(
            event_type=NeuralEventType.SIGNAL_GENERATED,
            payload=payload,
        )

        log_reflective_event("FTA_TRADE_BROADCAST", payload)
        cloud_log_event("fta.trade_broadcast", payload)

    # ================================================================
    # UTILITY
    # ================================================================

    @staticmethod
    def _save_log(data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(BRIDGE_LOG_PATH), exist_ok=True)
        with open(BRIDGE_LOG_PATH, "a", encoding="utf-8") as file:
            json.dump(data, file)
            file.write("\n")


# ======================================================================
# LOCAL EXECUTION DEMO
# ======================================================================

if __name__ == "__main__":
    import asyncio

    bridge = FTAReflectiveTradeAlignmentBridge()

    async def run_demo():
        await bridge.start()
        result = bridge.consolidate_alignment(
            fta_alignment_index=0.68,
            fta_confidence=0.74,
            reflective_bias=0.52,
            trade_integrity_index=0.83,
            coherence_index=0.67,
        )
        await bridge.broadcast_to_tradeplan(result)
        print("🎯 Final Trade Alignment Result:\n", json.dumps(result, indent=2))
        await bridge.stop()

    asyncio.run(run_demo())
