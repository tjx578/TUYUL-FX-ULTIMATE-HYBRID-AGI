#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌌 Phase Resonance Engine v1.5 (Reflective Adaptive Mode)
---------------------------------------------------------
TUYUL FX ULTIMATE AGI v5.8r++ | Quad Vault Reflective Discipline Mode

Evolusi dari Phase Imbalance Engine:
  • Menilai keseimbangan fase (Price × Time × Volume)
  • Mengukur resonansi reflektif dengan TRQ–3D Field
  • Beradaptasi dengan feedback αβγ drift dari Meta-Learning Layer
  • Menulis hasil ke Journal Vault (phase_resonance_log.json)
"""

from __future__ import annotations

import datetime
import json
import math
from pathlib import Path


LOG_PATH = Path("data/logs/phase_resonance_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def phase_resonance_engine_v1_5(
    price_change: float,
    volume_change: float,
    time_delta: float,
    atr: float,
    trq_energy: float = 1.0,
    reflective_intensity: float = 1.0,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
    alpha_drift: float = 0.0,
    beta_drift: float = 0.0,
    gamma_drift: float = 0.0,
    integrity_index: float = 0.97,
) -> dict[str, object]:
    """Menghitung Phase Resonance Index (PRI) dan Resonant Field State adaptif."""

    if any(v <= 0 for v in [abs(price_change), abs(volume_change), abs(time_delta), atr]):
        return {"status": "invalid input"}

    price_energy = abs(price_change / atr)
    volume_energy = math.log1p(volume_change)
    time_energy = math.log1p(time_delta)

    energy_balance = (price_energy + volume_energy + time_energy) / 3
    imbalance_factor = (
        abs(price_energy - volume_energy)
        + abs(price_energy - time_energy)
        + abs(volume_energy - time_energy)
    ) / 3

    drift_factor = (abs(alpha_drift) + abs(beta_drift) + abs(gamma_drift)) / 3
    drift_correction = max(0.85, 1.0 - drift_factor)

    alpha_sync = (alpha + beta + gamma) / 3
    pri = (
        energy_balance
        / (1 + imbalance_factor)
        * trq_energy
        * reflective_intensity
        * alpha_sync
        * drift_correction
    )

    if pri >= 1.3:
        field_state = "Expansion Resonance"
    elif 0.9 <= pri < 1.3:
        field_state = "Equilibrium Resonance"
    elif 0.7 <= pri < 0.9:
        field_state = "Adaptive Compression"
    else:
        field_state = "Phase Drift Detected"

    coherence_score = (pri / (1 + drift_factor)) * integrity_index

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "price_energy": round(price_energy, 3),
        "volume_energy": round(volume_energy, 3),
        "time_energy": round(time_energy, 3),
        "energy_balance": round(energy_balance, 3),
        "imbalance_factor": round(imbalance_factor, 3),
        "phase_resonance_index": round(pri, 3),
        "field_state": field_state,
        "alpha": round(alpha, 3),
        "beta": round(beta, 3),
        "gamma": round(gamma, 3),
        "alpha_drift": round(alpha_drift, 4),
        "beta_drift": round(beta_drift, 4),
        "gamma_drift": round(gamma_drift, 4),
        "drift_correction": round(drift_correction, 3),
        "reflective_intensity": round(reflective_intensity, 3),
        "trq_energy": round(trq_energy, 3),
        "integrity_index": round(integrity_index, 3),
        "coherence_score": round(coherence_score, 3),
        "note": "Phase Resonance Engine v1.5 (Reflective Adaptive Mode)",
    }

    _log_to_file(result)
    return result


def _log_to_file(data: dict) -> None:
    """Simpan hasil ke Journal Vault log reflektif."""
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(data) + "\n")


__all__ = ["phase_resonance_engine_v1_5"]
