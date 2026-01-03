"""Execution routes for reflective trade execution bridge."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from server_api.services.cloud_logger_service import CloudLoggerService
from server_api.services.reflective_execution_service import ReflectiveExecutionService


router = APIRouter()
executor = ReflectiveExecutionService()
logger = CloudLoggerService()


class ExecutionRequest(BaseModel):
	pair: str = Field(..., description="Symbol pair, e.g., XAUUSD")


@router.post("/run")
async def execute_reflective_trade(request: ExecutionRequest) -> dict:
	"""Execute a reflective trade based on the latest trade plan."""
	try:
		result = executor.run_execution(request.pair)
		logger.info("Executed reflective trade", {"pair": request.pair, "pnl": result.get("pnl")})
		return result
	except Exception as exc:  # noqa: BLE001
		raise HTTPException(status_code=500, detail=f"Execution error: {exc}")


@router.get("/latest")
async def get_latest_execution() -> dict:
	"""Return the latest reflective execution result."""
	return executor.get_latest_execution()


@router.post("/audit")
async def audit_reflective_execution() -> dict:
	"""Run an integrity audit for the last reflective execution."""
	return executor.run_audit()
