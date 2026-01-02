from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class CalibrationSummary:
    new_confidence_weight: float
    sample_size: int
    status: str = "updated"

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "new_confidence_weight": self.new_confidence_weight,
            "sample_size": self.sample_size,
            "status": self.status,
        }


class RiskFeedbackCalibrator:
    """Calibrate confidence weighting based on stored vault risk data."""

    def __init__(self, *, vault_path: str | Path = "data/vault/risk_logs") -> None:
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.confidence_weight: float = 1.0

    def load_risk_data(self, *, limit: int = 10) -> list[dict[str, Any]]:
        files = sorted(
            self.vault_path.glob("*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        items: list[dict[str, Any]] = []
        for path in files[:limit]:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    items.append(payload)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
        return items

    def calibrate(
        self, risk_data: list[dict[str, Any]]
    ) -> CalibrationSummary | dict[str, Any]:
        if not risk_data:
            return {"status": "no_data"}

        confidences = [_safe_float(item.get("confidence"), 0.5) for item in risk_data]
        drawdowns = [_safe_float(item.get("drawdown"), 0.0) for item in risk_data]
        sample_size = len(confidences)

        average_confidence = sum(confidences) / sample_size
        average_drawdown = sum(abs(value) for value in drawdowns) / sample_size

        weight = 1.0 + (average_confidence - 0.5) * 0.5
        if average_drawdown > 0.10:
            weight *= 0.85
        weight = max(0.5, min(weight, 1.5))

        self.confidence_weight = weight
        return CalibrationSummary(
            new_confidence_weight=weight, sample_size=sample_size, status="updated"
        )

    def save_calibration(self) -> Path | None:
        calibration_path = self.vault_path / "risk_feedback_calibration.json"
        payload = {"new_confidence_weight": self.confidence_weight}
        try:
            calibration_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError:
            return None
        return calibration_path
