"""
🧩 REFLECTIVE TRADE INTEGRITY AUDIT v6 (Production)
---------------------------------------------------
Part of TUYUL FX ULTIMATE Hybrid AGI Reflective Layer (L16)

Fungsi utama:
- Mengevaluasi integritas keputusan trade (BUY/SELL/WAIT)
- Menghitung Trade Integrity Index (TII)
- Menilai bias reflektif dan sinkronisasi FRPC/REE
- Mengirim feedback ke REE untuk recalibration
- Sinkronisasi hasil audit ke Vault & Google Cloud Logging
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

from google.cloud import logging as cloud_logging

from core_reflective.reflective_logger import log_reflective_event


class ReflectiveTradeIntegrityAudit:
    """Main class untuk layer Reflective Trade Integrity Audit (RTIA v6)."""

    MODULE_NAME = "REFLECTIVE_TRADE_INTEGRITY_AUDIT"
    MODULE_VERSION = "v6.0r∞"
    STATUS = "PRODUCTION"

    def __init__(
        self,
        frpc_path: str = "data/integrity/frpc_drift_log.json",
        ree_path: str = "data/logs/reflective_evolution_log.json",
        plan_path: str = "quad_vaults/journal_vault/session_logs/trade_plan_YYYYMMDD.json",
        tii_log_path: str = "data/logs/reflective_trade_precision_log.json",
        audit_log_path: str = "data/logs/reflective_audit_log.json",
        feedback_path: str = "data/integrity/ree_integrity_feedback.json",
    ) -> None:
        self.frpc_path = frpc_path
        self.ree_path = ree_path
        self.plan_path = plan_path
        self.tii_log_path = tii_log_path
        self.audit_log_path = audit_log_path
        self.feedback_path = feedback_path

        self.client = None
        self.logger = None
        self._configure_cloud_logger()

    def _configure_cloud_logger(self) -> None:
        try:
            self.client = cloud_logging.Client()
            self.logger = self.client.logger("reflective.audit.integrity")
        except Exception as exc:  # pragma: no cover - defensive fallback
            self.client = None
            self.logger = None
            log_reflective_event(
                "CLOUD_LOGGER_FALLBACK",
                {"module": self.MODULE_NAME, "error": str(exc)},
            )

    # ============================================================
    # CORE COMPUTATION
    # ============================================================

    def compute_tii(
        self,
        fusion_confidence: float,
        reflective_resonance: float,
        bias_delta: float,
        variance_dev: float,
    ) -> float:
        """Hitung Trade Integrity Index (TII)."""
        eps = 0.001
        tii = (
            fusion_confidence
            * reflective_resonance
            * (1 - abs(bias_delta))
            / (variance_dev + eps)
        )
        return round(min(max(tii, 0.0), 1.0), 3)

    # ============================================================
    # MAIN AUDIT FUNCTION
    # ============================================================

    def audit_trade(
        self,
        pair: str,
        decision: str,
        fusion_confidence: float,
        reflective_resonance: float,
        bias_delta: float,
        variance_dev: float,
    ) -> Dict[str, Any]:
        """Lakukan audit integritas reflektif untuk satu keputusan trade."""
        tii_score = self.compute_tii(
            fusion_confidence, reflective_resonance, bias_delta, variance_dev
        )

        if tii_score >= 0.90:
            state = "ACCEPTED"
            reason = "Fusion–Reflective alignment optimal"
        elif tii_score >= 0.75:
            state = "REVIEW"
            reason = "Minor reflective drift detected"
        else:
            state = "REJECTED"
            reason = "Bias high atau reflective misalignment"

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pair": pair,
            "decision": decision,
            "confidence": fusion_confidence,
            "tii_score": tii_score,
            "reflective_resonance": reflective_resonance,
            "bias_delta": bias_delta,
            "integrity_state": state,
            "reason": reason,
        }

        self._persist_audit(payload)
        self._send_feedback_to_ree(payload)
        self._sync_to_cloud(payload)

        log_reflective_event(
            "REFLECTIVE_TRADE_INTEGRITY_AUDIT",
            {"pair": pair, "decision": decision, "tii_score": tii_score, "state": state},
        )

        return payload

    # ============================================================
    # INTERNAL I/O METHODS
    # ============================================================

    def _persist_audit(self, payload: Dict[str, Any]) -> None:
        """Simpan hasil audit ke file lokal."""
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        with open(self.audit_log_path, "a", encoding="utf-8") as file:
            json.dump(payload, file)
            file.write("\n")

        vault_path = "quad_vaults/journal_vault/session_logs/reflective_trade_integrity.json"
        os.makedirs(os.path.dirname(vault_path), exist_ok=True)
        with open(vault_path, "a", encoding="utf-8") as file:
            json.dump(payload, file)
            file.write("\n")

    def _send_feedback_to_ree(self, payload: Dict[str, Any]) -> None:
        """Kirim feedback hasil audit ke REE untuk recalibration."""
        feedback = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tii_score": payload["tii_score"],
            "bias_delta": payload["bias_delta"],
            "state": payload["integrity_state"],
            "action": "RECALIBRATE"
            if payload["integrity_state"] == "REJECTED"
            else "STABLE",
        }
        os.makedirs(os.path.dirname(self.feedback_path), exist_ok=True)
        with open(self.feedback_path, "w", encoding="utf-8") as file:
            json.dump(feedback, file, indent=2)

    def _sync_to_cloud(self, payload: Dict[str, Any]) -> None:
        """Kirim hasil audit ke Google Cloud Logging."""
        if self.logger is None:
            return

        self.logger.log_struct(
            {
                "event": "reflective.audit.completed",
                "pair": payload["pair"],
                "decision": payload["decision"],
                "tii_score": payload["tii_score"],
                "integrity_state": payload["integrity_state"],
                "reason": payload["reason"],
                "module": self.MODULE_NAME,
                "version": self.MODULE_VERSION,
            }
        )

    # ============================================================
    # BATCH MODE
    # ============================================================

    def run_batch_audit(self, trade_decisions: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """Jalankan audit untuk banyak trade sekaligus."""
        results = []
        for trade in trade_decisions:
            result = self.audit_trade(
                pair=trade["pair"],
                decision=trade["decision"],
                fusion_confidence=trade["confidence"],
                reflective_resonance=trade["resonance"],
                bias_delta=trade.get("bias_delta", 0.0),
                variance_dev=trade.get("variance_dev", 0.01),
            )
            results.append(result)
        return results


if __name__ == "__main__":
    print("🧠 Running Reflective Trade Integrity Audit v6.0r∞")
    auditor = ReflectiveTradeIntegrityAudit()

    trades = [
        {
            "pair": "EURUSD",
            "decision": "BUY",
            "confidence": 0.85,
            "resonance": 0.95,
            "bias_delta": -0.02,
            "variance_dev": 0.01,
        },
        {
            "pair": "GBPJPY",
            "decision": "SELL",
            "confidence": 0.78,
            "resonance": 0.82,
            "bias_delta": 0.07,
            "variance_dev": 0.015,
        },
    ]

    results = auditor.run_batch_audit(trades)
    print(json.dumps(results, indent=2))
