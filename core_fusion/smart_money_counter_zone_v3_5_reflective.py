from __future__ import annotations

"""Smart Money Counter-Zone v3.5 reflective detector."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping


@dataclass
class CounterZoneContext:
    price: float
    vwap: float
    atr: float
    rsi: float
    mfi: float
    cci50: float
    rsi_h4: float
    trq_energy: float
    reflective_intensity: float
    alpha: float
    beta: float
    gamma: float
    integrity_index: float
    journal_path: Path | None = None


def _clamp(value: float, *, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _compute_confidence(ctx: CounterZoneContext) -> float:
    energy_score = _clamp(ctx.trq_energy / 2.5)
    reflective_score = _clamp((ctx.reflective_intensity + ctx.integrity_index) / 2)
    gradient_score = _clamp((ctx.alpha + ctx.beta + ctx.gamma) / 3)
    momentum_score = _clamp(
        (
            abs(ctx.rsi - 50.0) / 50.0
            + abs(ctx.mfi - 50.0) / 50.0
            + min(abs(ctx.cci50) / 200.0, 1.0)
            + abs(ctx.rsi_h4 - 50.0) / 50.0
        )
        / 4
    )

    confidence = 0.35
    confidence += 0.25 * energy_score
    confidence += 0.2 * reflective_score
    confidence += 0.1 * gradient_score
    confidence += 0.1 * momentum_score

    return round(_clamp(confidence, high=0.995), 3)


def _derive_direction(ctx: CounterZoneContext) -> str:
    if ctx.price > ctx.vwap and ctx.rsi >= 60.0:
        return "SELL"
    if ctx.price < ctx.vwap and ctx.rsi <= 40.0:
        return "BUY"
    if ctx.mfi <= 45.0 and ctx.price <= ctx.vwap:
        return "BUY"
    if ctx.rsi_h4 >= 65.0:
        return "SELL"
    return "BUY" if ctx.price <= ctx.vwap else "SELL"


def smart_money_counter_v3_5_reflective(
    *,
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💎 Smart Money Counter-Zone v3.5 (Reflective Adaptive Mode)
------------------------------------------------------------
Integrasi penuh dengan TUYUL FX ULTIMATE HYBRID AGI v5.8r++ Quad Vault System.
Mendeteksi zona pembalikan berdasarkan:
    • Deviasi VWAP
    • Spread MFI–CCI50
    • RSI ekstrem multi-timeframe (RSI + RSI_H4)
    • Energi Reflektif TRQ-3D (α β γ + intensity)

Output dikalibrasi ke Journal Vault melalui Reflective Bridge Manager.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path


def smart_money_counter_v3_5_reflective(
    price: float,
    vwap: float,
    atr: float,
    rsi: float,
    mfi: float,
    cci50: float,
    rsi_h4: float,
    trq_energy: float,
    reflective_intensity: float,
    alpha: float,
    beta: float,
    gamma: float,
    integrity_index: float,
    journal_path: Path | None = None,
) -> Dict[str, float | str | Mapping[str, float]]:
    """Detect reflective counter-zones using VWAP, TRQ–3D, and αβγ gradients."""

    ctx = CounterZoneContext(
        price=price,
        vwap=vwap,
        atr=atr,
        rsi=rsi,
        mfi=mfi,
        cci50=cci50,
        rsi_h4=rsi_h4,
        trq_energy=trq_energy,
        reflective_intensity=reflective_intensity,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        integrity_index=integrity_index,
        journal_path=journal_path,
    )

    direction = _derive_direction(ctx)
    risk_buffer = max(ctx.atr * 1.6, 0.0008)
    target_buffer = max(ctx.atr * 1.8, 0.0012)

    if direction == "BUY":
        entry = round(ctx.price - ctx.atr * 0.1, 5)
        sl = round(entry - risk_buffer, 5)
        tp = round(entry + target_buffer, 5)
    else:
        entry = round(ctx.price + ctx.atr * 0.1, 5)
        sl = round(entry + risk_buffer, 5)
        tp = round(entry - target_buffer, 5)

    return {
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "type": direction,
        "confidence": _compute_confidence(ctx),
        "note": "Smart Money VWAP Counter-Zone v3.5 (Reflective Adaptive Mode)",
        "meta": {
            "trq_energy": round(ctx.trq_energy, 6),
            "reflective_intensity": round(ctx.reflective_intensity, 6),
            "alpha": round(ctx.alpha, 6),
            "beta": round(ctx.beta, 6),
            "gamma": round(ctx.gamma, 6),
            "integrity_index": round(ctx.integrity_index, 6),
        },
    }
    trq_energy: float = 1.0,
    reflective_intensity: float = 1.0,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
    integrity_index: float = 0.97,
    journal_path: Path | str = "data/logs/reflective_trade_precision_log.json",
) -> dict[str, object]:
    """Deteksi zona pembalikan reflektif adaptif berbasis energi TRQ-3D & VWAP."""
    if atr <= 0:
        return {"status": "ATR invalid for Smart Money Counter-Zone"}

    vwap_dev = abs(price - vwap)
    spread = abs(mfi - cci50)
    vwap_thr = 1.2 * atr
    spread_thr = 55
    rsi_extreme = (rsi >= 80 and price > vwap) or (rsi <= 20 and price < vwap)
    rsi_h4_support = (rsi_h4 >= 65 and price > vwap) or (rsi_h4 <= 35 and price < vwap)

    if vwap_dev >= vwap_thr and spread >= spread_thr and rsi_extreme and rsi_h4_support:
        side = "SELL" if price > vwap else "BUY"
        sl = price + vwap_dev if side == "SELL" else price - vwap_dev
        tp = vwap

        base_conf = max(0.0, 1.0 - (vwap_dev / (2 * atr)))
        trq_boost = (trq_energy * reflective_intensity) / 2
        meta_factor = (alpha + beta + gamma) / 3
        integrity_boost = integrity_index - 0.9
        confidence = min(
            1.0,
            base_conf * 0.7 + trq_boost * 0.2 + meta_factor * 0.05 + integrity_boost * 0.05,
        )

        result = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "entry": round(price, 5),
            "sl": round(sl, 5),
            "tp": round(tp, 5),
            "type": side,
            "spread": round(spread, 2),
            "deviation": round(vwap_dev, 5),
            "confidence": round(confidence, 3),
            "trq_energy": round(trq_energy, 3),
            "reflective_intensity": round(reflective_intensity, 3),
            "alpha": round(alpha, 3),
            "beta": round(beta, 3),
            "gamma": round(gamma, 3),
            "integrity_index": round(integrity_index, 3),
            "note": "Smart Money VWAP Counter-Zone v3.5 (Reflective Adaptive Mode)",
        }

        _log_to_journal(result, journal_path)
        return result

    return {"status": "No valid counter-zone"}


def _log_to_journal(data: dict, path: Path | str):
    """Menyimpan output ke Journal Vault log reflektif."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write(json.dumps(data) + "\n")


__all__ = ["smart_money_counter_v3_5_reflective"]
