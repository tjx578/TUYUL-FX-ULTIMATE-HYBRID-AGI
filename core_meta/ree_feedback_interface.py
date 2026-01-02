from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from core_fusion.fta_integration_v6_production import TuyulGPTBridgeWithFundamentals
from core_reflective.reflective_evolution_engine_v6 import ReflectiveEvolutionEngine
from core_reflective.reflective_logger import log_reflective_event


class REEFeedbackInterface:
    """Bridge Layer-12.5 fusion reasoning to Layer-17 REE meta-learning."""

    def __init__(self, log_path: Path | str = "data/logs/ree_integrity_feedback.json"):
        self.bridge = TuyulGPTBridgeWithFundamentals()
        self.ree = ReflectiveEvolutionEngine()
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def run_cycle(
        self, pair: str, timeframe: str, market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        fusion_output = self.bridge.handle_request(pair, timeframe, market_data)
        ree_feedback = self.ree.run_feedback_cycle(
            pair=pair,
            fusion_conf=fusion_output["layer12"].get("fusion_confidence", 0.0),
            fundamental_score=fusion_output["fundamental_context"].get(
                "fundamental_score", 0.0
            ),
            bias=fusion_output["layer12"].get("bias_direction", "NEUTRAL"),
            timestamp=fusion_output.get(
                "timestamp", datetime.now(timezone.utc).isoformat()
            ),
        )

        combined = {
            "pair": pair,
            "timeframe": timeframe,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fusion_result": fusion_output,
            "ree_feedback": ree_feedback,
            "integrity_status": (
                "PASS"
                if ree_feedback.get("reflective_integrity", 0.0) > 0.9
                else "REVIEW"
            ),
        }

        self._save_feedback(combined)
        log_reflective_event("REE_BRIDGE_RESULT", combined)
        return combined

    def _save_feedback(self, payload: Dict[str, Any]) -> None:
        with open(self.log_path, "a", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n---\n")


if __name__ == "__main__":
    sample_market = {
        "prices": [1.105, 1.108, 1.111],
        "highs": [1.110, 1.113, 1.115],
        "lows": [1.101, 1.104, 1.106],
        "closes": [1.107, 1.109, 1.112],
        "volumes": [1000, 1150, 980],
        "returns": [0.0012, 0.001, 0.0008],
    }

    ree_bridge = REEFeedbackInterface()
    result = ree_bridge.run_cycle("GBPUSD", "H1", sample_market)

    print("\nReflective Feedback Summary:")
    print(json.dumps(result, indent=2))
