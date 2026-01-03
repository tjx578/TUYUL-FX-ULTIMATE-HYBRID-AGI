#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔁 TII Reflective Feedback Adapter v6 — Production
-------------------------------------------------
Mengonversi hasil TII menjadi feedback adaptif untuk Meta-Learning Layer (REE).
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Dict, Any

LOG_PATH = Path("data/logs/tii_feedback_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def tii_reflective_feedback_adapter_v6_production(tii_data: Dict[str, Any]) -> Dict[str, Any]:
    feedback_strength = round(tii_data["tii"] * 0.95, 3)
    ree_signal = "positive" if tii_data["tii"] >= 0.85 else "neutral" if tii_data["tii"] >= 0.7 else "negative"

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "tii": tii_data["tii"],
        "status": tii_data["status"],
        "ree_feedback_strength": feedback_strength,
        "ree_signal": ree_signal,
        "note": "Reflective feedback generated from TII engine v3.2",
    }

    _log(result)
    return result


def _log(data: Dict[str, Any]) -> None:
    with open(LOG_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(data) + "\n")


__all__ = ["tii_reflective_feedback_adapter_v6_production"]
