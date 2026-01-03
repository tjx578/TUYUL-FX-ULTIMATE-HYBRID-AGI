"""Reflective system monitor routes for status, audit, and restart."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from server_api.services.cloud_logger_service import CloudLoggerService
from server_api.services.cloud_monitor_service import CloudMonitorService
from server_api.services.sync_service import ReflectiveSyncService


router = APIRouter()
sync_service = ReflectiveSyncService()
logger = CloudLoggerService()
monitor = CloudMonitorService()


@router.get("/system/status")
async def get_system_status() -> dict:
    """Return reflective system status including vault sync and runtime metrics."""
    try:
        status = await sync_service.status()
        monitor_data = monitor.collect_metrics()
        integrity = status.get("global_integrity", status.get("integrity", 0.0))
        return {
            "system": "TUYUL FX ULTIMATE HYBRID AGI v6.0r∞",
            "status": "Online",
            "vault_integrity": integrity,
            "reflective_coherence": integrity,
            "meta_integrity": integrity,
            "vault_sync_state": status.get("vault_sync_state", "unknown"),
            "reflective_cycle": "RFXC-20260103-001",
            "alpha_beta_gamma": [1.732, 0.986, 1.019],
            "drift_index": monitor_data.get("drift_index"),
            "latency_ms": monitor_data.get("latency_ms"),
            "reflective_intensity": monitor_data.get("reflective_intensity"),
            "timestamp": monitor_data.get("timestamp"),
            "message": "Reflective Harmony Stable",
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("System status error", {"error": str(exc)})
        raise HTTPException(status_code=500, detail=f"System status error: {exc}")


@router.post("/system/audit")
async def system_audit() -> dict:
    """Run a reflective system audit returning integrity and drift metrics."""
    try:
        audit = monitor.run_audit()
        logger.info("System reflective audit executed.")
        return {
            "integrity_index": audit.get("integrity_index"),
            "reflective_coherence": audit.get("coherence_index"),
            "meta_integrity": audit.get("meta_integrity"),
            "drift_index": audit.get("drift_index"),
            "reflective_field_state": audit.get("reflective_field_state"),
            "vault_latency_ms": audit.get("latency_ms"),
            "status": "System Reflective Audit Completed",
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("System audit error", {"error": str(exc)})
        raise HTTPException(status_code=500, detail=f"System audit error: {exc}")


@router.post("/system/restart")
async def restart_reflective_cycle() -> dict:
    """Restart reflective cycle and return new coherence snapshot."""
    try:
        result = await sync_service.restart_cycle()
        return {
            "reflective_cycle": result.get("cycle_id"),
            "fusion_confidence": result.get("fusion_confidence"),
            "reflective_coherence": result.get("reflective_coherence"),
            "integrity_index": result.get("integrity_index"),
            "status": "Reflective Cycle Restarted",
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("System restart error", {"error": str(exc)})
        raise HTTPException(status_code=500, detail=f"System restart error: {exc}")
