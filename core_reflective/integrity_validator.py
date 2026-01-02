"""System integrity validation helpers for reflective trading cycles."""

from __future__ import annotations

import os
import platform
from typing import Any, Dict

from core_reflective.risk_feedback_calibrator import (
    CalibrationSummary,
    RiskFeedbackCalibrator,
)

CORE_FILES = (
    os.path.join("core_cognitive", "twms_calculator.py"),
    os.path.join("core_cognitive", "reflex_emotion_core.py"),
    os.path.join("core_cognitive", "montecarlo_validator.py"),
)


def system_integrity_check() -> Dict[str, Any]:
    """Return integrity metadata for the Cognitive Trading Core."""

    files_ok = all(os.path.exists(path) for path in CORE_FILES)

    calibrator = RiskFeedbackCalibrator(vault_path="data/vault/risk_logs/")
    try:
        samples = calibrator.load_risk_data(limit=5)
        calibration = calibrator.calibrate(samples)
        if isinstance(calibration, CalibrationSummary):
            feedback_payload: Dict[str, Any] = {
                "status": "READY",
                **calibration.as_dict(),
            }
        elif isinstance(calibration, dict):
            status = calibration.get("status", "NO_DATA")
            feedback_payload = {"status": status, **calibration}
        else:
            feedback_payload = {"status": "NO_DATA"}
        calibrator.save_calibration()
    except Exception as exc:  # pragma: no cover - defensive guard
        feedback_payload = {"status": f"ERROR: {exc.__class__.__name__}"}

    return {
        "platform": platform.system(),
        "core_integrity": "PASS" if files_ok else "FAIL",
        "modules_verified": files_ok,
        "feedback_calibration": feedback_payload,
    }


def finalize_trade_cycle(*, vault_limit: int = 10) -> Dict[str, Any]:
    """Run post-trade calibration using the latest Vault risk insights."""

    integrity = system_integrity_check()
    calibrator = RiskFeedbackCalibrator(vault_path="data/vault/risk_logs/")
    recent_data = calibrator.load_risk_data(limit=vault_limit)
    calibration = calibrator.calibrate(recent_data)
    snapshot_path = calibrator.save_calibration()

    result = {**integrity, "calibration": calibration}
    if snapshot_path:
        result["calibration_snapshot"] = snapshot_path
    return result
