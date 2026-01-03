"""Reflective synchronization service for Quad Vault manifests.

This service keeps a lightweight view of vault integrity and exposes
async helpers used by the API gateway during startup/shutdown.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict


class ReflectiveSyncService:
	"""Synchronize and cache vault integrity and status."""

	def __init__(self) -> None:
		self.vault_index_path = "quad_vaults/manifests/vault_index.json"
		self.audit_path = "quad_vaults/manifests/vault_integrity_audit.yml"
		self.integrity_index: float = 0.0
		self._last_status: Dict[str, Any] | None = None

	async def sync_vaults(self) -> Dict[str, Any]:
		"""Load the latest vault manifest and cache integrity metrics."""
		status = await self.status()
		self.integrity_index = status.get("global_integrity", status.get("integrity", 0.0))
		self._last_status = status
		return status

	async def flush_sessions(self) -> None:
		"""Placeholder for flushing in-flight reflective sessions to storage."""
		return None

	async def status(self) -> Dict[str, Any]:
		"""Return the most recent vault status snapshot."""
		if self._last_status:
			return self._last_status
		return self._read_vault_index()

	def _read_vault_index(self) -> Dict[str, Any]:
		if not os.path.exists(self.vault_index_path):
			return {
				"timestamp": datetime.utcnow().isoformat(),
				"vaults": [],
				"integrity": 0.0,
				"status": "missing",
			}

		with open(self.vault_index_path, "r", encoding="utf-8") as file:
			data = json.load(file)

		integrity = data.get("governance", {}).get("global_integrity") or 0.0
		return {
			"timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
			"vaults": data.get("vault_registry", []),
			"integrity": integrity,
			"global_integrity": integrity,
			"vault_sync_state": data.get("governance", {}).get("vault_sync_state", "unknown"),
		}
