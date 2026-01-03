"""Reflective Cloud Monitor — latency, drift, coherence analytics engine."""

from __future__ import annotations

import json
import os
from datetime import datetime
from time import perf_counter
from typing import Any, Dict

from core_meta.ree_feedback_interface import REEFeedbackInterface
from core_meta.ree_integrity_controller import REEIntegrityController
from core_reflective.hybrid_reflective_bridge_manager import HybridReflectiveBridgeManager
from core_reflective.reflective_logger import ReflectiveLogger


class CloudMonitorService:
    """Monitor reflective integrity across Vaults and Meta layer in near real time."""

    def __init__(self) -> None:
        self.bridge = HybridReflectiveBridgeManager()
        self.meta = REEIntegrityController()
        self.feedback = REEFeedbackInterface()
        self.logger = ReflectiveLogger("cloud_monitor_service")
        self.integrity_path = "data/integrity/system_integrity.json"
        self.coherence_path = "data/integrity/coherence_index.json"
        self.drift_log_path = "data/integrity/frpc_drift_log.json"

    # 🧩 1️⃣ Kumpulkan Metrik Reflektif Global
    def collect_metrics(self) -> Dict[str, Any]:
        start = perf_counter()

        bridge_sync = self.bridge.sync_all()
        meta_state = self.meta.evaluate_integrity()
        feedback_state = self.feedback.collect_feedback()

        drift_index = round(
            (
                abs(feedback_state.get("alpha_drift", 0.0))
                + abs(feedback_state.get("beta_drift", 0.0))
                + abs(feedback_state.get("gamma_drift", 0.0))
            )
            / 3,
            4,
        )

        integrity_index = round(
            (bridge_sync.get("integrity_index", 0.0) + meta_state.get("integrity_index", 0.0)) / 2,
            3,
        )
        reflective_coherence = round(
            (bridge_sync.get("coherence_index", 0.0) + feedback_state.get("reflective_coherence", 0.0)) / 2,
            3,
        )
        meta_integrity = meta_state.get("integrity_index", 0.0)

        # Derive a stable reflective intensity heuristic (bounded 1.70–1.85)
        intensity_base = 1.7 + max(0.0, min(0.15, meta_integrity - 0.85))
        reflective_intensity = round(min(1.85, max(1.7, intensity_base)), 3)

        latency_ms = int((perf_counter() - start) * 1000)

        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "integrity_index": integrity_index,
            "reflective_coherence": reflective_coherence,
            "meta_integrity": meta_integrity,
            "reflective_intensity": reflective_intensity,
            "drift_index": drift_index,
            "latency_ms": latency_ms,
        }

        self._persist_metrics(metrics)
        self.logger.log({"event": "cloud_metrics", "data": metrics}, category="monitor")
        return metrics

    # 🧩 2️⃣ Jalankan Audit Reflektif
    def run_audit(self) -> Dict[str, Any]:
        metrics = self.collect_metrics()
        state = "HARMONIC" if (metrics["reflective_coherence"] >= 0.95 and metrics["integrity_index"] >= 0.96 and metrics["drift_index"] <= 0.007) else "DRIFT"

        audit = {
            "integrity_index": metrics["integrity_index"],
            "reflective_coherence": metrics["reflective_coherence"],
            "meta_integrity": metrics["meta_integrity"],
            "drift_index": metrics["drift_index"],
            "reflective_field_state": state,
            "latency_ms": metrics["latency_ms"],
            "timestamp": metrics["timestamp"],
        }

        self.logger.log({"event": "cloud_audit", "data": audit}, category="audit")
        return audit

    # 🧩 3️⃣ Simpan ke Cache Integritas
    def _persist_metrics(self, metrics: Dict[str, Any]) -> None:
        os.makedirs("data/integrity", exist_ok=True)
        with open(self.integrity_path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "integrity_index": metrics.get("integrity_index", 0.0),
                    "meta_integrity": metrics.get("meta_integrity", 0.0),
                    "timestamp": metrics.get("timestamp"),
                },
                file,
                indent=2,
            )

        with open(self.coherence_path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "reflective_coherence": metrics.get("reflective_coherence", 0.0),
                    "timestamp": metrics.get("timestamp"),
                },
                file,
                indent=2,
            )

        with open(self.drift_log_path, "a", encoding="utf-8") as file:
            file.write(json.dumps(metrics) + "\n")


# Runtime helper
cloud_monitor_service = CloudMonitorService()
