"""Reflective Evolution Engine (REE) meta-learning service.

Runs adaptive learning for the Meta Layer (α, β, γ), evaluates integrity/coherence,
and persists learning curves plus feedback snapshots to the vault manifests.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from core_meta.neural_bridge_hub_v6 import NeuralBridgeHubV6
from core_meta.ree_adaptive_analysis import REEAdaptiveAnalysis
from core_meta.ree_feedback_interface import REEFeedbackInterface
from core_meta.ree_integrity_controller import REEIntegrityController
from core_reflective.reflective_logger import ReflectiveLogger


class REEMetaService:
	"""Coordinate REE adaptive learning, integrity evaluation, and feedback."""

	def __init__(self) -> None:
		self.adaptive = REEAdaptiveAnalysis()
		self.integrity = REEIntegrityController()
		self.feedback = REEFeedbackInterface()
		self.neural_hub = NeuralBridgeHubV6()
		self.logger = ReflectiveLogger("ree_meta_service")
		self.learning_curve_path = Path("core_meta/configs/ree_learning_curve.json")
		self.integrity_path = Path("data/integrity/ree_integrity_feedback.json")

	# 🧩 1️⃣ Jalankan Siklus Pembelajaran Reflektif
	def run_meta_learning_cycle(self) -> Dict[str, Any]:
		# Analyze drift and update adaptive weights
		drift = self.adaptive.compute_reflective_drift()
		weights = self.adaptive.update_adaptive_weights()

		# Integrity evaluation and meta feedback
		integrity_state = self.integrity.evaluate_integrity()
		feedback_state = self.feedback.collect_feedback()
		learning_feedback = self.feedback.compute_learning_feedback()

		# Neural bridge synchronization to propagate meta updates
		hub_sync = self.neural_hub.run_full_sync()

		reflective_gradient = round(
			abs(drift.get("alpha_drift", 0.0))
			+ abs(drift.get("beta_drift", 0.0))
			+ abs(drift.get("gamma_drift", 0.0)),
			4,
		)

		meta_result = {
			"alpha_delta": drift.get("alpha_drift", 0.0),
			"beta_delta": drift.get("beta_drift", 0.0),
			"gamma_delta": drift.get("gamma_drift", 0.0),
			"reflective_gradient": reflective_gradient,
			"meta_integrity": integrity_state.get("integrity_index", 0.0),
			"reflective_coherence": hub_sync.get("coherence_index", 0.0),
			"adaptive_weights": {
				"alpha": weights.get("alpha_weight"),
				"beta": weights.get("beta_weight"),
				"gamma": weights.get("gamma_weight"),
			},
			"learning_gain": learning_feedback.get("learning_gain"),
			"meta_integrity_delta": learning_feedback.get("meta_integrity_delta"),
			"timestamp": datetime.utcnow().isoformat() + "Z",
		}

		self._save_learning_curve(meta_result)
		self._save_integrity_feedback(meta_result)
		self.logger.log({"event": "meta_learning_cycle", "data": meta_result}, category="meta")
		return meta_result

	# 🧩 2️⃣ Cek Status Meta Layer
	def get_meta_status(self) -> Dict[str, Any]:
		integrity_state = self.integrity.evaluate_integrity()
		feedback_state = self.feedback.collect_feedback()
		status = {
			"meta_integrity": integrity_state.get("integrity_index", 0.0),
			"reflective_coherence": feedback_state.get("reflective_coherence", 0.0),
			"alpha_drift": feedback_state.get("alpha_drift", 0.0),
			"beta_drift": feedback_state.get("beta_drift", 0.0),
			"gamma_drift": feedback_state.get("gamma_drift", 0.0),
			"timestamp": datetime.utcnow().isoformat() + "Z",
		}
		self.logger.log({"event": "meta_status", "data": status}, category="meta")
		return status

	# 🧩 3️⃣ Sinkronisasi Neural Hub
	def sync_neural_layer(self) -> Dict[str, Any]:
		hub_state = self.neural_hub.run_full_sync()
		self.logger.log({"event": "neural_hub_sync", "data": hub_state}, category="meta")
		return hub_state

	# 🧩 4️⃣ Simpan Hasil Pembelajaran
	def _save_learning_curve(self, result: Dict[str, Any]) -> None:
		self.learning_curve_path.parent.mkdir(parents=True, exist_ok=True)
		with open(self.learning_curve_path, "a", encoding="utf-8") as file:
			json.dump(result, file)
			file.write("\n")

	# 🧩 5️⃣ Simpan Meta Feedback
	def _save_integrity_feedback(self, result: Dict[str, Any]) -> None:
		self.integrity_path.parent.mkdir(parents=True, exist_ok=True)
		with open(self.integrity_path, "w", encoding="utf-8") as file:
			json.dump(result, file, indent=2)


# Runtime helper
ree_meta_service = REEMetaService()
