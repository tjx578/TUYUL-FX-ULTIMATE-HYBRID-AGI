#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌀 Adaptive Field Stabilizer v6.0r++
-----------------------------------
TUYUL FX ULTIMATE HYBRID AGI v5.8r++ | Reflective Gradient Orchestrator (RGO Layer)

Fungsi:
  • Menstabilkan α–β–γ field berdasarkan output TRQ–3D
  • Mengukur gradient drift reflektif antar layer
  • Menentukan status sinkronisasi medan (Accumulation / Expansion / Reversal)
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Dict

LOG_PATH = Path("data/logs/reflective_field_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def adaptive_field_stabilizer(
    alpha: float, beta: float, gamma: float, integrity_threshold: float = 0.95
) -> Dict[str, object]:
    """Menghitung stabilitas gradien α–β–γ reflektif dan menentukan status field."""

    gradient = round((abs(alpha - beta) + abs(beta - gamma) + abs(alpha - gamma)) / 3, 5)

    if gradient < 0.02:
        field_state = "Accumulation"
    elif gradient < 0.05:
        field_state = "Expansion"
    else:
        field_state = "Reversal"

    integrity_index = round(max(0.85, 1.0 - gradient / 0.1), 3)

    if integrity_index >= integrity_threshold:
        sync_cluster = ["Hybrid", "FX", "Kartel", "Journal"]
    elif integrity_index >= 0.9:
        sync_cluster = ["Hybrid", "FX", "Kartel"]
    else:
        sync_cluster = ["Hybrid", "FX"]

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "gradient": gradient,
        "integrity_index": integrity_index,
        "field_state": field_state,
        "sync_cluster": sync_cluster,
        "note": "Adaptive Field Stabilizer v6.0r++ — Reflective Gradient Control",
    }

    _log(result)
    return result


def _log(data: dict) -> None:
    with open(LOG_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(data) + "\n")


__all__ = ["adaptive_field_stabilizer"]
