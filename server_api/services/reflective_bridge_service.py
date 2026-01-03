"""Hybrid Reflective Bridge Service.

Bridges Reflex → Fusion → TRQ–3D → RGO → Meta (REE) layers and writes
lightweight reflective telemetry into Journal Vault logs.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from core_meta.ree_feedback_interface import REEFeedbackInterface
from core_reflective.adaptive_field_stabilizer import adaptive_field_stabilizer
from core_reflective.hybrid_reflective_bridge_manager import HybridReflectiveBridgeManager
from core_reflective.reflective_cycle_manager import reflective_cycle_manager
from core_reflective.reflective_logger import ReflectiveLogger
from core_reflective.trq3d_engine import trq3d_engine


class ReflectiveBridgeService:
	"""Coordinate cross-layer reflective integration for a symbol pair."""

	def __init__(self) -> None:
		self.bridge = HybridReflectiveBridgeManager()
		self.ree_feedback = REEFeedbackInterface()
		self.logger = ReflectiveLogger("reflective_bridge_service")
		self._bridge_initialized = False

	# 🧩 1️⃣ Jalankan integrasi reflektif penuh
	def run_reflective_bridge(
		self,
		pair: str,
		timeframe: str = "H1",
		price_series: Optional[List[float]] = None,
		volume_series: Optional[List[float]] = None,
	) -> Dict[str, Any]:
		if not self._bridge_initialized:
			self.bridge.initialize()
			self.ree_feedback.initialize()
			self._bridge_initialized = True

		# Layer sync baseline (reflective, neural, quantum)
		sync_snapshot = self.bridge.sync_all()

		# TRQ–3D energy computation (price × time × volume)
		trq = trq3d_engine(pair, timeframe, price_series, volume_series)

		# RGO field stabilization (α–β–γ gradient & integrity)
		field_state = adaptive_field_stabilizer(trq["alpha"], trq["beta"], trq["gamma"])

		# Meta-layer reflective feedback (REE)
		meta_fb = self.ree_feedback.collect_feedback()

		# Compose coherence & integrity indices using available signals
		fusion_coherence = sync_snapshot.get("coherence_index", 0.0)
		reflective_coherence = round(
			(fusion_coherence + meta_fb.get("reflective_coherence", 0.0) + field_state["integrity_index"]) / 3,
			3,
		)
		integrity_index = round((field_state["integrity_index"] + meta_fb.get("meta_integrity", 0.0)) / 2, 3)

		# Run a lightweight reflective cycle log for traceability
		reflective_cycle_manager(
			{
				"pair": pair,
				"timeframe": timeframe,
				"fusion_score": reflective_coherence,
			}
		)

		result = {
			"pair": pair,
			"timeframe": timeframe,
			"reflective_intensity": trq["reflective_intensity"],
			"mean_energy": trq["mean_energy"],
			"alpha": trq["alpha"],
			"beta": trq["beta"],
			"gamma": trq["gamma"],
			"gradient": field_state["gradient"],
			"field_state": field_state["field_state"],
			"sync_cluster": field_state["sync_cluster"],
			"meta_integrity": meta_fb.get("meta_integrity"),
			"reflective_coherence": reflective_coherence,
			"integrity_index": integrity_index,
			"coherence_reflective_layer": fusion_coherence,
			"timestamp": datetime.datetime.utcnow().isoformat() + "Z",
			"version": sync_snapshot.get("version", "6.0r++"),
		}

		self.logger.log({"event": "bridge_sync", "data": result}, category="bridge")
		return result

	# 🧩 2️⃣ Sinkronisasi Meta Feedback
	def sync_meta_feedback(self, pair: str) -> Dict[str, Any]:
		feedback_state = self.ree_feedback.collect_feedback()
		learning_feedback = self.ree_feedback.compute_learning_feedback()
		payload = {
			"pair": pair,
			"meta_integrity": feedback_state.get("meta_integrity"),
			"reflective_coherence": feedback_state.get("reflective_coherence"),
			"alpha_drift": feedback_state.get("alpha_drift"),
			"beta_drift": feedback_state.get("beta_drift"),
			"gamma_drift": feedback_state.get("gamma_drift"),
			"learning_gain": learning_feedback.get("learning_gain"),
			"meta_integrity_delta": learning_feedback.get("meta_integrity_delta"),
			"timestamp": learning_feedback.get("timestamp"),
		}
		self.logger.meta_log(payload)
		return payload

	# 🧩 3️⃣ Audit Harmoni Reflektif
	def audit_reflective_harmony(self, pair: str, timeframe: str = "H1") -> Dict[str, Any]:
		bridge_data = self.run_reflective_bridge(pair, timeframe=timeframe)
		feedback = self.sync_meta_feedback(pair)

		# Harmony index blends bridge coherence with meta feedback coherence
		harmony_index = round(
			(bridge_data["reflective_coherence"] + feedback.get("reflective_coherence", 0.0)) / 2,
			3,
		)

		audit_result = {
			"pair": pair,
			"timeframe": timeframe,
			"harmony_index": harmony_index,
			"status": "Reflective Harmony Stable" if harmony_index >= 0.95 else "Harmony Drift Detected",
			"bridge_integrity": bridge_data["integrity_index"],
			"meta_integrity": feedback.get("meta_integrity"),
			"timestamp": datetime.datetime.utcnow().isoformat() + "Z",
		}

		self.logger.audit_log(audit_result)
		return audit_result


# Runtime helper
bridge_service = ReflectiveBridgeService()

