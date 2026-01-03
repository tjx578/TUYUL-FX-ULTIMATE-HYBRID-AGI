#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📉 CCI–MFI Divergence Detector v6 (Reflective Production Mode)
--------------------------------------------------------------
TUYUL FX ULTIMATE HYBRID AGI v5.8r++ | Quad Vault Reflective Discipline

Fungsi:
  • Deteksi divergence antara Commodity Channel Index (CCI) dan Money Flow Index (MFI)
  • Mengukur deviasi reflektif antar momentum harga dan volume
  • Memberikan sinyal potensi reversal atau continuation reflektif
  • Menulis hasil ke Journal Vault (divergence_log.json)
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

LOG_PATH = Path("data/logs/divergence_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def cci_mfi_divergence_detector_v6(
    cci_values: list[float],
    mfi_values: list[float],
    reflective_intensity: float = 1.0,
    trq_energy: float = 1.0,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
    integrity_index: float = 0.97,
) -> dict[str, object]:
    """
    Menganalisis divergence reflektif antar indikator CCI dan MFI.
    Mengembalikan sinyal BUY/SELL reflektif bila terjadi mismatch signifikan.
    """

    # Validasi input
    if len(cci_values) < 2 or len(mfi_values) < 2:
        return {"status": "Not enough data"}

    if len(cci_values) != len(mfi_values):
        return {"status": "Length mismatch"}

    # 1️⃣ Hitung perubahan (delta) untuk mendeteksi arah
    cci_delta = cci_values[-1] - cci_values[-2]
    mfi_delta = mfi_values[-1] - mfi_values[-2]

    # 2️⃣ Deteksi divergence arah
    divergence_detected = (cci_delta > 0 and mfi_delta < 0) or (cci_delta < 0 and mfi_delta > 0)

    # 3️⃣ Hitung magnitude divergence
    divergence_strength = abs(cci_delta - mfi_delta)
    reflective_factor = reflective_intensity * trq_energy * ((alpha + beta + gamma) / 3)

    reflective_score = (divergence_strength / 100.0) * reflective_factor * integrity_index

    # 4️⃣ Klasifikasi hasil divergence
    if divergence_detected and reflective_score >= 0.7:
        if cci_delta > 0:
            signal = "Bullish Divergence"
        else:
            signal = "Bearish Divergence"
    else:
        signal = "No Divergence"

    # 5️⃣ Confidence reflektif
    confidence = min(1.0, reflective_score)

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "cci_delta": round(cci_delta, 3),
        "mfi_delta": round(mfi_delta, 3),
        "divergence_strength": round(divergence_strength, 3),
        "reflective_score": round(reflective_score, 3),
        "signal": signal,
        "confidence": round(confidence, 3),
        "reflective_intensity": round(reflective_intensity, 3),
        "trq_energy": round(trq_energy, 3),
        "alpha": round(alpha, 3),
        "beta": round(beta, 3),
        "gamma": round(gamma, 3),
        "integrity_index": round(integrity_index, 3),
        "note": "CCI–MFI Divergence Detector v6 – Reflective Production Mode",
    }

    _log_to_vault(result)
    return result


def _log_to_vault(data: dict) -> None:
    """Simpan hasil ke Journal Vault"""
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(data) + "\n")


__all__ = ["cci_mfi_divergence_detector_v6"]
