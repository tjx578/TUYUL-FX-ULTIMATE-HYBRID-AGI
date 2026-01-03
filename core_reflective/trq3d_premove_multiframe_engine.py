#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚛️ TRQ–3D Pre-Move Multi-Frame Engine v6.1r++
----------------------------------------------
TUYUL FX ULTIMATE HYBRID AGI v5.8r++ | Reflective Quantum Forecast Engine

Fungsi:
  • Menganalisis energi reflektif antar time frame (H1, H4, D1)
  • Memprediksi pergeseran energi reflektif 3–6 jam ke depan
  • Menentukan arah fase reflektif (Expansion / Reversal / Neutral)
"""

from __future__ import annotations

import datetime
import json
import math
from pathlib import Path
from typing import Dict, List

LOG_PATH = Path("data/logs/trq3d_premove_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def trq3d_premove_multiframe_engine(
    pair: str,
    timeframes: List[str] | None = None,
    price_data: Dict[str, List[float]] | None = None,
    volume_data: Dict[str, List[float]] | None = None,
) -> Dict[str, object]:
    """Prediksi energi reflektif 3–6 jam ke depan untuk beberapa timeframe."""

    if timeframes is None:
        timeframes = ["H1", "H4", "D1"]

    results: Dict[str, object] = {}
    projections: List[float] = []

    if not price_data or not volume_data:
        price_data = {
            "H1": [1.2715, 1.2731, 1.2740, 1.2752, 1.2760],
            "H4": [1.2680, 1.2710, 1.2735, 1.2750, 1.2765],
            "D1": [1.2500, 1.2610, 1.2690, 1.2740, 1.2760],
        }
        volume_data = {
            "H1": [310, 420, 580, 470, 530],
            "H4": [1200, 1380, 1450, 1320, 1400],
            "D1": [5200, 5500, 5800, 6000, 6300],
        }

    for tf in timeframes:
        price_series = price_data[tf]
        volume_series = volume_data[tf]

        deltas = [abs(price_series[i] - price_series[i - 1]) for i in range(1, len(price_series))]
        energy_units = [d * (v / sum(volume_series)) for d, v in zip(deltas, volume_series[1:])]

        mean_energy = sum(energy_units) / len(energy_units)
        reflective_intensity = min(1.5, round(math.tanh(mean_energy * 10), 3))
        projections.append(reflective_intensity)

        results[tf] = {
            "mean_energy": round(mean_energy, 5),
            "reflective_intensity": reflective_intensity,
            "phase": _phase_interpret(reflective_intensity),
        }

    h1, h4, d1 = projections
    avg_intensity = round(sum(projections) / len(projections), 3)
    momentum_gradient = round((h1 - h4) + (h4 - d1), 3)

    if avg_intensity >= 1.15:
        bias = "Expansion"
    elif avg_intensity <= 0.85:
        bias = "Reversal"
    else:
        bias = "Neutral"

    projection = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "pair": pair,
        "intensity_H1": h1,
        "intensity_H4": h4,
        "intensity_D1": d1,
        "avg_intensity": avg_intensity,
        "momentum_gradient": momentum_gradient,
        "bias_projection": bias,
        "note": "TRQ–3D Pre-Move Multi-Frame Engine v6.1r++",
    }

    _log(projection)
    return {"frames": results, "projection": projection}


def _phase_interpret(reflective_intensity: float) -> str:
    if reflective_intensity >= 1.2:
        return "Expansion"
    if reflective_intensity >= 0.9:
        return "Stable"
    return "Reversal"


def _log(data: dict) -> None:
    with open(LOG_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(data) + "\n")


__all__ = ["trq3d_premove_multiframe_engine"]
