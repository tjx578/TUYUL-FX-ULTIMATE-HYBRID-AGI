from __future__ import annotations

import datetime
import json
import statistics
from pathlib import Path
from typing import Dict, Iterable

TIMEFRAMES: tuple[str, str, str, str] = ("H1", "H4", "D1", "W1")

LOG_PATH = Path("data/logs/multi_timeframe_alignment_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def multi_timeframe_alignment_analyzer(
    biases: Dict[str, float],
    rsi_values: Dict[str, float],
    reflective_intensity: float = 1.0,
    trq_energy: float = 1.0,
    alpha: float = 1.0,
    beta: float = 1.0,
    gamma: float = 1.0,
    integrity_index: float = 0.97,
) -> Dict[str, object]:
    """
    Analisis keselarasan bias lintas timeframe reflektif.
    biases: dict { "H1": 1/-1, "H4": 1/-1, "D1": 1/-1, "W1": 1/-1 }
    rsi_values: dict { "H1": val, "H4": val, "D1": val, "W1": val }
    """

    validation_error = _validate_inputs(biases, rsi_values, TIMEFRAMES)
    if validation_error:
        return {"status": "Invalid timeframe data", "detail": validation_error}

    alignment_anchor = biases["H4"]
    aligned = [tf for tf in TIMEFRAMES if biases[tf] == alignment_anchor]
    alignment_ratio = len(aligned) / len(TIMEFRAMES)

    rsi_sample = [float(rsi_values[tf]) for tf in TIMEFRAMES]
    rsi_var = statistics.pstdev(rsi_sample)
    rsi_coherence = max(0.0, 1.0 - (rsi_var / 25))

    bias_strength = alignment_ratio * rsi_coherence * reflective_intensity * trq_energy
    meta_sync = (alpha + beta + gamma) / 3
    bias_strength *= meta_sync

    if bias_strength >= 0.85:
        regime_state = "Strong Alignment"
    elif 0.65 <= bias_strength < 0.85:
        regime_state = "Moderate Alignment"
    elif 0.45 <= bias_strength < 0.65:
        regime_state = "Weak Alignment"
    else:
        regime_state = "Disaligned"

    time_coherence_index = (bias_strength * integrity_index) / (1 + rsi_var / 50)

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "alignment_ratio": round(alignment_ratio, 3),
        "rsi_variance": round(rsi_var, 3),
        "rsi_coherence": round(rsi_coherence, 3),
        "bias_strength": round(bias_strength, 3),
        "meta_sync": round(meta_sync, 3),
        "reflective_intensity": round(reflective_intensity, 3),
        "trq_energy": round(trq_energy, 3),
        "integrity_index": round(integrity_index, 3),
        "time_coherence_index": round(time_coherence_index, 3),
        "regime_state": regime_state,
        "note": "MTF Alignment Analyzer v1.5 – Reflective Fusion Mode",
    }

    _log_to_file(result)
    return result


def _validate_inputs(
    biases: Dict[str, float], rsi_values: Dict[str, float], timeframes: Iterable[str]
) -> str | None:
    missing_biases = [tf for tf in timeframes if tf not in biases]
    missing_rsi = [tf for tf in timeframes if tf not in rsi_values]
    if missing_biases or missing_rsi:
        return f"Missing data for: {missing_biases + missing_rsi}"

    if not all(isinstance(biases[tf], (int, float)) for tf in timeframes):
        return "Bias values must be numeric."
    if not all(isinstance(rsi_values[tf], (int, float)) for tf in timeframes):
        return "RSI values must be numeric."

    return None


def _log_to_file(data: Dict[str, object]) -> None:
    with open(LOG_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(data) + "\n")


__all__ = ["multi_timeframe_alignment_analyzer"]
