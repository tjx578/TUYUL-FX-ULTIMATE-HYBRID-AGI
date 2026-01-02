from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core_cognitive.risk_manager import (  # noqa: E402
    RiskFeedbackCalibrator,
    VaultRiskSync,
    calculate_risk,
    calibrate_risk,
)


def test_calibrate_risk_tiers() -> None:
    assert calibrate_risk(drawdown=0.0) == 1.0
    assert calibrate_risk(drawdown=0.08) == 0.75
    assert calibrate_risk(drawdown=0.12) == 0.5
    assert calibrate_risk(drawdown=0.2) == 0.0
    with pytest.raises(ValueError):
        calibrate_risk(drawdown=-0.01)


def test_calculate_risk_basic() -> None:
    assessment = calculate_risk(
        balance=10_000,
        confidence=0.8,
        reflex_coherence=0.8,
        drawdown=0.05,
        entry_price=1.25,
        stop_loss=1.245,
    )

    assert assessment.balance == 10_000
    assert assessment.adjusted_risk > 0
    assert assessment.lot_size >= 0


def test_calculate_risk_with_calibration_and_persist(tmp_path) -> None:
    calibrator = RiskFeedbackCalibrator(vault_path=tmp_path)
    calibration_source = tmp_path / "log.json"
    calibration_source.write_text(
        json.dumps({"confidence": 0.9, "drawdown": 0.02}), encoding="utf-8"
    )

    sync = VaultRiskSync(vault_path=tmp_path / "logs")
    assessment = calculate_risk(
        balance=5_000,
        confidence=0.9,
        drawdown=0.02,
        pair="EUR/USD",
        entry_price=1.1,
        stop_loss=1.095,
        calibrate=True,
        calibrator=calibrator,
        vault_sync=sync,
        persist=True,
    )

    assert assessment.calibration_path is not None
    assert assessment.vault_log_path is not None
    assert (tmp_path / "risk_feedback_calibration.json").exists()
