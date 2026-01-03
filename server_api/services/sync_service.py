"""Reflective synchronization engine for Quad Vault and Meta layer.

Keeps vault coherence in sync, persists integrity/coherence snapshots, and
provides hooks for restart and runtime status used by the API gateway.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from time import perf_counter
from typing import Any, Dict

from core_meta.ree_integrity_controller import REEIntegrityController
from core_reflective.hybrid_reflective_bridge_manager import HybridReflectiveBridgeManager
from core_reflective.reflective_cycle_manager import reflective_cycle_manager
from core_reflective.reflective_logger import ReflectiveLogger


class ReflectiveSyncService:
	"""Synchronize vaults, meta layer, and cache integrity metrics."""

	def __init__(self) -> None:
		self.vault_index_path = "quad_vaults/manifests/vault_index.json"
		self.integrity_cache_path = "data/integrity/system_integrity.json"
		self.coherence_cache_path = "data/integrity/coherence_index.json"
		self.drift_log_path = "data/integrity/frpc_drift_log.json"
		self.logger = ReflectiveLogger("sync_service")
		self.bridge = HybridReflectiveBridgeManager()
		self.ree = REEIntegrityController()
		self.integrity_index: float = 0.0
		self.coherence_index: float = 0.0
		self.meta_integrity: float = 0.0
		self._last_status: Dict[str, Any] | None = None

	# 🧩 1️⃣ Sinkronisasi Semua Vault
	async def sync_vaults(self) -> Dict[str, Any]:
		start = perf_counter()
		bridge_sync = self.bridge.sync_all()
		meta_state = self.ree.evaluate_integrity()

		self.integrity_index = round(
			(bridge_sync.get("integrity_index", 0.0) + meta_state.get("integrity_index", 0.0)) / 2,
			3,
		)
		self.coherence_index = round(
			(bridge_sync.get("coherence_index", 0.0) + meta_state.get("reflective_coherence", 0.0)) / 2,
			3,
		)
		self.meta_integrity = meta_state.get("integrity_index", 0.0)

		latency_ms = int((perf_counter() - start) * 1000)

		result = {
			"integrity_index": self.integrity_index,
			"coherence_index": self.coherence_index,
			"meta_integrity": self.meta_integrity,
			"recovery_action": meta_state.get("recovery_action"),
			"sync_state": bridge_sync.get("sync_state"),
			"latency_ms": latency_ms,
			"timestamp": datetime.utcnow().isoformat() + "Z",
			"status": "Vault Sync Completed",
		}

		self._last_status = result
		self._persist_integrity_cache(result)
		self.logger.log({"event": "vault_sync", "data": result}, category="sync")
		return result

	# 🧩 2️⃣ Cek Status Runtime Sinkronisasi
	async def status(self) -> Dict[str, Any]:
		if self._last_status:
			return self._last_status
		return self._read_vault_index()

	# 🧩 3️⃣ Restart Reflective Cycle
	async def restart_cycle(self) -> Dict[str, Any]:
		cycle_payload = reflective_cycle_manager(
			{
				"pair": "GLOBAL",
				"timeframe": "SYNC",
				"fusion_score": self.coherence_index or 0.95,
			}
		)
		self._last_status = None
		self.logger.log({"event": "cycle_restart", "data": cycle_payload}, category="cycle")
		return {
			"cycle_id": cycle_payload.get("timestamp"),
			"reflective_coherence": cycle_payload.get("reflective_intensity"),
			"integrity_index": self.integrity_index,
			"status": cycle_payload.get("status"),
		}

	# 🧩 4️⃣ Simpan State Sinkronisasi
	async def flush_sessions(self) -> None:
		if self._last_status:
			self._persist_integrity_cache(self._last_status)
			self.logger.log({"event": "sync_flush", "data": self._last_status}, category="sync")
		return None

	# ------------------------------------------------------------
	# Helpers
	# ------------------------------------------------------------
	def _read_vault_index(self) -> Dict[str, Any]:
		if not os.path.exists(self.vault_index_path):
			return {
				"timestamp": datetime.utcnow().isoformat() + "Z",
				"vaults": [],
				"integrity": 0.0,
				"status": "missing",
			}

		with open(self.vault_index_path, "r", encoding="utf-8") as file:
			data = json.load(file)

		integrity = data.get("governance", {}).get("global_integrity") or 0.0
		coherence = data.get("governance", {}).get("coherence_index", integrity)
		return {
			"timestamp": data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
			"vaults": data.get("vault_registry", []),
			"integrity": integrity,
			"global_integrity": integrity,
			"coherence_index": coherence,
			"vault_sync_state": data.get("governance", {}).get("vault_sync_state", "unknown"),
		}

	def _persist_integrity_cache(self, payload: Dict[str, Any]) -> None:
		os.makedirs(os.path.dirname(self.integrity_cache_path), exist_ok=True)
		with open(self.integrity_cache_path, "w", encoding="utf-8") as file:
			json.dump(
				{
					"integrity_index": payload.get("integrity_index", 0.0),
					"meta_integrity": payload.get("meta_integrity", 0.0),
					"timestamp": payload.get("timestamp"),
				},
				file,
				indent=2,
			)

		with open(self.coherence_cache_path, "w", encoding="utf-8") as file:
			json.dump(
				{
					"coherence_index": payload.get("coherence_index", 0.0),
					"timestamp": payload.get("timestamp"),
				},
				file,
				indent=2,
			)

		with open(self.drift_log_path, "a", encoding="utf-8") as file:
			file.write(json.dumps(payload) + "\n")
