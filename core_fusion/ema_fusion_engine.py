from __future__ import annotations

from typing import Final, Literal, Mapping, Sequence

TrendStrength = Literal[
    "STRONG_UPTREND",
    "STRONG_DOWNTREND",
    "MODERATE_UPTREND",
    "MODERATE_DOWNTREND",
    "FLAT / NO CLEAR TREND",
]

__all__ = ["ema_fusion_engine"]

_SLOPE_PRECISION: Final = 5
_SLOPE_WINDOW: Final = 5
_SLOPE_EPSILON: Final = 1e-6


def _validate_length(data: Sequence[float]) -> None:
    if len(data) < _SLOPE_WINDOW:
        raise ValueError("EMA data must contain at least 5 points to calculate slope.")


def _slope(data: Sequence[float]) -> float:
    _validate_length(data)
    baseline = float(data[-_SLOPE_WINDOW])
    latest = float(data[-1])
    baseline_magnitude = max(abs(baseline), _SLOPE_EPSILON)
    delta = (latest - baseline) / baseline_magnitude
    return round(delta, _SLOPE_PRECISION)


def _classify_trend(avg_slope: float) -> TrendStrength:
    if avg_slope >= 0.6:
        return "STRONG_UPTREND"
    if avg_slope <= -0.6:
        return "STRONG_DOWNTREND"
    if 0.2 <= avg_slope < 0.6:
        return "MODERATE_UPTREND"
    if -0.6 < avg_slope <= -0.2:
        return "MODERATE_DOWNTREND"
    return "FLAT / NO CLEAR TREND"


def ema_fusion_engine(
    ema_short: Sequence[float],
    ema_mid: Sequence[float],
    ema_long: Sequence[float],
) -> dict[str, float | TrendStrength | Mapping[str, float]]:
    """
    Calculate multi-timeframe EMA slope alignment and classify the prevailing trend.

    Args:
        ema_short: EMA values for the short timeframe (for example, EMA20).
        ema_mid: EMA values for the mid timeframe (for example, EMA50).
        ema_long: EMA values for the long timeframe (for example, EMA100).

    Returns:
        A dictionary containing the averaged slope, trend strength label, and slope details.
    """

    short_slope = _slope(ema_short)
    mid_slope = _slope(ema_mid)
    long_slope = _slope(ema_long)

    avg_slope = (short_slope + mid_slope + long_slope) / 3
    trend_strength = _classify_trend(avg_slope)

    return {
        "ema_slope": round(avg_slope, _SLOPE_PRECISION),
        "trend_strength": trend_strength,
        "slope_detail": {
            "ema_short": short_slope,
            "ema_mid": mid_slope,
            "ema_long": long_slope,
        },
    }


if __name__ == "__main__":
    example = ema_fusion_engine(
        ema_short=[1.1020, 1.1023, 1.1025, 1.1030, 1.1037],
        ema_mid=[1.1005, 1.1008, 1.1010, 1.1014, 1.1019],
        ema_long=[1.0980, 1.0982, 1.0984, 1.0987, 1.0990],
    )
    print("EMA Fusion Engine v5.3.3 (Test Mode)")
    for key, value in example.items():
        print(f"{key:15s}: {value}")
