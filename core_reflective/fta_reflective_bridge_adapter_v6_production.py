"""
🌐 FTA–Reflective Bridge Adapter v6.0
=========================================================
Bridge layer yang menghubungkan hasil FTA Engine (Tuyul Kartel FX)
dengan sistem reflektif TUYUL ULTIMATE Layer 12–16.
=========================================================
Author: Wolf Alpha Analyst
Version: v6.0r∞ Production
Last Update: January 2026
"""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict

from core_reflective.fusion_reflective_propagation_coefficient_v6_production import (
    FusionReflectivePropagationCoefficient,
)
from core_reflective.reflective_cycle_manager import ReflectiveCycleManager
from core_reflective.reflective_logger import ReflectiveLogger


class FTAReflectiveBridgeAdapter:
    """
    🌉 Bridge adapter untuk mentransfer output FTA (fundamental–technical alignment)
    menjadi input koherensi reflektif untuk Layer 12–16.
    """

    def __init__(self, reflective_cycle: ReflectiveCycleManager | None = None):
        self.version = "6.0r∞"
        self.reflective_cycle = reflective_cycle or ReflectiveCycleManager()
        self.frpc = FusionReflectivePropagationCoefficient()
        self.logger = ReflectiveLogger("fta_reflective_bridge")
        self.output_path = Path("data/logs/fta_reflective_bridge_log.json")

    def load_fta_output(self, fta_output: Dict[str, Any]) -> Dict[str, Any]:
        """Memvalidasi struktur data hasil FTA Engine."""

        required_keys = ["fta_alignment", "confidence_multiplier", "entry_signals"]
        for key in required_keys:
            if key not in fta_output:
                raise ValueError(f"❌ Missing required key in FTA output: {key}")

        return {
            "pair": fta_output["header"]["pair"],
            "fta_score": fta_output["fta_alignment"]["fta_score"],
            "fta_bias": fta_output["fta_alignment"]["alignment_matrix"],
            "fta_confidence": fta_output["fta_alignment"]["fta_confidence"],
            "confidence_level": fta_output["confidence_multiplier"]["status"],
            "direction": fta_output["entry_signals"]["direction"],
            "entry_price": fta_output["entry_signals"]["entry_price"],
            "stop_loss": fta_output["entry_signals"]["stop_loss"],
            "timestamp": fta_output["header"]["timestamp"],
        }

    def propagate_to_reflective(self, fta_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔁 Meneruskan hasil FTA ke Reflective Cycle Manager & FRPC system.
        """

        pair = fta_data["pair"]
        fta_score = fta_data["fta_score"]

        reflective_input = {
            "pair": pair,
            "fta_score": fta_score,
            "confidence": fta_data["fta_confidence"],
            "direction": fta_data["direction"],
            "entry_price": fta_data["entry_price"],
            "bias": fta_data["fta_bias"],
            "timestamp": fta_data["timestamp"],
        }

        frpc_result = self.frpc.calculate_frpc(pair=pair, fta_score=fta_score)

        cycle_result = self.reflective_cycle.run_cycle(
            pair=pair,
            fta_score=fta_score,
            frpc_coefficient=frpc_result["frpc_coefficient"],
            direction=fta_data["direction"],
            timestamp=fta_data["timestamp"],
        )

        combined_result = {
            "pair": pair,
            "fta_score": fta_score,
            "fta_confidence": fta_data["fta_confidence"],
            "frpc_coefficient": frpc_result["frpc_coefficient"],
            "reflective_output": cycle_result,
            "timestamp": fta_data["timestamp"],
            "bridge_status": "✅ Propagated to Reflective System",
        }

        self._log_bridge_event(combined_result)
        return combined_result

    def _log_bridge_event(self, data: Dict[str, Any]) -> None:
        """Simpan log ke file runtime."""

        record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event": "FTA_REFLECTIVE_BRIDGE_UPDATE",
            "data": data,
        }
        os.makedirs(self.output_path.parent, exist_ok=True)
        with open(self.output_path, "a", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False)
            f.write("\n")

        self.logger.info(f"🔗 Bridge update logged for {data['pair']}")

    def bridge(self, fta_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 Jalankan proses bridging penuh (FTA → Reflective → FRPC)
        """

        validated = self.load_fta_output(fta_output)
        return self.propagate_to_reflective(validated)


if __name__ == "__main__":
    from tuyul_fx_ultimate_hybrid_agi.core_fusion.fundamental_technical_adapter import (
        TuyulKartelFXv3,
    )

    engine = TuyulKartelFXv3()
    fta_output = engine.run_example()

    bridge = FTAReflectiveBridgeAdapter()
    result = bridge.bridge(fta_output)

    print("\n=== 🔁 Bridge Result ===")
    print(json.dumps(result, indent=2))
