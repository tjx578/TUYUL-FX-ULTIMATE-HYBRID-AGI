"""
TUYUL FX Ultimate — System Route (v6.0r++)
-------------------------------------------------------
Handles reflective system monitoring, vault sync status,
TRQ–3D energy metrics, and meta-learning coherence report.
"""

from datetime import datetime
import json
import os

from fastapi import APIRouter, HTTPException

from core_reflective.hybrid_reflective_bridge_manager import HybridReflectiveBridgeManager
from core_meta.meta_learning_driver import MetaLearningDriver
from core_reflective.reflective_cycle_manager import ReflectiveCycleManager
from core_reflective.trq3d_engine import TRQ3DEngine
from core_reflective.reflective_logger import ReflectiveLogger


router = APIRouter()
logger = ReflectiveLogger("SystemRoute")


# ============================================================
# Status system endpoint
# ============================================================
@router.get("/system/status")
async def get_system_status():
	"""Return overall system reflective status including vault integrity, TRQ–3D coherence, alpha–beta–gamma sync, and meta-learning integrity."""
	try:
		bridge = HybridReflectiveBridgeManager()
		bridge_data = bridge.sync_all()

		meta_driver = MetaLearningDriver()
		meta_status = meta_driver.evaluate_cycle_status()

		trq3d = TRQ3DEngine()
		trq_data = trq3d.compute_reflective_energy("H1")

		status_report = {
			"timestamp": datetime.utcnow().isoformat(),
			"reflective_sync": bridge_data,
			"meta_learning": meta_status,
			"trq3d": trq_data,
			"integrity_index": round((meta_status["integrity_index"] + bridge_data["coherence_index"]) / 2, 3),
			"reflective_coherence": meta_status["reflective_coherence"],
			"harmonic_alignment": trq_data["reflective_intensity"],
			"system_status": "stable" if meta_status["integrity_index"] >= 0.94 else "degraded",
		}

		logger.log(f"System status requested: {status_report}")
		return status_report

	except Exception as exc:  # noqa: BLE001
		logger.log(f"System status error: {exc}")
		raise HTTPException(status_code=500, detail=f"System status error: {exc}")


# ============================================================
# Vault synchronization status
# ============================================================
@router.get("/system/vault-sync")
async def get_vault_sync_status():
	"""Return Quad Vault synchronization status (Hybrid, FX, Kartel, Journal). Reads state from quad_vaults/manifests/vault_index.json."""
	try:
		vault_path = "quad_vaults/manifests/vault_index.json"
		if not os.path.exists(vault_path):
			raise FileNotFoundError("Vault index file not found")

		with open(vault_path, "r", encoding="utf-8") as file:
			vault_data = json.load(file)

		response = {
			"timestamp": datetime.utcnow().isoformat(),
			"vaults": vault_data,
			"status": "synced" if all(v["integrity"] >= 0.94 for v in vault_data.values()) else "partial",
		}

		logger.log(f"Vault sync status retrieved: {response}")
		return response

	except Exception as exc:  # noqa: BLE001
		logger.log(f"Vault sync error: {exc}")
		raise HTTPException(status_code=500, detail=f"Vault sync error: {exc}")


# ============================================================
# Reflective performance summary
# ============================================================
@router.get("/system/performance")
async def get_reflective_performance_summary():
	"""Summarize reflective system performance metrics (Fusion to Reflective to Meta). Pulls data from logs and TRQ–3D analyzer."""
	try:
		trq3d = TRQ3DEngine()
		trq_data = trq3d.compute_reflective_energy("H4")

		meta_driver = MetaLearningDriver()
		metrics = meta_driver.get_reflective_performance_summary()

		performance = {
			"timestamp": datetime.utcnow().isoformat(),
			"trq3d_energy": trq_data["mean_energy"],
			"reflective_intensity": trq_data["reflective_intensity"],
			"meta_learning_gain": metrics["learning_gain"],
			"integrity_index": metrics["integrity_index"],
			"reflective_coherence": metrics["reflective_coherence"],
			"alpha_beta_gamma": metrics["alpha_beta_gamma"],
			"performance_status": "optimal" if metrics["integrity_index"] >= 0.95 else "adjusting",
		}

		logger.log(f"Reflective performance summary: {performance}")
		return performance

	except Exception as exc:  # noqa: BLE001
		logger.log(f"Performance summary error: {exc}")
		raise HTTPException(status_code=500, detail=f"Performance summary error: {exc}")


# ============================================================
# System diagnostic and cloud ping
# ============================================================
@router.get("/system/diagnostic")
async def run_diagnostic():
	"""Run a short reflective diagnostic test to ensure cloud sync and bridge coherence."""
	try:
		bridge = HybridReflectiveBridgeManager()
		result = bridge.sync_all()

		diagnostic = {
			"timestamp": datetime.utcnow().isoformat(),
			"reflective_sync": result["reflective_sync"],
			"neural_sync": result["neural_sync"],
			"quantum_sync": result["quantum_sync"],
			"coherence_index": result["coherence_index"],
			"diagnostic_status": "ok" if result["coherence_index"] >= 0.93 else "warning",
		}

		logger.log(f"Diagnostic completed: {diagnostic}")
		return diagnostic

	except Exception as exc:  # noqa: BLE001
		logger.log(f"Diagnostic error: {exc}")
		raise HTTPException(status_code=500, detail=f"Diagnostic error: {exc}")
