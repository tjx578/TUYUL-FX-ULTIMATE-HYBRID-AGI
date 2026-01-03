#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚖️ Equilibrium Momentum Fusion v6 (Reflective Adaptive Mode)
------------------------------------------------------------
TUYUL FX ULTIMATE HYBRID AGI v5.8r++ | Quad Vault Reflective Discipline Mode

Fungsi:
  • Mengukur keseimbangan momentum (bullish vs bearish)
  • Mengintegrasikan energi TRQ–3D dan αβγ field
  • Memberikan sinyal bias reflektif dengan confidence adaptif
  • Merekam hasil ke Journal Vault (fusion_equilibrium_log.json)
"""

from __future__ import annotations

import datetime
import json
import math
from pathlib import Path
from typing import Any, Dict, Mapping

LOG_PATH = Path("data/logs/fusion_equilibrium_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def equilibrium_momentum_fusion_v6(
    price_change: float,
    volume_change: float,
    time_weight: float,
    atr: float,
    trq_energy: float = 1.0,
    reflective_intensity: float = 1.0,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
    integrity_index: float = 0.97,
    direction_hint: float = 1.0,
) -> Dict[str, Any]:
    """
    Menghitung keseimbangan momentum reflektif antar dimensi (Price × Volume × Time).
    """

    if atr <= 0 or any(v is None for v in [price_change, volume_change, time_weight]):
        return {"status": "invalid input"}

    price_momentum = abs(price_change / atr)
    volume_factor = math.log1p(abs(volume_change))
    time_factor = math.log1p(abs(time_weight))

    equilibrium = (price_momentum + volume_factor + time_factor) / 3
    imbalance = abs(price_momentum - volume_factor) + abs(volume_factor - time_factor)

    trq_sync = trq_energy * reflective_intensity
    alpha_sync = (alpha + beta + gamma) / 3

    fusion_score = (equilibrium / (1 + imbalance)) * trq_sync * alpha_sync * integrity_index
    signed_score = fusion_score * math.copysign(1.0, direction_hint)

    if signed_score >= 1.25:
        bias = "Bullish Reflective Phase"
    elif signed_score <= -0.75:
        bias = "Bearish Reflective Phase"
    else:
        bias = "Neutral Reflective Phase"

    confidence = min(1.0, abs(signed_score) / 1.5)

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "price_momentum": round(price_momentum, 3),
        "volume_factor": round(volume_factor, 3),
        "time_factor": round(time_factor, 3),
        "equilibrium": round(equilibrium, 3),
        "imbalance": round(imbalance, 3),
        "fusion_score": round(fusion_score, 3),
        "fusion_score_signed": round(signed_score, 3),
        "reflective_confidence": round(confidence, 3),
        "bias": bias,
        "trq_energy": round(trq_energy, 3),
        "reflective_intensity": round(reflective_intensity, 3),
        "alpha": round(alpha, 3),
        "beta": round(beta, 3),
        "gamma": round(gamma, 3),
        "integrity_index": round(integrity_index, 3),
        "note": "Equilibrium Momentum Fusion v6 – Reflective Adaptive Mode",
    }

    _log_to_vault(result)
    return result


def equilibrium_momentum_fusion(
    vwap_val: float,
    ema_fusion_data: Mapping[str, Any],
    reflex_strength: float,
    trq_energy: float = 1.0,
    reflective_intensity: float = 1.0,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
    integrity_index: float = 0.97,
) -> Dict[str, Any]:
    """
    Adaptasi high-level equilibrium fusion untuk pipeline Ultra Fusion.

    Parameter:
        vwap_val: Nilai VWAP terkini.
        ema_fusion_data: Dict dengan kunci minimal:
            - ema50 (float): EMA50 anchor.
            - fusion_strength (float): Output layer precision.
            - cross_state (str): "bullish" / "bearish" / "neutral".
        reflex_strength: Koherensi refleks (positif / negatif).
    """

    ema50 = float(ema_fusion_data.get("ema50") or 0.0)
    fusion_strength = float(ema_fusion_data.get("fusion_strength") or 0.0)
    cross_state = str(ema_fusion_data.get("cross_state", "neutral")).lower()

    if vwap_val is None or not math.isfinite(vwap_val):
        return {"status": "invalid input"}

    price_change = vwap_val - ema50
    direction_hint = (
        1.0 if cross_state == "bullish" else -1.0 if cross_state == "bearish" else 0.0
    )
    direction_hint = direction_hint or math.copysign(1.0, price_change or 1.0)

    atr_proxy = _estimate_atr_proxy(vwap_val, ema50)

    fusion_output = equilibrium_momentum_fusion_v6(
        price_change=price_change,
        volume_change=fusion_strength,
        time_weight=reflex_strength,
        atr=atr_proxy,
        trq_energy=trq_energy,
        reflective_intensity=reflective_intensity,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        integrity_index=integrity_index,
        direction_hint=direction_hint,
    )

    if fusion_output.get("status") == "invalid input":
        return fusion_output

    signed_score = fusion_output["fusion_score_signed"]

    if signed_score >= 1.25:
        state = "BULLISH"
    elif signed_score <= -0.75:
        state = "BEARISH"
    else:
        state = "NEUTRAL"

    magnitude = abs(signed_score)
    if magnitude >= 1.75:
        momentum_band = "hyper"
    elif magnitude >= 1.25:
        momentum_band = "strong"
    elif magnitude >= 0.75:
        momentum_band = "balanced"
    else:
        momentum_band = "calm"

    enriched_output: Dict[str, Any] = {
        **fusion_output,
        "state": state,
        "equilibrium_state": state,
        "momentum_band": momentum_band,
        "vwap": round(vwap_val, 6),
        "ema50": round(ema50, 6),
        "fusion_strength_input": round(fusion_strength, 4),
        "reflex_strength": round(reflex_strength, 4),
        "cross_state": cross_state,
        "atr_proxy": round(atr_proxy, 6),
    }

    return enriched_output


def _estimate_atr_proxy(vwap_val: float, ema50: float) -> float:
    """
    Estimasi konservatif ATR jika tidak disediakan eksplisit pada layer ini.

    Menggunakan kombinasi deviasi VWAP-EMA50 dan skala dasar harga untuk
    menghindari nilai nol/negatif.
    """

    base_scale = max(abs(vwap_val), abs(ema50), 1e-6)
    deviation = abs(vwap_val - ema50)
    proxy = max(deviation * 1.25, base_scale * 0.0008, 1e-6)
    return proxy


def _log_to_vault(data: Dict[str, Any]) -> None:
    """Simpan hasil ke Journal Vault."""
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        json.dump(data, log_file)
        log_file.write("\n")


__all__ = ["equilibrium_momentum_fusion_v6", "equilibrium_momentum_fusion"]
