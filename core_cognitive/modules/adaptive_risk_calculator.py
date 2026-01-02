from __future__ import annotations

from typing import Literal

ModeLiteral = Literal["normal", "reflexive", "aggressive"]

_BASE_RISK_FRACTION = 0.01
_MODE_MULTIPLIERS: dict[ModeLiteral, float] = {
    "normal": 1.0,
    "reflexive": 0.9,
    "aggressive": 1.2,
}


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def calculate_dynamic_risk(confidence: float, mode: ModeLiteral) -> float:
    """Return the dynamic risk fraction based on confidence and operating mode."""

    confidence_value = _clamp(confidence, 0.0, 1.0)
    mode_multiplier = _MODE_MULTIPLIERS.get(mode, 1.0)
    baseline = _BASE_RISK_FRACTION * (0.85 + 0.75 * confidence_value)
    adaptive_risk = baseline * mode_multiplier
    return _clamp(adaptive_risk, 0.0, 0.025)


def calculate_lot_size(
    balance: float,
    entry_price: float,
    stop_loss: float,
    pip_value: float,
    risk_fraction: float,
) -> float:
    """Calculate lot size based on risk fraction and price distance."""

    if balance <= 0 or pip_value <= 0:
        raise ValueError("Balance and pip value must be positive")
    if entry_price <= 0 or stop_loss <= 0:
        raise ValueError("Entry and stop loss must be positive")

    price_distance = abs(entry_price - stop_loss)
    if price_distance == 0:
        return 0.0

    pip_distance = price_distance * 10000
    risk_amount = balance * _clamp(risk_fraction, 0.0, 1.0)
    per_lot_risk = pip_distance * pip_value
    if per_lot_risk == 0:
        return 0.0

    lot_size = risk_amount / per_lot_risk
    return round(lot_size, 2)
