"""Reflective layer routes for running full reflective cycles."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter()


class ReflectiveCycleRequest(BaseModel):
	pair: str = Field(..., description="Symbol pair, e.g., XAUUSD")


@router.post("/run_cycle")
async def run_reflective_cycle(request: ReflectiveCycleRequest) -> dict:
	"""Run a reflective cycle across Fusion, TRQ–3D, and REE layers."""
	try:
		# Stub values; replace with ReflectiveCycleManager().run_cycle(...) results.
		result = {
			"pair": request.pair,
			"reflective_coherence": 0.956,
			"integrity_index": 0.969,
			"bias": "Bullish Reflective",
			"regime_state": "Mid Expansion",
			"probability": 0.942,
			"status": "Reflective cycle executed successfully",
		}
		return result
	except Exception as exc:  # noqa: BLE001
		raise HTTPException(status_code=500, detail=f"Reflective cycle error: {exc}")
