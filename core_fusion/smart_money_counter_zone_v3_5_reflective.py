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


__all__ = ["smart_money_counter_v3_5_reflective"]
