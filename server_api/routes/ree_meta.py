"""Meta reflective routes bridging TII feedback into REE meta-learning."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from server_api.services.cloud_logger_service import CloudLoggerService
from server_api.services.ree_meta_service import REEMetaService


router = APIRouter()
ree_meta_service = REEMetaService()
logger = CloudLoggerService()


@router.post("/feedback")
async def post_meta_feedback() -> dict:
	"""Apply reflective feedback from TII into REE meta-learning."""
	try:
		feedback = ree_meta_service.process_feedback()
		return {
			"meta_cycle_id": feedback.get("meta_cycle_id"),
			"alpha_delta": feedback.get("alpha_delta"),
			"beta_delta": feedback.get("beta_delta"),
			"gamma_delta": feedback.get("gamma_delta"),
			"reflective_gradient": feedback.get("reflective_gradient"),
			"learning_gain": feedback.get("learning_gain"),
			"integrity_index": feedback.get("integrity_index"),
			"status": "REE Feedback Applied",
		}
	except Exception as exc:  # noqa: BLE001
		logger.error("REE meta feedback error", {"error": str(exc)})
		raise HTTPException(status_code=500, detail=f"REE meta feedback error: {exc}")


@router.get("/status")
async def get_meta_status() -> dict:
	"""Return current meta-layer integrity and drift state."""
	try:
		status = ree_meta_service.status()
		return {
			"meta_cycle_id": status.get("meta_cycle_id"),
			"meta_integrity": status.get("meta_integrity"),
			"drift_state": status.get("drift_state"),
			"reinforcement_state": status.get("reinforcement_state"),
			"reflective_coherence": status.get("reflective_coherence"),
			"alpha_beta_gamma": status.get("alpha_beta_gamma"),
			"status": "Meta Layer Reflective Sync Stable",
		}
	except Exception as exc:  # noqa: BLE001
		logger.error("REE meta status error", {"error": str(exc)})
		raise HTTPException(status_code=500, detail=f"REE meta status error: {exc}")


@router.post("/update_drift")
async def update_meta_drift() -> dict:
	"""Trigger an adaptive drift update for α–β–γ gradient."""
	try:
		result = ree_meta_service.update_drift()
		logger.info("Updated αβγ drift", result)
		return {
			"drift_update": result.get("gradient"),
			"alpha": result.get("alpha"),
			"beta": result.get("beta"),
			"gamma": result.get("gamma"),
			"integrity_index": result.get("integrity_index"),
			"status": "Meta Drift Field Updated",
		}
	except Exception as exc:  # noqa: BLE001
		logger.error("REE drift update error", {"error": str(exc)})
		raise HTTPException(status_code=500, detail=f"REE drift update error: {exc}")
