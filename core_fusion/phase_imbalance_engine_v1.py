"""Phase Imbalance Engine v1 (Reflective Fusion Mode).

This module measures phase imbalance across price, volume, and time dimensions for
TUYUL FX ULTIMATE HYBRID AGI v5.8r++ (Quad Vault Reflective Discipline Mode).
It outputs a reflective score and imbalance zone used by TRQ–3D and RGO layers.
"""

from __future__ import annotations

import datetime
import json
import math
from pathlib import Path
from typing import Any, Dict

from core_reflective.reflective_logger import log_reflective_event
from server_api.services.cloud_logger_service import cloud_log_event


LOG_PATH = Path("data/logs/phase_imbalance_log.json")


def phase_imbalance_engine_v1(
    price_change: float,
    volume_change: float,
    time_delta: float,
    atr: float,
    reflective_intensity: float = 1.0,
    trq_energy: float = 1.0,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
) -> Dict[str, Any]:
    """Calculate the reflective Phase Imbalance Index for TRQ–3D integration.

    The score blends normalized energies from price momentum, volume expansion, and
    temporal drift. It is amplified by reflective intensity, TRQ energy, and RGO
    alpha/beta/gamma synchronization.
    """

    if not _inputs_are_valid(price_change, volume_change, time_delta, atr):
        return {"status": "invalid_input"}

    price_energy, volume_energy, time_energy = _compute_energy_components(
        price_change=price_change,
        volume_change=volume_change,
        time_delta=time_delta,
        atr=atr,
    )

    phase_balance = (price_energy + volume_energy + time_energy) / 3.0
    imbalance_spread = (
        abs(price_energy - phase_balance)
        + abs(volume_energy - phase_balance)
        + abs(time_energy - phase_balance)
    ) / 3.0

    coherence_ratio = 1.0 / (1.0 + imbalance_spread)
    alpha_sync = max((alpha + beta + gamma) / 3.0, 0.0)

    reflective_score = (
        phase_balance
        * coherence_ratio
        * max(reflective_intensity, 0.0)
        * max(trq_energy, 0.0)
        * (alpha_sync or 1.0)
    )

    zone = _classify_zone(reflective_score)

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "price_energy": round(price_energy, 4),
        "volume_energy": round(volume_energy, 4),
        "time_energy": round(time_energy, 4),
        "phase_balance": round(phase_balance, 4),
        "imbalance_spread": round(imbalance_spread, 4),
        "coherence_ratio": round(coherence_ratio, 4),
        "reflective_score": round(reflective_score, 4),
        "zone": zone,
        "alpha": round(alpha, 4),
        "beta": round(beta, 4),
        "gamma": round(gamma, 4),
        "status": "ok",
        "note": "Phase Imbalance Engine v1 – Reflective Mode",
    }

    _log_to_vault(result)
    log_reflective_event("PHASE_IMBALANCE", result)
    cloud_log_event("fusion.phase_imbalance", result)

    return result


def _compute_energy_components(
    *, price_change: float, volume_change: float, time_delta: float, atr: float
) -> tuple[float, float, float]:
    price_energy = min(abs(price_change) / atr, 10.0)
    volume_energy = min(math.log1p(abs(volume_change)), 10.0)
    time_energy = min(math.log1p(abs(time_delta)), 10.0)
    return price_energy, volume_energy, time_energy


def _classify_zone(reflective_score: float) -> str:
    if reflective_score >= 1.2:
        return "Overextension"
    if reflective_score <= 0.7:
        return "Compression"
    return "Equilibrium"


def _inputs_are_valid(
    price_change: float, volume_change: float, time_delta: float, atr: float
) -> bool:
    has_non_positive = any(
        value <= 0 for value in [abs(price_change), abs(volume_change), abs(time_delta), atr]
    )
    return not has_non_positive and math.isfinite(atr)


def _log_to_vault(data: Dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        json.dump(data, log_file, ensure_ascii=False)
        log_file.write("\n")


__all__ = ["phase_imbalance_engine_v1"]


if __name__ == "__main__":
    sample = phase_imbalance_engine_v1(
        price_change=0.0018,
        volume_change=1.25,
        time_delta=0.5,
        atr=0.0009,
        reflective_intensity=1.1,
        trq_energy=1.05,
        alpha=1.02,
        beta=0.98,
        gamma=1.0,
    )
    print(json.dumps(sample, indent=2))
