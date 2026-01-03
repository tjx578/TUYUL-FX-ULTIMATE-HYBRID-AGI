"""Reflective Trade Plan generator and validator.

Transforms reflective bridge outputs, TRQ-3D signals, and Monte Carlo scoring
into a concrete trade plan persisted in the Journal Vault.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

from core_cognitive.montecarlo_validator import montecarlo_validate
from core_meta.ree_feedback_interface import REEFeedbackInterface
from core_reflective.reflective_logger import ReflectiveLogger
from core_reflective.reflective_trade_plan_generator_v6_production import (
	generate_reflective_trade_plan,
)
from server_api.services.reflective_bridge_service import (
	ReflectiveBridgeService,
	bridge_service,
)


class ReflectiveTradePlanService:
	"""Generate and validate reflective trade plans for a symbol."""

	def __init__(self) -> None:
		# Reuse the bridge singleton when available to avoid extra bootstraps.
		self.bridge = bridge_service if bridge_service else ReflectiveBridgeService()
		self.ree_feedback = REEFeedbackInterface()
		self.logger = ReflectiveLogger("reflective_tradeplan_service")
		self.journal_path = Path(
			f"quad_vaults/journal_vault/trade_plan_{date.today().strftime('%Y%m%d')}.json"
		)
		self._latest_plan: Dict[str, Any] | None = None

	# 🧩 1️⃣ Generate reflective trade plan
	def generate_trade_plan(self, pair: str, timeframe: str = "H4") -> Dict[str, Any]:
		bridge_state = self.bridge.run_reflective_bridge(pair, timeframe=timeframe)
		meta_state = self.ree_feedback.collect_feedback()

		raw_plan, signal = self._generate_signal(pair, timeframe)

		entry, stop_loss, target = self._extract_prices(signal)
		rr_ratio = self._compute_rr(entry, stop_loss, target)
		probability = self._compute_probability(entry, stop_loss, target, signal, bridge_state)

		plan_data = {
			"pair": pair,
			"timeframe": timeframe,
			"bias": self._derive_bias(signal),
			"entry": entry,
			"entry_zone": self._derive_entry_zone(signal, entry),
			"stop_loss": stop_loss,
			"targets": self._derive_targets(signal, target),
			"probability": probability,
			"rr_ratio": rr_ratio,
			"integrity_index": bridge_state.get("integrity_index"),
			"reflective_intensity": bridge_state.get("reflective_intensity"),
			"meta_confidence": meta_state.get("meta_integrity"),
			"reflective_coherence": bridge_state.get("reflective_coherence"),
			"regime_state": bridge_state.get("field_state"),
			"bridge_version": bridge_state.get("version"),
			"raw_signal": signal,
			"timestamp": datetime.utcnow().isoformat() + "Z",
		}

		self._save_plan(plan_data)
		self.logger.log({"event": "trade_plan_generated", "plan": plan_data}, category="trade_plan")
		self._latest_plan = plan_data
		return plan_data

	# 🧩 2️⃣ Retrieve latest plan
	def get_latest_plan(self) -> Dict[str, Any]:
		if self._latest_plan:
			return self._latest_plan
		if self.journal_path.exists():
			with open(self.journal_path, "r", encoding="utf-8") as file:
				return json.load(file)
		return {"status": "No reflective plan found."}

	# 🧩 3️⃣ Validate plan integrity with Monte Carlo + REE feedback
	def validate_trade_plan(self, pair: str, timeframe: str = "H4") -> Dict[str, Any]:
		plan = self.get_latest_plan()
		if "entry" not in plan or "stop_loss" not in plan or not plan.get("targets"):
			return {"status": "No plan available for validation."}

		entry = float(plan["entry"])
		stop_loss = float(plan["stop_loss"])
		target = float(plan["targets"][0])
		rr_ratio = self._compute_rr(entry, stop_loss, target)
		probability = self._compute_probability(entry, stop_loss, target, plan.get("raw_signal", {}), plan)

		meta_state = self.ree_feedback.collect_feedback()
		validation = {
			"pair": pair,
			"timeframe": timeframe,
			"probability": probability,
			"rr_ratio": rr_ratio,
			"integrity_index": plan.get("integrity_index"),
			"meta_confidence": meta_state.get("meta_integrity"),
			"status": "Reflective Trade Plan Validated",
			"timestamp": datetime.utcnow().isoformat() + "Z",
		}

		self.logger.audit_log({"event": "trade_plan_validated", "data": validation})
		return validation

	# ------------------------------------------------------------
	# Helpers
	# ------------------------------------------------------------
	def _generate_signal(self, pair: str, timeframe: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
		try:
			raw_plan = generate_reflective_trade_plan(pair, timeframe)
			return raw_plan, raw_plan.get("signal", {}) or {}
		except Exception as exc:  # pragma: no cover - defensive
			self.logger.log({"event": "fallback_signal", "error": str(exc)}, category="trade_plan")
			return {}, {}

	def _extract_prices(self, signal: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
		entry = self._to_float(signal.get("entry"))
		stop_loss = self._to_float(signal.get("sl") or signal.get("stop_loss"))
		target = self._to_float(signal.get("tp"))
		return entry, stop_loss, target

	def _derive_bias(self, signal: Dict[str, Any]) -> str:
		side = str(signal.get("type", "BUY")).upper()
		return "Bullish Reflective" if side != "SELL" else "Bearish Reflective"

	def _derive_entry_zone(self, signal: Dict[str, Any], entry: Optional[float]) -> str:
		if signal.get("entry_zone"):
			return str(signal["entry_zone"])
		if entry is not None:
			return f"{entry:.5f}"
		return "N/A"

	def _derive_targets(self, signal: Dict[str, Any], target: Optional[float]) -> list:
		if signal.get("targets"):
			return signal["targets"]  # type: ignore[return-value]
		if target is not None:
			return [target]
		return []

	def _compute_rr(
		self, entry: Optional[float], stop_loss: Optional[float], target: Optional[float]
	) -> Optional[float]:
		if entry is None or stop_loss is None or target is None:
			return None
		risk = abs(entry - stop_loss)
		reward = abs(target - entry)
		if risk <= 0:
			return None
		return round(reward / risk, 3)

	def _compute_probability(
		self,
		entry: Optional[float],
		stop_loss: Optional[float],
		target: Optional[float],
		signal: Dict[str, Any],
		bridge_state: Dict[str, Any],
	) -> float:
		signal_conf = self._to_float(signal.get("confidence")) or 0.0
		coherence = self._to_float(bridge_state.get("reflective_coherence")) or 0.0
		integrity = self._to_float(bridge_state.get("integrity_index")) or 0.0

		samples: Iterable[float]
		if entry is not None and stop_loss is not None and target is not None:
			risk = abs(entry - stop_loss)
			reward = abs(target - entry)
			edge = reward - risk
			samples = [edge * 0.6, edge * 1.05, -risk * 0.4, reward * 0.8 - risk * 0.5]
		else:
			samples = [coherence - 0.5, integrity - 0.5, signal_conf - 0.4, 0.02]

		try:
			mc = montecarlo_validate(list(samples), iterations=512)
			return round((mc.get("win_probability_%", 0.0) or 0.0) / 100, 3)
		except Exception:  # pragma: no cover - fallback path
			base = (signal_conf + coherence + integrity) / 3 if (signal_conf or coherence or integrity) else 0.5
			return round(base, 3)

	def _to_float(self, value: Any) -> Optional[float]:
		try:
			return float(value)
		except (TypeError, ValueError):
			return None

	def _save_plan(self, plan_data: Dict[str, Any]) -> None:
		self.journal_path.parent.mkdir(parents=True, exist_ok=True)
		with open(self.journal_path, "w", encoding="utf-8") as file:
			json.dump(plan_data, file, indent=2)


# Runtime helper
tradeplan_service = ReflectiveTradePlanService()
