"""
⚙️ Adaptive Threshold Controller v6 — TUYUL FX Ultimate
-------------------------------------------------------
Menyesuaikan ambang batas Fusion Engine secara dinamis berdasarkan:
- FRPC Drift (field feedback)
- Market volatility real-time
- Reflective bias & confidence gradient

Terintegrasi dengan Cloud Run + Reflective Bridge Manager.
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict

import yaml

from core_reflective.reflective_logger import log_reflective_event
from server_api.services.cloud_logger_service import cloud_log_event

CONFIG_PATH = os.path.join("core_fusion", "configs", "fusion_thresholds.yml")
FRPC_LOG_PATH = os.path.join("data", "integrity", "frpc_drift_log.json")
OUTPUT_LOG_PATH = os.path.join("data", "logs", "fusion_adaptive_log.json")


class AdaptiveThresholdController:
    """Runtime optimizer for Fusion thresholds (Layer 12 Controller)."""

    def __init__(self) -> None:
        self.last_update_time = None
        self.update_interval = 60  # seconds
        self.thresholds: Dict[str, float] = {}

    # =====================================================
    # MAIN CONTROL LOGIC
    # =====================================================

    async def update_thresholds(self) -> Dict[str, float] | None:
        """Main loop for adaptive recalibration."""
        frpc_data = self._load_frpc_drift()
        current_time = datetime.utcnow().isoformat()

        if not frpc_data:
            print("⚠️ FRPC data not available — skipping adaptive update.")
            return None

        # === Compute adaptive parameters
        frpc_gradient = float(frpc_data.get("gradient", 0.0))
        mean_energy = float(frpc_data.get("mean_energy", 0.0))
        integrity_index = float(frpc_data.get("integrity_index", 1.0))

        # === Define dynamic adjustment
        adjustment_factor = 1.0 + (frpc_gradient * 0.5)
        volatility_adjustment = max(0.9, min(1.1, integrity_index))

        # === Apply new adaptive thresholds
        new_thresholds = {
            "ema_alignment_weight": round(0.75 * adjustment_factor, 3),
            "vwap_sensitivity": round(1.25 * volatility_adjustment, 3),
            "reflex_confidence_multiplier": round(mean_energy / 3.0, 3),
            "fusion_precision_tolerance": round(0.02 * (1 + abs(frpc_gradient)), 4),
        }

        # Save to file + Cloud + Reflective
        self._write_config(new_thresholds)
        await self._log_update(new_thresholds, current_time)

        print(f"✅ Adaptive thresholds updated @ {current_time}")
        return new_thresholds

    # =====================================================
    # FILE HANDLERS
    # =====================================================

    def _load_frpc_drift(self) -> Dict[str, Any]:
        """Load latest FRPC drift data."""
        try:
            if not os.path.exists(FRPC_LOG_PATH):
                return {}
            with open(FRPC_LOG_PATH, "r", encoding="utf-8") as frpc_log:
                return json.load(frpc_log)
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Failed to read FRPC drift log: {exc}")
            return {}

    def _write_config(self, thresholds: Dict[str, Any]) -> None:
        """Write new thresholds into YAML config file."""
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as config_file:
                yaml.dump(thresholds, config_file, default_flow_style=False)
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Failed to write new config: {exc}")

    # =====================================================
    # CLOUD & REFLECTIVE LOGGING
    # =====================================================

    async def _log_update(self, thresholds: Dict[str, Any], timestamp: str) -> None:
        """Sync adaptive results to cloud & reflective system."""
        log_entry = {
            "timestamp": timestamp,
            "adaptive_thresholds": thresholds,
        }

        # === Local log
        os.makedirs(os.path.dirname(OUTPUT_LOG_PATH), exist_ok=True)
        with open(OUTPUT_LOG_PATH, "a", encoding="utf-8") as output_log:
            json.dump(log_entry, output_log)
            output_log.write("\n")

        # === Cloud Log
        cloud_log_event("fusion.adaptive_update", log_entry)

        # === Reflective Bridge Sync
        log_reflective_event("ADAPTIVE_THRESHOLD_UPDATE", log_entry)


# =====================================================
# RUNTIME EXECUTION
# =====================================================


async def main() -> None:
    controller = AdaptiveThresholdController()
    await controller.update_thresholds()


if __name__ == "__main__":
    asyncio.run(main())
