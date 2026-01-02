from __future__ import annotations

import json
import importlib.util
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from types import ModuleType
from typing import Final, Literal

ModeLiteral = Literal["normal", "reflexive", "aggressive"]

_BASE_RISK_PERCENT: Final[float] = 1.0
_MAX_RISK_FRACTION: Final[float] = 0.018
_MODULE_DIR = Path(__file__).resolve().parent / "modules"


def _load_module(module_name: str, module_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_adaptive_module = _load_module(
    "core_cognitive.modules.adaptive_risk_calculator",
    _MODULE_DIR / "adaptive_risk_calculator.py",
)
calculate_dynamic_risk = _adaptive_module.calculate_dynamic_risk  # type: ignore[attr-defined]
calculate_lot_size = _adaptive_module.calculate_lot_size  # type: ignore[attr-defined]

_feedback_module = _load_module(
    "core_cognitive.modules.risk_feedback_calibrator",
    _MODULE_DIR / "risk_feedback_calibrator.py",
)
CalibrationSummary = _feedback_module.CalibrationSummary  # type: ignore[attr-defined]
RiskFeedbackCalibrator = _feedback_module.RiskFeedbackCalibrator  # type: ignore[attr-defined]

_vault_module = _load_module(
    "core_cognitive.modules.vault_risk_sync", _MODULE_DIR / "vault_risk_sync.py"
)
VaultRiskSync = _vault_module.VaultRiskSync  # type: ignore[attr-defined]

__all__ = ["RiskAssessment", "calibrate_risk", "calculate_risk", "run_calibration"]


@dataclass(slots=True)
class RiskAssessment:
    """Detailed adaptive risk profile for a trade or simulation."""

    balance: float
    drawdown: float
    reflex_coherence: float
    base_risk: float
    adjusted_risk: float
    risk_fraction: float
    risk_amount: float
    lot_size: float
    mode: ModeLiteral
    confidence: float
    dynamic_risk: float
    alignment_score: int | None = None
    calibration: CalibrationSummary | dict[str, float | int | str] | None = None
    calibration_path: str | None = None
    vault_log_path: str | None = None


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def _normalise_mode(
    mode: str | None, drawdown: float, confidence: float
) -> ModeLiteral:
    if mode:
        lowered = mode.lower()
        if lowered in {"normal", "reflexive", "aggressive"}:
            return lowered  # type: ignore[return-value]
    if drawdown >= 0.12:
        return "reflexive"
    if confidence >= 0.93 and drawdown <= 0.05:
        return "aggressive"
    return "normal"


def calibrate_risk(*, drawdown: float) -> float:
    """Return the drawdown tier multiplier used by the adaptive risk engine."""

    if drawdown < 0:
        raise ValueError("Drawdown cannot be negative")

    if drawdown <= 0.05:
        return 1.0
    if drawdown <= 0.10:
        return 0.75
    if drawdown <= 0.15:
        return 0.5
    return 0.0


def _hydrate_confidence_weight(calibrator: RiskFeedbackCalibrator) -> None:
    calibration_file = calibrator.vault_path / "risk_feedback_calibration.json"
    if not calibration_file.exists():
        return
    try:
        payload = json.loads(calibration_file.read_text(encoding="utf-8"))
        calibrator.confidence_weight = float(payload.get("new_confidence_weight", 1.0))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return


def _resolve_alignment_factor(score: int | None) -> float:
    if score is None:
        return 0.5
    if score <= 0:
        return 0.0
    return _clamp(score / 4.0, 0.0, 1.0)


def _resolve_pip_value(pair: str | None, pip_value: float | None) -> float:
    if pip_value is not None:
        return pip_value
    if pair and "JPY" in pair.upper():
        return 9.1
    return 10.0


def calculate_risk(
    balance: float,
    *,
    drawdown: float = 0.0,
    reflex_coherence: float | None = None,
    confidence: float | None = None,
    mode: str | None = None,
    pair: str | None = None,
    entry_price: float | None = None,
    stop_loss: float | None = None,
    pip_value: float | None = None,
    vault_sync: VaultRiskSync | None = None,
    calibrator: RiskFeedbackCalibrator | None = None,
    vault_history: int = 10,
    persist: bool = False,
    calibrate: bool | None = None,
    calibration_limit: int = 10,
    alignment_score: int | None = None,
) -> RiskAssessment:
    """Calculate the adaptive risk exposure for a trade context."""

    if balance <= 0:
        raise ValueError("Balance must be positive")

    if reflex_coherence is None and confidence is None:
        raise ValueError("Either reflex_coherence or confidence must be provided")

    drawdown_fraction = drawdown / 100 if drawdown > 1 else drawdown
    if drawdown_fraction < 0:
        raise ValueError("Drawdown cannot be negative")

    reflex_value = (
        reflex_coherence if reflex_coherence is not None else confidence or 0.0
    )
    reflex_value = _clamp(reflex_value, 0.0, 1.0)
    confidence_value = confidence if confidence is not None else reflex_value
    confidence_value = _clamp(confidence_value, 0.0, 1.0)

    mode_literal = _normalise_mode(mode, drawdown_fraction, confidence_value)
    dynamic_fraction = calculate_dynamic_risk(confidence_value, mode_literal)
    drawdown_multiplier = calibrate_risk(drawdown=drawdown_fraction)
    alignment_factor = _resolve_alignment_factor(alignment_score)

    calibrate_flag = persist if calibrate is None else calibrate
    calibration_summary: CalibrationSummary | dict[str, float | int | str] | None = None
    calibration_path: str | None = None
    confidence_weight = 1.0

    sync: VaultRiskSync | None = None
    if persist or calibrate_flag:
        sync = vault_sync or VaultRiskSync()

    effective_calibrator = calibrator
    if calibrate_flag:
        effective_calibrator = effective_calibrator or RiskFeedbackCalibrator(
            vault_path=(sync.vault_path if sync else Path("data/vault/risk_logs"))
        )
        if calibration_limit > 0:
            _hydrate_confidence_weight(effective_calibrator)
            calibration_summary = effective_calibrator.calibrate(
                effective_calibrator.load_risk_data(limit=calibration_limit)
            )
            if isinstance(calibration_summary, CalibrationSummary):
                confidence_weight = calibration_summary.new_confidence_weight
                saved_path = effective_calibrator.save_calibration()
                if saved_path is not None:
                    calibration_path = str(saved_path)
            else:
                effective_calibrator.save_calibration()

    adjusted_fraction = (
        dynamic_fraction * drawdown_multiplier * confidence_weight * alignment_factor
    )
    adjusted_fraction = _clamp(adjusted_fraction, 0.0, _MAX_RISK_FRACTION)

    adjusted_percent = round(adjusted_fraction * 100, 2)
    dynamic_percent = round(dynamic_fraction * 100, 2)
    risk_amount = round(balance * adjusted_fraction, 2)

    resolved_pip_value = _resolve_pip_value(pair, pip_value)
    lot_size = 0.0
    if entry_price is not None and stop_loss is not None:
        lot_size = calculate_lot_size(
            balance, entry_price, stop_loss, resolved_pip_value, adjusted_fraction
        )

    assessment = RiskAssessment(
        balance=round(balance, 2),
        drawdown=round(drawdown_fraction, 4),
        reflex_coherence=round(reflex_value, 4),
        base_risk=_BASE_RISK_PERCENT,
        adjusted_risk=adjusted_percent,
        risk_fraction=round(adjusted_fraction, 4),
        risk_amount=risk_amount,
        lot_size=lot_size,
        mode=mode_literal,
        confidence=round(confidence_value, 4),
        dynamic_risk=dynamic_percent,
        alignment_score=alignment_score,
        calibration=calibration_summary,
        calibration_path=calibration_path,
    )

    if persist:
        if pair is None:
            raise ValueError("Pair symbol must be provided when persist=True")
        sync = sync or VaultRiskSync()
        payload: dict[str, float | int | str | None] = {
            "balance": assessment.balance,
            "drawdown": assessment.drawdown,
            "reflex_coherence": assessment.reflex_coherence,
            "confidence": assessment.confidence,
            "mode": assessment.mode,
            "base_risk": assessment.base_risk,
            "dynamic_risk": assessment.dynamic_risk,
            "adjusted_risk": assessment.adjusted_risk,
            "risk_fraction": assessment.risk_fraction,
            "risk_amount": assessment.risk_amount,
            "lot_size": assessment.lot_size,
        }
        if alignment_score is not None:
            payload["alignment_score"] = alignment_score
        if calibration_summary is not None:
            if isinstance(calibration_summary, CalibrationSummary):
                payload["calibration"] = calibration_summary.as_dict()
            else:
                payload["calibration"] = calibration_summary
        if calibration_path is not None:
            payload["calibration_path"] = calibration_path
        vault_log_path = sync.save(pair, payload)
        assessment = replace(assessment, vault_log_path=vault_log_path)

    return assessment


def run_calibration(
    profile: str,
    *,
    vault_path: str | Path = "data/vault/risk_logs/",
    limit: int = 10,
) -> dict[str, float | int | str]:
    """Execute a feedback calibration cycle for the supplied profile."""

    calibrator = RiskFeedbackCalibrator(vault_path=vault_path)
    _hydrate_confidence_weight(calibrator)
    summary = calibrator.calibrate(calibrator.load_risk_data(limit=limit))
    calibrator.save_calibration()

    payload: dict[str, float | int | str] = {"profile": profile}
    if isinstance(summary, CalibrationSummary):
        payload.update(summary.as_dict())
    elif isinstance(summary, dict):
        payload.update(summary)
    else:
        payload["status"] = "unknown"
    return payload
