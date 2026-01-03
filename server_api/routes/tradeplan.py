"""Trade planning routes for reflective trade plan generation."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from server_api.services.cloud_logger_service import CloudLoggerService
from server_api.services.reflective_tradeplan_service import ReflectiveTradePlanService


router = APIRouter()
service = ReflectiveTradePlanService()
logger = CloudLoggerService()


class TradePlanRequest(BaseModel):
	pair: str = Field(..., description="Symbol pair, e.g., XAUUSD")


@router.post("/generate")
async def generate_trade_plan(request: TradePlanRequest) -> dict:
	"""Generate a reflective trade plan for the given pair."""
	try:
		plan = service.generate_trade_plan(request.pair)
		logger.info("Generated reflective plan", {"pair": request.pair, "integrity_index": plan.get("integrity_index")})
		return plan
	except Exception as exc:  # noqa: BLE001
		raise HTTPException(status_code=500, detail=f"Trade plan error: {exc}")


@router.get("/latest")
async def latest_reflective_plan() -> dict:
	"""Return the latest generated reflective trade plan."""
	plan = service.get_latest_plan()
	return plan


@router.post("/validate")
async def validate_plan(request: TradePlanRequest) -> dict:
	"""Validate integrity and coherence for a reflective trade plan."""
	validation = service.validate_trade_plan(request.pair)
	return validation
