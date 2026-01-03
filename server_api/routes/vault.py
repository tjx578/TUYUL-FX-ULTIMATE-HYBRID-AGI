"""Vault layer routes for reflective vault status and synchronization."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from server_api.services.sync_service import ReflectiveSyncService


router = APIRouter()
sync_service = ReflectiveSyncService()


@router.get("/status")
async def vault_status() -> dict:
	"""Return Quad Vault status, integrity, and coherence."""
	try:
		status = await sync_service.status()
		integrity = status.get("global_integrity", status.get("integrity", 0.0))
		response = {
			"vaults": status.get("vaults", []),
			"integrity": integrity,
			"coherence": integrity,
			"state": status.get("vault_sync_state", "unknown"),
		}
		return response
	except Exception as exc:  # noqa: BLE001
		raise HTTPException(status_code=500, detail=f"Vault status error: {exc}")
