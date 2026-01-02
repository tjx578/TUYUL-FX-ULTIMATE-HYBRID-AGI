"""
FUNDAMENTAL DRIVE ENGINE v5.3.3 – TUYUL FX HYBRID AGI 🧠💹
==========================================================

Mengintegrasikan analisis makro fundamental ke dalam sistem reflektif TUYUL FX.
Layer ini (L11.5) berfungsi sebagai jembatan antara FTA (L10), Adaptive Risk (L11),
dan Fusion Layer (L12). Sinkron otomatis ke Kartel Vault dan REE Feedback Loop.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FundamentalDriveEngine")

# === Default Paths ===
VAULT_PATH = Path("quad_vaults/kartel_vault/reflective_memory")
OUTPUT_LOG = VAULT_PATH / "fundamental_drive_snapshot.json"
REE_FEEDBACK_LOG = Path("quad_vaults/journal_vault/session_logs/reflective_feedback.json")
FUSION_OUTPUT_LOG = Path("quad_vaults/hybrid_vault/fusion_conf12_feed.json")
ADAPTIVE_RISK_LOG = Path("quad_vaults/hybrid_vault/adaptive_risk_signal.json")

BIAS_WEIGHTS = {
    "policy_diff": 0.25,
    "inflation_diff": 0.20,
    "commodity_corr": 0.15,
    "risk_sentiment": 0.20,
    "carry_diff": 0.20,
}


@dataclass
class FundamentalSnapshot:
    """Snapshot hasil kalkulasi fundamental reflektif."""

    cycle_id: str
    fund_bias_score: float
    fund_bias_dir: str
    raw_components: Dict[str, float]
    timestamp: str
    integrity_index: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "layer": "L11.5-FUNDAMENTAL",
            "FUND_BIAS_SCORE": self.fund_bias_score,
            "FUND_BIAS_DIR": self.fund_bias_dir,
            "raw_components": self.raw_components,
            "integrity_index": self.integrity_index,
            "timestamp": self.timestamp,
        }


class FundamentalDriveEngine:
    """
    Reflective Fundamental Drive Engine (Layer 11.5)
    Menghitung FUND_BIAS_SCORE berbasis variabel fundamental makro.
    Sinkron ke Kartel Vault, propagate ke Fusion Layer & Adaptive Risk,
    dan memicu REE feedback cycle otomatis.
    """

    def __init__(
        self,
        vault_path: Path = VAULT_PATH,
        output_log: Path = OUTPUT_LOG,
        ree_feedback_log: Path = REE_FEEDBACK_LOG,
        fusion_output_log: Path = FUSION_OUTPUT_LOG,
        adaptive_risk_log: Path = ADAPTIVE_RISK_LOG,
        bias_weights: Mapping[str, float] | None = None,
    ):
        self.vault_path = vault_path
        self.output_log = output_log
        self.ree_feedback_log = ree_feedback_log
        self.fusion_output_log = fusion_output_log
        self.adaptive_risk_log = adaptive_risk_log
        self.bias_weights = dict(bias_weights or BIAS_WEIGHTS)

        self._validate_weights()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        for path in [
            self.vault_path,
            self.output_log.parent,
            self.ree_feedback_log.parent,
            self.fusion_output_log.parent,
            self.adaptive_risk_log.parent,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def _validate_weights(self) -> None:
        missing = [key for key in BIAS_WEIGHTS if key not in self.bias_weights]
        if missing:
            raise ValueError(f"Missing bias weight definitions: {', '.join(missing)}")
        total_weight = sum(self.bias_weights.values())
        if round(total_weight, 4) != 1.0:
            raise ValueError("Bias weights must sum to 1.0")

    def compute_bias_score(
        self,
        policy_diff: float,
        inflation_diff: float,
        commodity_corr: float,
        risk_sentiment: float,
        carry_diff: float,
    ) -> FundamentalSnapshot:
        """Hitung bias makro fundamental dan arah utama."""

        self._validate_inputs(
            {
                "policy_diff": policy_diff,
                "inflation_diff": inflation_diff,
                "commodity_corr": commodity_corr,
                "risk_sentiment": risk_sentiment,
                "carry_diff": carry_diff,
            }
        )

        raw_score = (
            self.bias_weights["policy_diff"] * policy_diff
            + self.bias_weights["inflation_diff"] * inflation_diff
            + self.bias_weights["commodity_corr"] * commodity_corr
            + self.bias_weights["risk_sentiment"] * risk_sentiment
            + self.bias_weights["carry_diff"] * carry_diff
        )
        normalized = (raw_score + 1) / 2
        direction = self._score_direction(normalized)

        integrity_index = min(1.0, round(0.88 + (normalized * 0.12), 3))
        snapshot = FundamentalSnapshot(
            cycle_id=self._build_cycle_id(),
            fund_bias_score=round(normalized, 3),
            fund_bias_dir=direction,
            raw_components={
                "policy_diff": policy_diff,
                "inflation_diff": inflation_diff,
                "commodity_corr": commodity_corr,
                "risk_sentiment": risk_sentiment,
                "carry_diff": carry_diff,
            },
            timestamp=datetime.utcnow().isoformat(),
            integrity_index=integrity_index,
        )

        logger.info(
            "[FUND] Bias Score %s → %s", snapshot.fund_bias_score, snapshot.fund_bias_dir
        )
        return snapshot

    def sync_to_vault(self, data: Mapping[str, Any]) -> str:
        """Simpan hasil bias ke Kartel Vault (reflective_memory)."""

        return self._write_json(
            target=self.output_log,
            payload=data,
            success_msg=f"[SYNC] Fundamental bias synced to {self.output_log}",
            error_prefix="[ERROR] Vault sync failed",
        )

    def dispatch_to_fusion_layer(self, snapshot: FundamentalSnapshot) -> Dict[str, Any]:
        """Generate signal untuk Fusion Layer CONF₁₂."""

        fusion_conf12 = round(
            (snapshot.fund_bias_score * 0.7)
            + (snapshot.raw_components["risk_sentiment"] * 0.3),
            3,
        )
        fusion_payload = {
            "cycle_id": snapshot.cycle_id,
            "layer": "L12-CONF",
            "fusion_conf12": fusion_conf12,
            "direction": snapshot.fund_bias_dir,
            "bias_driver": "fundamental",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "READY" if fusion_conf12 >= 0.55 else "WATCH",
        }

        self._write_json(
            target=self.fusion_output_log,
            payload=fusion_payload,
            success_msg="[FUSION] CONF₁₂ feed updated.",
            error_prefix="[FUSION] Feed write error",
        )
        return fusion_payload

    def dispatch_to_adaptive_risk(
        self, snapshot: FundamentalSnapshot, fusion_payload: Mapping[str, Any]
    ) -> Dict[str, Any]:
        """Kirim sinyal ke Adaptive Risk Engine."""

        volatility_guard = round(max(0.1, 1 - abs(snapshot.raw_components["risk_sentiment"])), 3)
        risk_budget = round(0.35 + (snapshot.fund_bias_score * 0.4), 3)
        adaptive_risk = {
            "cycle_id": snapshot.cycle_id,
            "layer": "L11-ADAPTIVE-RISK",
            "direction": snapshot.fund_bias_dir,
            "risk_budget": min(1.0, risk_budget),
            "volatility_guard": volatility_guard,
            "fusion_conf12": fusion_payload["fusion_conf12"],
            "timestamp": datetime.utcnow().isoformat(),
            "state": "ADAPTIVE_READY",
        }

        self._write_json(
            target=self.adaptive_risk_log,
            payload=adaptive_risk,
            success_msg="[RISK] Adaptive signal dispatched.",
            error_prefix="[RISK] Dispatch error",
        )
        return adaptive_risk

    def trigger_reflective_feedback(
        self,
        snapshot: FundamentalSnapshot,
        fusion_payload: Mapping[str, Any],
        adaptive_risk: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Generate feedback ke Meta-Learning REE (Layer-17)."""

        feedback = {
            "cycle_id": snapshot.cycle_id,
            "source_layer": "L11.5",
            "reflective_input": snapshot.as_dict(),
            "fusion_signal": fusion_payload,
            "adaptive_risk": adaptive_risk,
            "ree_signal_strength": snapshot.fund_bias_score,
            "integrity_index": snapshot.integrity_index,
            "feedback_state": "READY",
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._write_json(
            target=self.ree_feedback_log,
            payload=feedback,
            success_msg="[REE] Reflective Feedback Cycle triggered successfully.",
            error_prefix="[REE] Feedback write error",
        )
        return feedback

    def run_cycle(self, payload: Dict[str, float]) -> Dict[str, Any]:
        """Eksekusi penuh siklus fundamental reflektif."""

        snapshot = self.compute_bias_score(**payload)
        vault_sync_path = self.sync_to_vault(snapshot.as_dict())
        fusion_payload = self.dispatch_to_fusion_layer(snapshot)
        adaptive_risk = self.dispatch_to_adaptive_risk(snapshot, fusion_payload)
        ree_feedback = self.trigger_reflective_feedback(
            snapshot=snapshot, fusion_payload=fusion_payload, adaptive_risk=adaptive_risk
        )
        return {
            "cycle_id": snapshot.cycle_id,
            "snapshot": snapshot.as_dict(),
            "vault_sync": vault_sync_path,
            "fusion_signal": fusion_payload,
            "adaptive_risk": adaptive_risk,
            "ree_feedback": ree_feedback,
        }

    def _write_json(
        self, target: Path, payload: Mapping[str, Any], success_msg: str, error_prefix: str
    ) -> str:
        try:
            target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            logger.info(success_msg)
            return str(target)
        except OSError as exc:
            logger.error("%s: %s", error_prefix, exc)
            return "write_failed"

    @staticmethod
    def _score_direction(normalized_score: float) -> str:
        if normalized_score >= 0.65:
            return "BULLISH"
        if normalized_score <= 0.35:
            return "BEARISH"
        return "NEUTRAL"

    @staticmethod
    def _validate_inputs(values: Mapping[str, float]) -> None:
        out_of_bounds = {
            key: value for key, value in values.items() if value < -1.0 or value > 1.0
        }
        if out_of_bounds:
            raise ValueError(f"Input values must be within [-1, 1]: {out_of_bounds}")

    @staticmethod
    def _build_cycle_id() -> str:
        return f"FD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"


# === CLI Mode ===
if __name__ == "__main__":
    print("⚙️  TUYUL FX FUNDAMENTAL DRIVE v5.3.3 Reflective Mode\n")

    engine = FundamentalDriveEngine()
    test_payload = {
        "policy_diff": 0.75,
        "inflation_diff": 0.40,
        "commodity_corr": 0.25,
        "risk_sentiment": 0.60,
        "carry_diff": 0.50,
    }

    result = engine.run_cycle(test_payload)
    print(json.dumps(result, indent=2))
    print("\n✅ Reflective cycle synced to Kartel Vault & REE feedback log.\n🐺 GAS BOSSKU ⚡")
