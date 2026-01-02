"""Risk feedback calibration utilities for reflective trading cycles."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Sequence


@dataclass
class CalibrationSummary:
    """Structured summary of risk calibration metrics."""

    status: str
    total_samples: int
    mean_error: float
    calibration_score: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "total_samples": self.total_samples,
            "mean_error": self.mean_error,
            "calibration_score": self.calibration_score,
        }


class RiskFeedbackCalibrator:
    """Load risk signals from the vault and derive calibration metrics."""

    def __init__(self, vault_path: str) -> None:
        self.vault_path = vault_path
        self.last_calibration: CalibrationSummary | Dict[str, Any] | None = None
        self._ensure_vault_dir()

    def _ensure_vault_dir(self) -> None:
        os.makedirs(self.vault_path, exist_ok=True)

    def load_risk_data(self, *, limit: int | None = None) -> List[Dict[str, Any]]:
        """Load recent risk entries from the vault directory."""

        if not os.path.exists(self.vault_path):
            return []

        candidates = [
            os.path.join(self.vault_path, name)
            for name in os.listdir(self.vault_path)
            if name.endswith(".json")
        ]
        candidates.sort(reverse=True)
        if limit is not None:
            candidates = candidates[:limit]

        entries: List[Dict[str, Any]] = []
        for path in candidates:
            try:
                with open(path, "r", encoding="utf-8") as file:
                    payload = json.load(file)
            except (OSError, json.JSONDecodeError):
                continue

            if isinstance(payload, list):
                entries.extend([row for row in payload if isinstance(row, dict)])
            elif isinstance(payload, dict):
                entries.append(payload)

        return entries

    def calibrate(
        self, samples: Sequence[Dict[str, Any]]
    ) -> CalibrationSummary | Dict[str, Any]:
        """Compute calibration metrics from provided samples."""

        if not samples:
            self.last_calibration = {"status": "NO_DATA"}
            return self.last_calibration

        errors = self._collect_metric(samples, "error")
        drift = self._collect_metric(samples, "drift")
        baselines = errors or drift

        mean_error = float(sum(baselines) / len(baselines)) if baselines else 0.0
        calibration_score = max(0.0, min(1.0, 1.0 - min(mean_error, 1.0)))

        summary = CalibrationSummary(
            status="READY",
            total_samples=len(samples),
            mean_error=round(mean_error, 6),
            calibration_score=round(calibration_score, 6),
        )
        self.last_calibration = summary
        return summary

    def save_calibration(self) -> str | None:
        """Persist the last calibration snapshot to the vault directory."""

        if self.last_calibration is None:
            return None

        snapshot = (
            self.last_calibration.as_dict()
            if isinstance(self.last_calibration, CalibrationSummary)
            else dict(self.last_calibration)
        )

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"calibration_{timestamp}.json"
        path = os.path.join(self.vault_path, filename)

        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(snapshot, file, indent=2)
        except OSError:
            return None

        return path

    @staticmethod
    def _collect_metric(
        samples: Sequence[Dict[str, Any]],
        key: str,
    ) -> List[float]:
        collected: List[float] = []
        for sample in samples:
            value = sample.get(key)
            number = RiskFeedbackCalibrator._ensure_number(value)

            if number is None:
                nested = sample.get("metrics") if isinstance(sample, dict) else None
                if isinstance(nested, dict):
                    number = RiskFeedbackCalibrator._ensure_number(nested.get(key))

            if number is not None:
                collected.append(number)

        return collected

    @staticmethod
    def _ensure_number(value: Any) -> float | None:
        if isinstance(value, (int, float)):
            return float(value)
        return None
