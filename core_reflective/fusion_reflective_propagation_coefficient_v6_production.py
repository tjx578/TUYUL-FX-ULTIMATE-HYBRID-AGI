#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fusion Reflective Propagation Coefficient v6 (FRPC) — Production Mode.

Bridges Fusion Equilibrium output with TRQ–3D / Meta Coherence layers to compute
the global reflective synchronization coefficient and state.
"""

from __future__ import annotations

import datetime
import json
import math
from pathlib import Path
from typing import Any

LOG_PATH = Path("data/logs/reflective_propagation_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def fusion_reflective_propagation_coefficient_v6(
    fusion_score: float,
    trq_energy: float,
    reflective_intensity: float,
    alpha: float,
    beta: float,
    gamma: float,
    integrity_index: float = 0.97,
) -> dict[str, Any]:
    """Compute reflective propagation coefficient across Fusion → TRQ–3D → Meta layers."""
    inputs = [fusion_score, trq_energy, reflective_intensity]
    if any(value is None or value <= 0 for value in inputs):
        return {"status": "invalid input"}

    fusion_norm = math.tanh(fusion_score)
    trq_norm = math.tanh(trq_energy)
    intensity_norm = math.tanh(reflective_intensity)

    alpha_sync = (alpha + beta + gamma) / 3
    gamma_phase = (alpha - gamma) ** 2 + (beta - alpha) ** 2

    frpc = (
        (fusion_norm * trq_norm * intensity_norm * alpha_sync) / (1 + gamma_phase)
    ) * integrity_index

    if frpc >= 0.95:
        propagation_state = "Full Reflective Sync"
    elif 0.85 <= frpc < 0.95:
        propagation_state = "Partial Reflective Sync"
    elif 0.7 <= frpc < 0.85:
        propagation_state = "Reflective Drift Detected"
    else:
        propagation_state = "Desynchronized"

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "fusion_score": round(fusion_score, 3),
        "trq_energy": round(trq_energy, 3),
        "reflective_intensity": round(reflective_intensity, 3),
        "alpha": round(alpha, 3),
        "beta": round(beta, 3),
        "gamma": round(gamma, 3),
        "alpha_sync": round(alpha_sync, 3),
        "gamma_phase": round(gamma_phase, 4),
        "integrity_index": round(integrity_index, 3),
        "frpc": round(frpc, 3),
        "propagation_state": propagation_state,
        "note": "Fusion Reflective Propagation Coefficient v6 – Production Mode",
    }

    _log_to_vault(result)
    return result


def _log_to_vault(data: dict[str, Any]) -> None:
    """Persist reflective propagation result to the journal vault."""
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(data) + "\n")


__all__ = ["fusion_reflective_propagation_coefficient_v6"]
