from __future__ import annotations

from typing import Dict

import pytest

from core_reflective import integrity_validator
from core_reflective import risk_feedback_calibrator


class DummyCalibrator(risk_feedback_calibrator.RiskFeedbackCalibrator):
    def __init__(self, vault_path: str, payload: Dict[str, float] | None = None) -> None:
        super().__init__(vault_path)
        self.payload = payload or {"error": 0.2}

    def load_risk_data(self, *, limit: int | None = None):  # type: ignore[override]
        return [self.payload, {"metrics": {"error": 0.1}}][: limit or None]

    def save_calibration(self) -> str | None:  # type: ignore[override]
        return "snapshot.json"


@pytest.fixture
def patched_calibrator(monkeypatch, tmp_path):
    def factory(vault_path: str) -> DummyCalibrator:
        return DummyCalibrator(str(tmp_path))

    monkeypatch.setattr(integrity_validator, "RiskFeedbackCalibrator", factory)


def test_system_integrity_check(patched_calibrator):
    result = integrity_validator.system_integrity_check()

    assert result["modules_verified"] is True
    assert result["core_integrity"] == "PASS"
    assert result["feedback_calibration"]["status"] == "READY"
    assert "mean_error" in result["feedback_calibration"]


def test_finalize_trade_cycle(patched_calibrator):
    result = integrity_validator.finalize_trade_cycle(vault_limit=2)

    assert result["calibration_snapshot"] == "snapshot.json"
    assert result["calibration"].status == "READY"
