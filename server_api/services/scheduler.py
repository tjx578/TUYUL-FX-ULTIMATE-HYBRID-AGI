"""Local reflective scheduler for FastAPI runtime.

Runs a lightweight reflective loop (bridge sync → audit → meta learning) at
configurable intervals, reusing shared service singletons to avoid extra
bootstraps.
"""

from __future__ import annotations

import asyncio
import datetime
from typing import Optional

from server_api.services.cloud_logger_service import cloud_logger_service
from server_api.services.cloud_monitor_service import cloud_monitor_service
from server_api.services.ree_meta_service import ree_meta_service
from server_api.services.reflective_bridge_service import ReflectiveBridgeService, bridge_service


class Scheduler:
	"""Reflective temporal scheduler for local/test mode."""

	def __init__(self) -> None:
		self.bridge = bridge_service or ReflectiveBridgeService()
		self.meta = ree_meta_service
		self.monitor = cloud_monitor_service
		self.logger = cloud_logger_service
		self.active = False

	# 🧩 1️⃣ Jalankan Scheduler Lokal
	async def start(self, interval_minutes: int = 30, pair: str = "GBPUSD") -> None:
		self.active = True
		self.logger.info(
			"[LOCAL SCHEDULER] Started",
			{"interval_minutes": interval_minutes, "pair": pair},
		)
		while self.active:
			try:
				now = datetime.datetime.utcnow().isoformat() + "Z"
				self.logger.info("[LOCAL SCHEDULER] Tick", {"timestamp": now})

				bridge_state = self.bridge.run_reflective_bridge(pair)
				audit = self.monitor.run_audit()
				meta_update = self.meta.run_meta_learning_cycle()

				self.logger.info(
					"[LOCAL SCHEDULER] Bridge & Meta",
					{
						"reflective_coherence": bridge_state.get("reflective_coherence"),
						"integrity_index": bridge_state.get("integrity_index"),
						"meta_integrity": meta_update.get("meta_integrity"),
					},
				)
				self.logger.info(
					"[LOCAL SCHEDULER] Audit",
					{"reflective_field_state": audit.get("reflective_field_state")},
				)
			except Exception as exc:  # pragma: no cover - defensive path
				self.logger.error("[LOCAL SCHEDULER ERROR]", {"error": str(exc)})

			await asyncio.sleep(max(1, interval_minutes) * 60)

	# 🧩 2️⃣ Hentikan Scheduler
	def stop(self) -> None:
		self.active = False
		self.logger.warn("[LOCAL SCHEDULER] Stopped manually.")


# Runtime helper
scheduler = Scheduler()
