"""FastAPI Reflective Gateway — TUYUL FX Ultimate Hybrid AGI v6.0r∞."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server_api.config.settings import Settings
from server_api.routes import (
	execution,
	fta_alignment,
	fundamental,
	fusion,
	journal,
	ree_meta,
	reflective,
	risk,
	system,
	tradeplan,
	vault,
)
from server_api.services.cloud_logger_service import CloudLoggerService
from server_api.services.sync_service import ReflectiveSyncService


settings = Settings()

app = FastAPI(
	title=settings.app_title,
	version=settings.app_version,
	description=settings.app_description,
	contact=settings.contact,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_allow_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


logger = CloudLoggerService()
reflective_sync = ReflectiveSyncService()

# Route registration
app.include_router(fusion.router, prefix="/fusion", tags=["Fusion12 Layer"])
app.include_router(reflective.router, prefix="/reflective", tags=["Reflective Core"])
app.include_router(vault.router, prefix="/vault", tags=["Vault Management"])
app.include_router(tradeplan.router, prefix="/tradeplan", tags=["Trade Planning"])
app.include_router(execution.router, prefix="/execution", tags=["Execution Engine"])
app.include_router(ree_meta.router, prefix="/ree_meta", tags=["Meta Reflective Learning"])
app.include_router(fundamental.router, prefix="/fundamental", tags=["Fundamental Drive"])
app.include_router(fta_alignment.router, prefix="/fta", tags=["FTA Alignment"])
app.include_router(risk.router, prefix="/risk", tags=["Risk Management"])
app.include_router(journal.router, prefix="/journal", tags=["Reflective Journal"])
app.include_router(system.router, prefix="/system", tags=["System Monitor"])


@app.on_event("startup")
async def startup_event() -> None:
	logger.info("Starting TUYUL FX Reflective API Gateway...")
	await reflective_sync.sync_vaults()
	logger.info("Quad Vault synchronization completed.")


@app.on_event("shutdown")
async def shutdown_event() -> None:
	logger.info("Shutting down Reflective API Gateway...")
	await reflective_sync.flush_sessions()
	logger.info("Reflective memory safely stored in Journal Vault.")


@app.get("/", tags=["System"])
async def root() -> dict:
	state = await reflective_sync.status()
	integrity = reflective_sync.integrity_index or state.get("global_integrity") or 0.0
	return {
		"system": "TUYUL FX ULTIMATE HYBRID AGI v6.0r∞",
		"status": "Online – Reflective Harmony",
		"vault_state": state,
		"meta_cycle": "Active",
		"integrity_index": round(integrity, 3),
		"message": "Harmonic Reflective Discipline Locked.",
	}
