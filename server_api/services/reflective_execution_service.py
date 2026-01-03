"""Reflective trade execution bridge and feedback handler."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from core_meta.ree_feedback_interface import REEFeedbackInterface
from core_reflective.reflective_logger import ReflectiveLogger
from core_reflective.reflective_trade_execution_bridge_v6_production import execute_reflective_trade
from core_reflective.reflective_trade_integrity_audit_v6_production import (
	reflective_trade_integrity_audit_v6_production,
)
from core_reflective.tii_reflective_feedback_adapter_v6_production import (
	tii_reflective_feedback_adapter_v6_production,
)
from server_api.services.reflective_tradeplan_service import tradeplan_service


class ReflectiveExecutionService:
	"""Execute reflective trades, audit outcomes, and send feedback."""

	def __init__(self) -> None:
		self.logger = ReflectiveLogger("reflective_execution_service")
		self.meta_feedback = REEFeedbackInterface()
		self.journal_path = Path("quad_vaults/journal_vault/trade_execution_log.json")
		self._latest: Dict[str, Any] | None = None

	# 🧩 1️⃣ Jalankan eksekusi reflektif otomatis
	def run_execution(self, pair: str) -> Dict[str, Any]:
		plan = tradeplan_service.get_latest_plan()
		plan_signal = self._extract_plan_signal(plan)

		if not plan_signal:
			result = {"status": "No reflective plan available for execution."}
			self.logger.log(result, category="execution")
			return result

		execution = execute_reflective_trade(pair, simulate=True)
		audit = reflective_trade_integrity_audit_v6_production(plan_signal, execution, plan_signal.get("integrity_index", 0.0))
		tii_feedback = tii_reflective_feedback_adapter_v6_production(
			{"tii": audit.get("integrity_score", 0.0), "status": audit.get("audit_status", ""),}
		)
		meta_fb = self._build_meta_feedback()

		pnl = execution.get("result", {}).get("pnl", 0.0)
		rr_ratio = execution.get("result", {}).get("rr_ratio")
		outcome = execution.get("result", {}).get("outcome")
		exit_price = self._to_float(execution.get("tp")) if outcome == "win" else self._to_float(execution.get("sl"))
		reflective_coherence = audit.get("integrity_score", 0.0)

		result = {
			"pair": pair,
			"entry": execution.get("entry"),
			"exit": exit_price,
			"pnl": pnl,
			"probability": plan.get("probability"),
			"rr_ratio": rr_ratio,
			"integrity_index": plan_signal.get("integrity_index", 0.0),
			"reflective_coherence": reflective_coherence,
			"meta_feedback": meta_fb,
			"tii_feedback": tii_feedback,
			"regime_state": plan.get("regime_state"),
			"timestamp": datetime.utcnow().isoformat() + "Z",
			"status": execution.get("status", "executed"),
			"execution_raw": execution,
		}

		self._latest = result
		self._save_execution(result)
		self.logger.log({"event": "execution_completed", "data": result}, category="execution")
		return result

	# 🧩 2️⃣ Ambil hasil eksekusi terakhir
	def get_latest_execution(self) -> Dict[str, Any]:
		if self._latest:
			return self._latest
		if self.journal_path.exists():
			with open(self.journal_path, "r", encoding="utf-8") as file:
				return json.load(file)
		return {"status": "No reflective execution record found."}

	# 🧩 3️⃣ Audit hasil reflektif penuh
	def run_audit(self, pair: str) -> Dict[str, Any]:
		plan = tradeplan_service.get_latest_plan()
		plan_signal = self._extract_plan_signal(plan)
		if not plan_signal:
			return {"status": "No reflective plan available for audit."}

		execution = execute_reflective_trade(pair, simulate=True)
		audit = reflective_trade_integrity_audit_v6_production(plan_signal, execution, plan_signal.get("integrity_index", 0.0))
		self.logger.audit_log({"event": "execution_audit", "data": audit})
		return audit

	# ------------------------------------------------------------
	# Helpers
	# ------------------------------------------------------------
	def _extract_plan_signal(self, plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
		if not isinstance(plan, dict):
			return None
		signal = plan.get("raw_signal") or plan.get("signal") or {}
		entry = self._to_float(signal.get("entry")) or self._to_float(plan.get("entry"))
		tp = self._to_float(signal.get("tp")) or self._first_float(plan.get("targets"))
		sl = self._to_float(signal.get("sl") or signal.get("stop_loss") or plan.get("stop_loss"))
		if entry is None or tp is None or sl is None:
			return None
		return {
			"entry": entry,
			"tp": tp,
			"sl": sl,
			"type": signal.get("type", "BUY"),
			"integrity_index": plan.get("integrity_index", 0.0),
		}

	def _build_meta_feedback(self) -> Dict[str, Any]:
		feedback_state = self.meta_feedback.collect_feedback()
		learning_feedback = self.meta_feedback.compute_learning_feedback()
		return {
			"reflective_coherence": feedback_state.get("reflective_coherence"),
			"meta_integrity": feedback_state.get("meta_integrity"),
			"alpha_drift": feedback_state.get("alpha_drift"),
			"beta_drift": feedback_state.get("beta_drift"),
			"gamma_drift": feedback_state.get("gamma_drift"),
			"learning_gain": learning_feedback.get("learning_gain"),
			"meta_integrity_delta": learning_feedback.get("meta_integrity_delta"),
			"timestamp": learning_feedback.get("timestamp"),
		}

	def _to_float(self, value: Any) -> Optional[float]:
		try:
			return float(value)
		except (TypeError, ValueError):
			return None

	def _first_float(self, values: Any) -> Optional[float]:
		if isinstance(values, list) and values:
			return self._to_float(values[0])
		return None

	def _save_execution(self, result: Dict[str, Any]) -> None:
		self.journal_path.parent.mkdir(parents=True, exist_ok=True)
		with open(self.journal_path, "w", encoding="utf-8") as file:
			json.dump(result, file, indent=2)


# Runtime helper
execution_service = ReflectiveExecutionService()
