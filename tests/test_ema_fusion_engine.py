from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core_fusion.ema_fusion_engine import ema_fusion_engine  # noqa: E402


def test_ema_fusion_engine_returns_expected_slopes() -> None:
    output = ema_fusion_engine(
        ema_short=[1.1020, 1.1023, 1.1025, 1.1030, 1.1037],
        ema_mid=[1.1005, 1.1008, 1.1010, 1.1014, 1.1019],
        ema_long=[1.0980, 1.0982, 1.0984, 1.0987, 1.0990],
    )

    assert output["trend_strength"] == "FLAT / NO CLEAR TREND"
    assert output["ema_slope"] == pytest.approx(0.00124)
    assert output["slope_detail"]["ema_short"] == pytest.approx(0.00154)
    assert output["slope_detail"]["ema_mid"] == pytest.approx(0.00127)
    assert output["slope_detail"]["ema_long"] == pytest.approx(0.00091)


def test_classifies_strong_uptrend() -> None:
    output = ema_fusion_engine(
        ema_short=[1.0, 1.4, 1.8, 2.2, 2.8],
        ema_mid=[2.0, 2.6, 3.2, 3.8, 4.4],
        ema_long=[3.0, 3.5, 4.0, 4.5, 5.5],
    )

    assert output["trend_strength"] == "STRONG_UPTREND"
    assert output["ema_slope"] >= 0.6


def test_classifies_strong_downtrend() -> None:
    output = ema_fusion_engine(
        ema_short=[5.0, 4.0, 3.5, 3.0, 1.0],
        ema_mid=[6.0, 5.2, 4.4, 3.6, 2.0],
        ema_long=[7.0, 6.2, 5.4, 4.6, 3.0],
    )

    assert output["trend_strength"] == "STRONG_DOWNTREND"
    assert output["ema_slope"] <= -0.6


def test_raises_error_when_not_enough_points() -> None:
    with pytest.raises(ValueError):
        ema_fusion_engine(
            ema_short=[1.0, 1.1, 1.2, 1.3],
            ema_mid=[1.0, 1.1, 1.2, 1.3, 1.4],
            ema_long=[1.0, 1.1, 1.2, 1.3, 1.4],
        )


def test_handles_near_zero_baseline_without_division_by_zero() -> None:
    output = ema_fusion_engine(
        ema_short=[0.0, 0.0, 0.0, 0.0, 0.001],
        ema_mid=[0.0, 0.0, 0.0, 0.0, 0.002],
        ema_long=[0.0, 0.0, 0.0, 0.0, 0.003],
    )

    for slope in output["slope_detail"].values():
        assert math.isfinite(slope)
        assert slope > 0
