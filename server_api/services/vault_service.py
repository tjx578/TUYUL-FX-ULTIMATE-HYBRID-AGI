"""Quad Vault reflective service for integrity, coherence, and sync audits."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping

import yaml

from core_meta.ree_integrity_controller import REEIntegrityController
from core_reflective.hybrid_reflective_bridge_manager import HybridReflectiveBridgeManager
from core_reflective.reflective_logger import ReflectiveLogger


VERSION = "v6.0r∞"
SAFE_INTEGRITY = 0.96
SAFE_COHERENCE = 0.95
SAFE_DRIFT = 0.007


@dataclass
class VaultStatusSnapshot:
	vaults: Dict[str, Dict[str, Any]]
	integrity_index: float
	coherence_index: float
	meta_integrity: float
	sync_state: str
	timestamp: str

	def as_dict(self) -> Dict[str, Any]:
		return asdict(self)


@dataclass
class VaultAuditSnapshot:
	global_integrity: float
	coherence_index: float
	drift_index: float
	meta_integrity: float
	reflective_field_state: str
	vaults: Dict[str, Dict[str, Any]]
	timestamp: str

	def as_dict(self) -> Dict[str, Any]:
		return asdict(self)


class VaultService:
	"""Central handler for Quad Vault integrity and reflective coherence."""

	def __init__(self) -> None:
		self.bridge = HybridReflectiveBridgeManager()
		self.logger = ReflectiveLogger("vault_service")
		self.ree_controller = REEIntegrityController()

		self.vault_manifest_path = Path("quad_vaults/manifests/vault_integrity_audit.yml")
		self.index_path = Path("quad_vaults/manifests/vault_index.json")
		self.integrity_cache_path = Path("data/integrity/system_integrity.json")
		self.coherence_cache_path = Path("data/integrity/coherence_index.json")
		self.drift_log_path = Path("data/integrity/frpc_drift_log.json")

	# ============================================================
	# 🧩 1️⃣ Ambil Status Quad Vault
	# ============================================================
	def get_status(self) -> VaultStatusSnapshot:
		meta_snapshot = self._evaluate_meta_layer()
		vaults = self._collect_vault_status(meta_snapshot)

		integrity_index = self._compute_integrity_index(vaults, meta_snapshot["meta_integrity"])
		coherence_index = self._compute_coherence_index(vaults, meta_snapshot["reflective_coherence"])
		sync_state = self._derive_sync_state(integrity_index, coherence_index, meta_snapshot["drift_index"])

		snapshot = VaultStatusSnapshot(
			vaults=vaults,
			integrity_index=integrity_index,
			coherence_index=coherence_index,
			meta_integrity=meta_snapshot["meta_integrity"],
			sync_state=sync_state,
			timestamp=meta_snapshot["timestamp"],
		)

		self._cache_runtime(snapshot, meta_snapshot)
		return snapshot

	# ============================================================
	# 🧩 2️⃣ Jalankan Audit Integritas
	# ============================================================
	def run_integrity_audit(self) -> VaultAuditSnapshot:
		meta_snapshot = self._evaluate_meta_layer()
		vaults = self._collect_vault_status(meta_snapshot)

		integrity_index = self._compute_integrity_index(vaults, meta_snapshot["meta_integrity"])
		coherence_index = self._compute_coherence_index(vaults, meta_snapshot["reflective_coherence"])

		audit_payload = {
			"global_integrity": integrity_index,
			"coherence_index": coherence_index,
			"drift_index": meta_snapshot["drift_index"],
			"meta_integrity": meta_snapshot["meta_integrity"],
			"reflective_field_state": meta_snapshot["reflective_field_state"],
			"timestamp": meta_snapshot["timestamp"],
		}

		self._write_audit_file(vaults, audit_payload)
		self.logger.log({"event": "vault_integrity_audit", **audit_payload}, category="audit")

		snapshot = VaultAuditSnapshot(vaults=vaults, **audit_payload)
		self._cache_runtime(
			VaultStatusSnapshot(
				vaults=vaults,
				integrity_index=integrity_index,
				coherence_index=coherence_index,
				meta_integrity=meta_snapshot["meta_integrity"],
				sync_state=self._derive_sync_state(
					integrity_index, coherence_index, meta_snapshot["drift_index"]
				),
				timestamp=meta_snapshot["timestamp"],
			),
			meta_snapshot,
		)
		return snapshot

	# ============================================================
	# 🧩 3️⃣ Update Vault Index File
	# ============================================================
	def update_vault_index(self) -> Dict[str, Any]:
		status = self.get_status()

		index_payload = {
			"version": VERSION,
			"timestamp": status.timestamp,
			"vault_registry": self._vault_registry_from_status(status.vaults),
			"governance": {
				"global_integrity": status.integrity_index,
				"coherence_index": status.coherence_index,
				"meta_integrity": status.meta_integrity,
				"vault_sync_state": status.sync_state,
			},
		}

		self._write_json(self.index_path, index_payload)
		self.logger.log({"event": "vault_index_updated", "path": str(self.index_path)})
		return index_payload

	# ============================================================
	# 🛠️ Internal helpers
	# ============================================================
	def _evaluate_meta_layer(self) -> Dict[str, Any]:
		ree_snapshot = self.ree_controller.evaluate_integrity()
		drift_values = {
			"alpha": float(self.ree_controller.state.get("alpha_drift", 0.0)),
			"beta": float(self.ree_controller.state.get("beta_drift", 0.0)),
			"gamma": float(self.ree_controller.state.get("gamma_drift", 0.0)),
		}
		drift_index = round(sum(abs(value) for value in drift_values.values()) / 3, 3)

		reflective_field_state = "Harmonic Expansion"
		if drift_index > SAFE_DRIFT:
			reflective_field_state = "Stabilizing"
		if drift_index > SAFE_DRIFT * 2:
			reflective_field_state = "Drift Correction"

		return {
			"meta_integrity": ree_snapshot["integrity_index"],
			"reflective_coherence": ree_snapshot["reflective_coherence"],
			"drift_index": drift_index,
			"drift": drift_values,
			"reflective_field_state": reflective_field_state,
			"timestamp": ree_snapshot["timestamp"],
		}

	def _collect_vault_status(self, meta_snapshot: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
		if hasattr(self.bridge, "get_vault_status"):
			try:
				return self.bridge.get_vault_status()  # type: ignore[attr-defined]
			except Exception:
				self.logger.log({"event": "vault_status_fallback"}, category="warning")

		coherence = float(meta_snapshot.get("reflective_coherence", 0.0))
		integrity = float(meta_snapshot.get("meta_integrity", 0.0))
		drift = float(meta_snapshot.get("drift_index", 0.0))

		base = round(max(integrity, coherence), 3)
		drift_penalty = round(min(drift * 3, 0.02), 3)

		return {
			"hybrid": {
				"integrity_index": base,
				"coherence_index": round(coherence - drift_penalty, 3),
				"state": "online",
			},
			"fx": {
				"integrity_index": round(base - 0.003, 3),
				"coherence_index": round(coherence - drift_penalty - 0.002, 3),
				"state": "online",
			},
			"kartel": {
				"integrity_index": round(base - 0.004, 3),
				"coherence_index": round(coherence - drift_penalty - 0.003, 3),
				"state": "online",
			},
			"journal": {
				"integrity_index": round(base - 0.002, 3),
				"coherence_index": round(coherence - drift_penalty - 0.001, 3),
				"state": "online",
			},
		}

	def _compute_integrity_index(self, vaults: Mapping[str, Mapping[str, Any]], meta_integrity: float) -> float:
		if not vaults:
			return round(meta_integrity, 3)
		average_vault_integrity = sum(float(v["integrity_index"]) for v in vaults.values()) / len(vaults)
		return round((average_vault_integrity + meta_integrity) / 2, 3)

	def _compute_coherence_index(
		self, vaults: Mapping[str, Mapping[str, Any]], reflective_coherence: float
	) -> float:
		if not vaults:
			return round(reflective_coherence, 3)
		coherence_values = [float(v["coherence_index"]) for v in vaults.values()]
		coherence_values.append(reflective_coherence)
		return round(sum(coherence_values) / len(coherence_values), 3)

	def _derive_sync_state(self, integrity: float, coherence: float, drift: float) -> str:
		if integrity >= SAFE_INTEGRITY and coherence >= SAFE_COHERENCE and drift <= SAFE_DRIFT:
			return "Unified"
		if drift > SAFE_DRIFT * 2:
			return "Drift Correction"
		return "Stabilizing"

	def _write_audit_file(self, vaults: Mapping[str, Any], result: Mapping[str, Any]) -> None:
		self.vault_manifest_path.parent.mkdir(parents=True, exist_ok=True)
		with open(self.vault_manifest_path, "w", encoding="utf-8") as file:
			yaml.safe_dump(
				{
					"version": VERSION,
					"timestamp": result["timestamp"],
					"vaults": vaults,
					"global_integrity": result["global_integrity"],
					"coherence_index": result["coherence_index"],
					"drift_index": result["drift_index"],
					"meta_integrity": result["meta_integrity"],
					"reflective_field_state": result["reflective_field_state"],
				},
				file,
				sort_keys=False,
			)

	def _vault_registry_from_status(self, vaults: Mapping[str, Mapping[str, Any]]) -> list[Dict[str, Any]]:
		registry: list[Dict[str, Any]] = []
		for name, payload in vaults.items():
			registry.append(
				{
					"name": f"{name.title()} Vault",
					"key": name,
					"integrity_index": float(payload.get("integrity_index", 0.0)),
					"coherence_index": float(payload.get("coherence_index", 0.0)),
					"state": payload.get("state", "unknown"),
				}
			)
		return registry

	def _cache_runtime(self, status: VaultStatusSnapshot, meta_snapshot: Mapping[str, Any]) -> None:
		payload = {
			"timestamp": status.timestamp,
			"integrity_index": status.integrity_index,
			"coherence_index": status.coherence_index,
			"meta_integrity": status.meta_integrity,
			"drift_index": meta_snapshot.get("drift_index", 0.0),
			"sync_state": status.sync_state,
			"version": VERSION,
		}

		self._write_json(self.integrity_cache_path, payload)
		self._write_json(self.coherence_cache_path, {"timestamp": status.timestamp, "coherence_index": status.coherence_index})
		self._write_json(
			self.drift_log_path,
			{
				"timestamp": status.timestamp,
				"drift_index": meta_snapshot.get("drift_index", 0.0),
				"alpha": meta_snapshot.get("drift", {}).get("alpha", 0.0),
				"beta": meta_snapshot.get("drift", {}).get("beta", 0.0),
				"gamma": meta_snapshot.get("drift", {}).get("gamma", 0.0),
			},
		)

	def _write_json(self, path: Path, payload: Mapping[str, Any]) -> None:
		path.parent.mkdir(parents=True, exist_ok=True)
		with open(path, "w", encoding="utf-8") as file:
			json.dump(payload, file, indent=2)


__all__ = ["VaultService", "VaultStatusSnapshot", "VaultAuditSnapshot"]
