#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Reflective Volume Quadrant Engine v6.0r++
--------------------------------------------
TUYUL FX ULTIMATE HYBRID AGI v5.8r++ | Reflective Volume Analysis System (RVQE Layer)

Fungsi:
  • Menghitung pembagian volume ke dalam 4 kuadran reflektif (Q1–Q4)
  • Mengukur Reflective Volume Imbalance (RVI)
  • Mengidentifikasi zona akumulasi, ekspansi, dan likuiditas aktif
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Dict, List

LOG_PATH = Path("data/logs/reflective_volume_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def reflective_volume_quadrant_engine(
    price_series: List[float],
    volume_series: List[float],
    vwap: float,
    threshold: float = 0.0008,
) -> Dict[str, object]:
    """Hitung distribusi volume reflektif ke 4 kuadran harga–volume."""

    if len(price_series) < 4 or len(volume_series) < 4:
        return {"status": "Insufficient data for RVQE"}

    high = max(price_series)
    low = min(price_series)
    midpoint = (high + low) / 2
    range_half = (high - low) / 2

    q1_vol = sum(v for p, v in zip(price_series, volume_series) if p > midpoint + threshold)
    q2_vol = sum(v for p, v in zip(price_series, volume_series) if midpoint < p <= midpoint + threshold)
    q3_vol = sum(v for p, v in zip(price_series, volume_series) if midpoint - threshold < p <= midpoint)
    q4_vol = sum(v for p, v in zip(price_series, volume_series) if p <= midpoint - threshold)

    total_vol = q1_vol + q2_vol + q3_vol + q4_vol
    if total_vol == 0:
        return {"status": "Zero total volume"}

    q1 = round((q1_vol / total_vol) * 100, 2)
    q2 = round((q2_vol / total_vol) * 100, 2)
    q3 = round((q3_vol / total_vol) * 100, 2)
    q4 = round((q4_vol / total_vol) * 100, 2)

    buyer_side = q1 + q2
    seller_side = q3 + q4
    rvi = round((buyer_side - seller_side) / 100, 3)

    if rvi > 0.05:
        bias = "Bullish Reflective Expansion"
        key_zone = high - range_half * 0.25
        liquidity_pool = low + range_half * 0.15
    elif rvi < -0.05:
        bias = "Bearish Reflective Expansion"
        key_zone = low + range_half * 0.25
        liquidity_pool = high - range_half * 0.15
    else:
        bias = "Neutral Reflective Equilibrium"
        key_zone = midpoint
        liquidity_pool = midpoint

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "high": round(high, 5),
        "low": round(low, 5),
        "vwap": round(vwap, 5),
        "quadrants": {"Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4},
        "rvi": rvi,
        "bias": bias,
        "key_support_demand": round(key_zone, 5),
        "liquidity_pool": round(liquidity_pool, 5),
        "note": "Reflective Volume Quadrant Engine v6.0r++",
    }

    _log(result)
    return result


def _log(data: dict) -> None:
    """Simpan hasil ke log reflektif Vault."""
    with open(LOG_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(data) + "\n")


__all__ = ["reflective_volume_quadrant_engine"]
