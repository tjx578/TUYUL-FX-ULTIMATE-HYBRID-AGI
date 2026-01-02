"""Prototype AGI engine orchestrator for TUYUL FX ULTRA WOLF v5.3.3.

This module wires together the adaptive risk intelligence loop components used
in TUYUL FX ULTRA WOLF v5.3.3. The real system feeds a ``vault_sync`` object
that persists risk snapshots into ``data/vault/risk_logs``. After persisting the
latest session we immediately recalibrate the confidence weighting by analysing
recent Vault history through :class:`RiskFeedbackCalibrator`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from math import isnan
from pathlib import Path
from time import monotonic
from typing import Any, Dict, Iterable, List, Literal, Mapping, Protocol, Sequence

DEFAULT_ACCOUNT_BALANCE = 100_000.0


class PatchRegistry:
    """Minimal patch registry used for telemetry."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def register_patch(
        self, module: str, version: str, status: str, description: str
    ) -> None:
        self._entries.append(
            {
                "module": module,
                "version": version,
                "status": status,
                "description": description,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @property
    def entries(self) -> list[dict[str, Any]]:
        return list(self._entries)


@dataclass(slots=True)
class TimeframeSignal:
    timeframe: str
    bias: str | None = None
    confidence: float | None = None
    confluence: float | None = None
    weight: float | None = None
    trend: Any | None = None
    ema_bias: Any | None = None
    divergence: Any | None = None
    wlwci: Any | None = None
    reflex_coherence: Any | None = None


class FundamentalContextIntegrator:
    MODULE_NAME = "FUNDAMENTAL_CONTEXT"
    MODULE_VERSION = "v1"
    STATUS = "active"

    def fetch_context(self, pair: str) -> dict[str, Any]:
        return {
            "pair": pair,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": "Macro context placeholder.",
        }


class MultiTimeframeIntegrator:
    MODULE_NAME = "MULTI_TIMEFRAME_INTEGRATOR"
    MODULE_VERSION = "v1"
    STATUS = "ACTIVE"

    def compute_alignment_score(
        self, signals: Sequence[TimeframeSignal], base_confidence: float | None = None
    ) -> dict[str, Any]:
        if not signals:
            raise ValueError("No signals provided")
        confidences = [
            signal.confidence
            for signal in signals
            if signal.confidence is not None and not isnan(signal.confidence)
        ]
        base = base_confidence if base_confidence is not None else 1.0
        avg_conf = sum(confidences) / len(confidences) if confidences else base
        alignment = sum(confidences) / len(confidences) if confidences else 0.0
        risk_modifier = max(0.7, min(1.5, avg_conf))
        return {
            "alignment_score": alignment,
            "final_confluence": alignment,
            "direction": signals[0].bias,
            "confidence": avg_conf,
            "risk_modifier": risk_modifier,
            "signals": [signal.__dict__ for signal in signals],
        }

    def integrate(
        self, timeframes: Mapping[str, Mapping[str, Any]], metrics: Mapping[str, Any]
    ) -> dict[str, Any]:
        biases = [frame.get("bias") for frame in timeframes.values() if frame]
        confidence = _first_numeric(
            [metrics.get("ema_strength"), metrics.get("wlwci"), metrics.get("rc")]
        )
        direction = next((bias for bias in biases if bias), "neutral")
        confidence = confidence if confidence is not None else 1.0
        return {
            "alignment_score": confidence,
            "trend_alignment": confidence,
            "final_confluence": confidence,
            "confidence": confidence,
            "mode": "integrated",
            "direction": direction,
            "entry_delay": False,
            "sync_status": "stable",
            "system_status": "ACTIVE",
        }


class TWMS_EMA_Strength:
    MODULE_NAME = "TWMS_EMA_STRENGTH"

    def __init__(self, ema_period: int = 50) -> None:
        self.ema_period = ema_period

    def integrate_with_twms(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        wlwci = _coerce_float(payload.get("wlwci")) or 0.0
        ema_strength = min(1.0, max(0.0, wlwci + 0.05))
        patched = {
            "wlwci": wlwci,
            "wlwci_adjusted": round(wlwci * ema_strength, 3),
            "ema_strength": round(ema_strength, 3),
            "twms_bias": payload.get("bias", "neutral"),
            "meta_patch": {"status": "applied", "module": self.MODULE_NAME},
        }
        return patched


class InstantExecutionGuard:
    def execute(
        self,
        *,
        pair: str,
        price_now: float,
        entry: float,
        conf12: float | None,
        rc: float,
        wlwci: float,
    ) -> tuple[str, str]:
        distance = abs(price_now - entry)
        if distance < 1e-6:
            return "EXECUTE", "Instant execution permitted."
        if conf12 is not None and conf12 > 0.9 and rc > 0.8 and wlwci > 0.8:
            return "EXECUTE", "High confidence alignment."
        return "WAIT", f"Pending alignment for {pair}."


class FusionLogFeedback:
    def __init__(self) -> None:
        self.log_dir = Path("data/fusion_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        pair: str,
        entry: float,
        stop_loss: float,
        sl_distance: float,
        risk_percent: float,
        lot_size: float,
        confidence: float,
        note: str,
        precision_zone: bool,
    ) -> None:
        payload = {
            "pair": pair,
            "entry": entry,
            "stop_loss": stop_loss,
            "sl_distance": sl_distance,
            "risk_percent": risk_percent,
            "lot_size": lot_size,
            "confidence": confidence,
            "note": note,
            "precision_zone": precision_zone,
            "timestamp": datetime.utcnow().isoformat(),
        }
        log_path = self.log_dir / "fusion_log.jsonl"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")

    def summary(
        self, pair: str, note: str, confidence: float, precision_zone: bool
    ) -> None:
        summary_path = self.log_dir / "fusion_summary.log"
        line = (
            f"{datetime.utcnow().isoformat()} | {pair} | "
            f"conf={confidence:.3f} | precision={precision_zone} | {note}"
        )
        with summary_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


class VaultRiskSync:
    def __init__(self) -> None:
        self.vault_path = Path("data/vault/risk_logs")
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.journal_file = self.vault_path / "journal.jsonl"

    def save(self, pair: str, risk_payload: dict[str, Any]) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        label = _normalise_pair_label(pair)
        file_path = self.vault_path / f"{label}_{timestamp}.json"
        file_path.write_text(json.dumps(risk_payload, indent=2), encoding="utf-8")
        return str(file_path)

    def append_journal_entry(
        self, entry: Mapping[str, Any], announce: bool = True
    ) -> None:
        with self.journal_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
        if announce:
            print(f"[JOURNAL] {entry}")


@dataclass(slots=True)
class CalibrationSummary:
    new_confidence_weight: float

    def as_dict(self) -> dict[str, Any]:
        return {"new_confidence_weight": self.new_confidence_weight}


class RiskFeedbackCalibrator:
    def __init__(self, vault_path: str = "data/vault/risk_logs/") -> None:
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self._last_calibration: CalibrationSummary | dict[str, Any] | None = None
        self._snapshot_path: Path | None = None

    def load_risk_data(self, limit: int = 10) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for path in sorted(self.vault_path.glob("*.json"), reverse=True)[:limit]:
            try:
                entries.append(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue
        return entries

    def calibrate(self, recent_data: list[dict[str, Any]]) -> CalibrationSummary:
        confidences = [
            _coerce_float(entry.get("confidence", 0.0)) or 0.0 for entry in recent_data
        ]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.75
        self._last_calibration = CalibrationSummary(new_confidence_weight=avg_conf)
        return self._last_calibration

    def save_calibration(self) -> str | None:
        if self._last_calibration is None:
            return None
        payload = (
            self._last_calibration.as_dict()
            if isinstance(self._last_calibration, CalibrationSummary)
            else self._last_calibration
        )
        snapshot_dir = self.vault_path / "calibration"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        path = snapshot_dir / f"calibration_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._snapshot_path = path
        return str(path)


@dataclass(slots=True)
class RiskAssessment:
    confidence: float
    mode: str
    adjusted_risk: float
    risk_amount: float
    lot_size: float
    vault_log_path: str
    alignment_score: float
    calibration: CalibrationSummary | dict[str, Any]


def calculate_dynamic_risk(confidence: float, mode: str) -> float:
    base = max(0.0, min(confidence, 1.0))
    if mode == "aggressive":
        return min(0.02, base * 0.02)
    if mode == "reflexive":
        return min(0.015, base * 0.015)
    return min(0.01, base * 0.01)


def calculate_lot_size(
    balance: float, entry_price: float, stop_loss: float, pip_value: float, risk_percent: float
) -> float:
    risk_amount = balance * (risk_percent / 100)
    sl_distance = abs(entry_price - stop_loss)
    if sl_distance == 0 or pip_value == 0:
        return 0.0
    return round(risk_amount / (sl_distance * pip_value), 3)


def calculate_adaptive_risk(
    *,
    account_balance: float,
    risk_percent: float,
    entry_price: float,
    stop_loss_price: float,
    pair: str,
    quote_to_usd_rate: float | None = None,
) -> dict[str, Any]:
    rate = quote_to_usd_rate if quote_to_usd_rate is not None else 1.0
    risk_amount = round(account_balance * (risk_percent / 100) * rate, 2)
    pip_value = 9.1 if "JPY" in pair.upper() else 10.0
    lot_size = calculate_lot_size(account_balance, entry_price, stop_loss_price, pip_value, risk_percent)
    return {
        "account_balance": account_balance,
        "risk_percent": risk_percent,
        "risk_amount": risk_amount,
        "lot_size": lot_size,
        "pip_value": pip_value,
    }


def calculate_risk(
    balance: float,
    *,
    drawdown: float,
    confidence: float,
    reflex_coherence: float,
    mode: str,
    pair: str,
    entry_price: float,
    stop_loss: float,
    pip_value: float,
    persist: bool,
    alignment_score: int | None = None,
) -> RiskAssessment:
    risk_percent = calculate_dynamic_risk(confidence, mode)
    risk_amount = balance * risk_percent
    lot_size = calculate_lot_size(balance, entry_price, stop_loss, pip_value, risk_percent * 100)
    vault = VaultRiskSync()
    payload = {
        "pair": pair,
        "confidence": confidence,
        "mode": mode,
        "risk_percent": risk_percent * 100,
        "risk_amount": risk_amount,
        "lot_size": lot_size,
        "alignment_score": alignment_score or confidence,
    }
    log_path = vault.save(pair, payload) if persist else ""
    calibration = CalibrationSummary(new_confidence_weight=confidence)
    return RiskAssessment(
        confidence=confidence,
        mode=mode,
        adjusted_risk=risk_percent * 100,
        risk_amount=risk_amount,
        lot_size=lot_size,
        vault_log_path=log_path,
        alignment_score=alignment_score or confidence,
        calibration=calibration,
    )


def generate_final_output(payload: Mapping[str, Any]) -> str:
    parts = [f"{key}: {value}" for key, value in payload.items()]
    return "\n".join(parts)


def execute_precision_entry_pipeline(
    pair: str,
    swing_low: float,
    swing_high: float,
    ema_value: float | None,
    vwap_value: float | None,
    atr_h4: float | None,
    daily_levels: Sequence[float] | None,
    weekly_levels: Sequence[float] | None,
    confidence: float,
    wlwci: float,
    balance: float,
    *,
    price_now: float | None = None,
) -> dict[str, Any]:
    mid_point = (swing_low + swing_high) / 2
    entry_price = price_now if price_now is not None else mid_point
    stop_loss = swing_low
    risk_percent = round(min(max(confidence, 0.5), 1.5), 2)
    pip_value = 9.1 if "JPY" in pair.upper() else 10.0
    lot_size = calculate_lot_size(balance, entry_price, stop_loss, pip_value, risk_percent)
    return {
        "entry": entry_price,
        "stop_loss": stop_loss,
        "alignment_score": confidence,
        "precision_zone": "PRECISION_ZONE" if wlwci > 0.8 else "NORMAL",
        "risk_percent": risk_percent,
        "sl_pips": abs(entry_price - stop_loss) * pip_value,
        "lot_size": lot_size,
        "risk_amount": balance * (risk_percent / 100),
    }


_PATCH_LOG_PATH = Path("data/vault/logs/patch_register.log")
_PRECISION_JOURNAL_DIR = Path("journals")
_PRIMARY_TIMEFRAMES: tuple[str, ...] = ("W1", "D1", "H4", "H1")
_TIMEFRAME_SEQUENCE = ("W1", "D1", "H4", "H1")
_TIMEFRAME_METRIC_SUFFIXES: Dict[str, tuple[str, ...]] = {
    "trend": ("trend", "bias", "direction"),
    "ema_bias": ("ema", "ema_bias", "ema_strength"),
    "divergence": ("dvg", "divergence", "divergence_conf", "divergence_confidence"),
    "wlwci": ("wlwci", "wlwci_adj", "wlwci_adjusted"),
    "reflex_coherence": ("rc", "reflex", "reflex_coherence", "reflex_integrity"),
}

TWMS_PATCH = TWMS_EMA_Strength(ema_period=50)
MULTI_TF_INTEGRATOR = MultiTimeframeIntegrator()
FUNDAMENTAL_CONTEXT = FundamentalContextIntegrator()
_PATCH_REGISTRY = PatchRegistry()
_INSTANT_EXECUTION_GUARD = InstantExecutionGuard()
_PRECISION_ALERT_COOLDOWN = 5.0
_PRECISION_ALERT_STATE: Dict[str, tuple[float, str]] = {}
_FUSION_LOGGER = FusionLogFeedback()

_PATCH_REGISTRY.register_patch(
    "TWMS_EMA_STRENGTH",
    "v5.3.2-AGI",
    "active",
    "Enhance WLWCI using EMA slope for trend integrity calibration",
)
_PATCH_REGISTRY.register_patch(
    MultiTimeframeIntegrator.MODULE_NAME,
    MultiTimeframeIntegrator.MODULE_VERSION,
    MultiTimeframeIntegrator.STATUS.lower(),
    "Multi timeframe confluence aggregation",
)
_PATCH_REGISTRY.register_patch(
    FundamentalContextIntegrator.MODULE_NAME,
    FundamentalContextIntegrator.MODULE_VERSION,
    FundamentalContextIntegrator.STATUS,
    "Inject macro context snapshot into Layer-12 output",
)


def _normalise_pair_label(pair: str) -> str:
    return pair.replace("/", "_").replace(" ", "_").upper() or "UNKNOWN"


def _append_precision_journal(pair: str, entry: Mapping[str, Any]) -> None:
    try:
        _PRECISION_JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
        label = _normalise_pair_label(pair)
        journal_path = _PRECISION_JOURNAL_DIR / f"{label}_journal.json"
        with journal_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
    except Exception as exc:  # pragma: no cover - telemetry only
        print(f"[WARN] Gagal mencatat journal FTA: {exc}")


def _should_emit_precision_notification(pair: str, status: str) -> bool:
    now = monotonic()
    label = _normalise_pair_label(pair)
    last_state = _PRECISION_ALERT_STATE.get(label)
    if last_state is None or last_state[1] != status or now - last_state[0] >= _PRECISION_ALERT_COOLDOWN:
        _PRECISION_ALERT_STATE[label] = (now, status)
        return True
    return False


def _notify_precision_zone(pair: str, status: str, alignment: Any) -> None:
    if not _should_emit_precision_notification(pair, status):
        return
    alignment_display = f"{float(alignment):.4f}" if isinstance(alignment, (int, float)) else str(alignment)
    if status == "PRECISION_ZONE":
        print(f"⚡ PRECISION ZONE DETECTED → {pair} | Alignment Score: {alignment_display}")
    else:
        print(f"ℹ NORMAL ZONE → {pair} | Alignment Score: {alignment_display}")


def _coerce_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        stripped = value.strip().rstrip("%")
        if not stripped:
            return None
        try:
            number = float(stripped)
        except ValueError:
            return None
    else:
        return None
    return None if isnan(number) else number


def _detect_bias(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if any(token in text for token in ("bull", "buy", "long")):
        return "buy"
    if any(token in text for token in ("bear", "sell", "short")):
        return "sell"
    if any(token in text for token in ("wait", "flat", "side", "neutral", "range")):
        return "neutral"
    return None


def _resolve_timeframe_signal(
    timeframe: str, sources: Sequence[Dict[str, Any]], fallback_confidence: float
) -> TimeframeSignal | None:
    bias: str | None = None
    confidence: float | None = None
    confluence: float | None = None
    weight: float | None = None
    tf_upper = timeframe.upper()
    tf_lower = tf_upper.lower()

    for source in sources:
        direct = source.get(tf_upper) or source.get(tf_lower)
        if isinstance(direct, dict):
            bias = bias or _detect_bias(
                direct.get("bias")
                or direct.get("direction")
                or direct.get("trend")
                or direct.get("signal")
            )
            if confidence is None:
                for key in ("confidence", "score", "alignment", "grade", "strength"):
                    candidate = _coerce_float(direct.get(key))
                    if candidate is not None:
                        confidence = candidate
                        break
            if confluence is None:
                for key in ("confluence", "confluence_score", "confluence_index", "final_confluence"):
                    candidate = _coerce_float(direct.get(key))
                    if candidate is not None:
                        confluence = candidate
                        break
            if weight is None:
                candidate = _coerce_float(direct.get("weight"))
                if candidate is not None:
                    weight = candidate

        for key, value in source.items():
            key_lower = str(key).lower()
            if tf_lower not in key_lower:
                continue
            if bias is None and any(token in key_lower for token in ("bias", "direction", "trend", "signal")):
                bias = _detect_bias(value)
            if confidence is None and any(token in key_lower for token in ("confidence", "score", "align", "grade", "strength")):
                candidate = _coerce_float(value)
                if candidate is not None:
                    confidence = candidate
            if confluence is None and "confluence" in key_lower:
                candidate = _coerce_float(value)
                if candidate is not None:
                    confluence = candidate
            if weight is None and "weight" in key_lower:
                candidate = _coerce_float(value)
                if candidate is not None:
                    weight = candidate

    if bias is None:
        return None

    conf_value = confidence if confidence is not None else fallback_confidence

    return TimeframeSignal(
        timeframe=tf_upper,
        bias=bias,
        confidence=conf_value,
        confluence=confluence,
        weight=weight,
    )


def _extract_timeframe_signals(directive: "AGIReasoningOutput") -> List[TimeframeSignal]:
    sources: List[Dict[str, Any]] = []
    if isinstance(directive.final_report_data, dict):
        sources.append(directive.final_report_data)
    if isinstance(directive.twms_payload, dict):
        sources.append(directive.twms_payload)

    signals: List[TimeframeSignal] = []
    for timeframe in _PRIMARY_TIMEFRAMES:
        signal = _resolve_timeframe_signal(timeframe, sources, directive.confidence)
        if signal:
            signals.append(signal)
    return signals


def _apply_risk_modifier(payload: Dict[str, Any], modifier: float | None) -> None:
    if not isinstance(payload, dict):
        return
    modifier_value = _coerce_float(modifier)
    if modifier_value is None or abs(modifier_value - 1.0) < 1e-9:
        return
    modifier_value = max(0.0, min(modifier_value, 2.0))

    payload["risk_modifier"] = round(modifier_value, 3)
    precision_map = {"risk_percent": 4, "risk_amount": 2, "lot_size": 4}
    for key, precision in precision_map.items():
        value = _coerce_float(payload.get(key))
        if value is None:
            continue
        base_key = f"{key}_base"
        payload.setdefault(base_key, value)
        payload[key] = round(value * modifier_value, precision)


def _first_numeric(values: Iterable[Any]) -> float | None:
    for value in values:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if isnan(numeric):
            continue
        return numeric
    return None


def _flatten_numeric_levels(value: Any) -> list[float]:
    levels: list[float] = []
    if value is None:
        return levels
    if isinstance(value, Mapping):
        for nested in value.values():
            levels.extend(_flatten_numeric_levels(nested))
        return levels
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for nested in value:
            levels.extend(_flatten_numeric_levels(nested))
        return levels
    try:
        number = float(value)
    except (TypeError, ValueError):
        return levels
    if number != number:
        return levels
    levels.append(number)
    return levels


def _extract_numeric_from_sources(
    sources: Sequence[Mapping[str, Any]], keys: Sequence[str]
) -> float | None:
    candidates: list[Any] = []
    for source in sources:
        if not isinstance(source, Mapping):
            continue
        lower_map = {str(k).lower(): value for k, value in source.items()}
        for key in keys:
            key_lower = key.lower()
            if key_lower in lower_map:
                candidates.append(lower_map[key_lower])
    return _first_numeric(candidates)


def _extract_level_series(sources: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> list[float]:
    levels: list[float] = []
    normalized = {key.lower() for key in keys}
    for source in sources:
        if not isinstance(source, Mapping):
            continue
        lower_map = {str(k).lower(): value for k, value in source.items()}
        for key, value in lower_map.items():
            if key in normalized:
                levels.extend(_flatten_numeric_levels(value))
    return levels


def _collect_timeframes(payload: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    definitions = {
        "W1": {"bias": ("w1_bias", "w1_conclusion", "macro_conclusion"), "confidence": ("w1_confidence", "macro_confidence", "confidence")},
        "D1": {"bias": ("d1_bias", "d1_conclusion"), "confidence": ("conf_d1", "d1_confidence", "confidence")},
        "H4": {"bias": ("h4_bias", "h4_conclusion"), "confidence": ("conf_h4", "h4_confidence", "confidence")},
        "H1": {"bias": ("h1_bias", "h1_conclusion"), "confidence": ("conf_h1", "h1_confidence", "confidence")},
    }

    frames: Dict[str, Dict[str, Any]] = {}
    for frame, config in definitions.items():
        bias = _extract_bias(payload, config["bias"])
        confidence = _first_numeric(payload.get(key) for key in config["confidence"])
        frames[frame] = {"bias": bias, "confidence": confidence if confidence is not None else 0.75}
    return frames


def _collect_timeframe_signals(directive: "AGIReasoningOutput") -> list[TimeframeSignal]:
    overrides: Dict[str, Mapping[str, Any]] = {}
    metrics = getattr(directive, "timeframe_metrics", None)
    if isinstance(metrics, Mapping):
        for timeframe, payload in metrics.items():
            if isinstance(payload, Mapping):
                overrides[timeframe.upper()] = payload

    base_sources: list[Mapping[str, Any]] = []
    if isinstance(directive.final_report_data, Mapping):
        base_sources.append(directive.final_report_data)
    if isinstance(directive.twms_payload, Mapping):
        base_sources.append(directive.twms_payload)
    base_sources.append(vars(directive))

    signals: list[TimeframeSignal] = []
    processed: set[str] = set()

    def gather(timeframe: str) -> None:
        tf_upper = timeframe.upper()
        extra = overrides.get(tf_upper)
        sources = [extra, *base_sources] if extra else base_sources
        prefix = tf_upper.lower()
        values: Dict[str, Any] = {}
        for metric_name, suffixes in _TIMEFRAME_METRIC_SUFFIXES.items():
            candidates: list[str] = []
            for suffix in suffixes:
                suffix_lower = suffix.lower()
                candidates.extend(
                    [
                        f"{prefix}_{suffix_lower}",
                        f"{prefix}{suffix_lower}",
                        f"{tf_upper}_{suffix_lower}",
                        f"{tf_upper}{suffix_lower}",
                        suffix_lower,
                        suffix_lower.upper(),
                    ]
                )
            candidates = list(dict.fromkeys(candidates))
            value = _extract_metric(sources, candidates)
            if value is None and extra and metric_name in extra:
                value = extra[metric_name]
            values[metric_name] = value
        if any(val not in (None, "") for val in values.values()):
            signals.append(
                TimeframeSignal(
                    timeframe=tf_upper,
                    trend=values.get("trend"),
                    ema_bias=values.get("ema_bias"),
                    divergence=values.get("divergence"),
                    wlwci=values.get("wlwci"),
                    reflex_coherence=values.get("reflex_coherence"),
                )
            )
            processed.add(tf_upper)

    for timeframe in _TIMEFRAME_SEQUENCE:
        gather(timeframe)

    for timeframe in overrides:
        if timeframe not in processed:
            gather(timeframe)

    return signals


def _extract_metric(sources: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> Any | None:
    for source in sources:
        try:
            items = source.items()
        except AttributeError:
            continue
        for key in keys:
            if key in source:
                value = source[key]
                if value not in (None, ""):
                    return value
        lower_map = {str(k).lower(): v for k, v in items}
        for key in keys:
            lowered = key.lower()
            if lowered in lower_map:
                value = lower_map[lowered]
                if value not in (None, ""):
                    return value
    return None


def _extract_fta_context(directive: "AGIReasoningOutput") -> Dict[str, Any] | None:
    sources: list[Mapping[str, Any]] = []
    if isinstance(directive.final_report_data, Mapping):
        sources.append(directive.final_report_data)
    if isinstance(directive.twms_payload, Mapping):
        sources.append(directive.twms_payload)
    timeframe_metrics = getattr(directive, "timeframe_metrics", None)
    if isinstance(timeframe_metrics, Mapping):
        for payload in timeframe_metrics.values():
            if isinstance(payload, Mapping):
                sources.append(payload)
    sources.append(dict(vars(directive)))

    swing_low = _extract_numeric_from_sources(sources, ("swing_low", "recent_low", "range_low", "low"))
    swing_high = _extract_numeric_from_sources(sources, ("swing_high", "recent_high", "range_high", "high"))
    price_now = _extract_numeric_from_sources(sources, ("price_now", "current_price", "price", "close", "last_price"))
    if price_now is None:
        price_now = directive.entry_price

    if swing_low is None or swing_high is None or price_now is None:
        return None

    if swing_high < swing_low:
        swing_low, swing_high = swing_high, swing_low

    ema_value = _extract_numeric_from_sources(sources, ("ema50", "ema_50", "ema", "ema_value"))
    vwap_value = _extract_numeric_from_sources(
        sources,
        ("vwap", "session_vwap", "anchored_vwap", "vwap_value"),
    )
    atr_h4 = _extract_numeric_from_sources(
        sources,
        ("atr_h4", "atr", "atr_value", "atr_multiplier"),
    )
    daily_levels = _extract_level_series(
        sources,
        ("d1_key_levels", "daily_key_levels", "daily_levels", "d1_levels"),
    )
    weekly_levels = _extract_level_series(
        sources,
        ("w1_key_levels", "weekly_key_levels", "weekly_levels", "w1_levels"),
    )

    return {
        "swing_low": swing_low,
        "swing_high": swing_high,
        "price_now": price_now,
        "ema_value": ema_value,
        "vwap_value": vwap_value,
        "atr_h4": atr_h4,
        "daily_levels": daily_levels,
        "weekly_levels": weekly_levels,
    }


def _extract_bias(source: Mapping[str, Any], keys: Iterable[str]) -> str | None:
    for key in keys:
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


@dataclass(slots=True)
class VaultSyncResult:
    pair: str
    risk_payload: dict[str, Any]
    vault_log_path: str
    calibration: CalibrationSummary | dict[str, str]
    mtf_summary: Dict[str, Any] | None = None
    adaptive_snapshot: Dict[str, Any] | None = None
    adaptive_log_path: str | None = None
    calibration_path: str | None = None
    ema_patch: Dict[str, Any] | None = None
    integrator: Dict[str, Any] | None = None
    fta_alignment: Dict[str, Any] | None = None
    fundamental_context: Dict[str, Any] | None = None


class VaultSyncProtocol(Protocol):
    def save(self, pair: str, risk_payload: dict[str, Any]) -> str:  # pragma: no cover - interface only
        ...


def run_layer_12(
    directive: "AGIReasoningOutput",
    *,
    balance: float = DEFAULT_ACCOUNT_BALANCE,
    pip_value: float | None = None,
    vault_sync: VaultSyncProtocol | None = None,
    limit: int = 10,
    adaptive_context: Dict[str, Any] | None = None,
) -> VaultSyncResult:
    vault = vault_sync or VaultRiskSync()

    timeframe_signals = _extract_timeframe_signals(directive)
    mtf_summary: Dict[str, Any] | None = None
    if timeframe_signals:
        integrator = MultiTimeframeIntegrator()
        try:
            mtf_summary = integrator.compute_alignment_score(timeframe_signals, base_confidence=directive.confidence)
        except ValueError:
            mtf_summary = None

    pip_lookup = pip_value if pip_value is not None else (9.1 if "JPY" in directive.pair.upper() else 10.0)

    timeframe_signals = _collect_timeframe_signals(directive)
    mtf_result: Dict[str, Any] | None = None
    risk_modifier = 1.0
    if timeframe_signals:
        mtf_result = MultiTimeframeIntegrator().compute_alignment_score(timeframe_signals)
        modifier_value = _coerce_float(mtf_result.get("risk_modifier"))
        if modifier_value is not None:
            risk_modifier = modifier_value

    manager = AGIExecutionRiskManager(balance=balance, pip_value=pip_lookup)
    risk_payload = manager.compute_trade_risk(
        pair=directive.pair,
        confidence=directive.confidence,
        mode=directive.mode,
        entry=directive.entry_price,
        sl=directive.stop_loss,
    )
    fundamental_context: Dict[str, Any] | None = None
    try:
        fundamental_context = FUNDAMENTAL_CONTEXT.fetch_context(directive.pair)
    except Exception as exc:  # pragma: no cover - telemetry only
        fundamental_context = {"error": str(exc), "pair": directive.pair}
    if fundamental_context:
        risk_payload["fundamental_context"] = fundamental_context
    fta_context = _extract_fta_context(directive)
    fta_result: Dict[str, Any] | None = None
    if fta_context:
        fta_result = execute_precision_entry_pipeline(
            directive.pair,
            fta_context["swing_low"],
            fta_context["swing_high"],
            fta_context.get("ema_value"),
            fta_context.get("vwap_value"),
            fta_context.get("atr_h4"),
            fta_context.get("daily_levels"),
            fta_context.get("weekly_levels"),
            directive.confidence,
            directive.wlwci or 0.0,
            balance,
            price_now=fta_context.get("price_now"),
        )
        zone_status = fta_result.get("precision_zone", "NORMAL")
        _append_precision_journal(
            directive.pair,
            {
                "pair": directive.pair,
                "layer": "L10",
                "precision_zone": zone_status,
                "alignment_score": fta_result.get("alignment_score"),
                "nearest_fib": fta_result.get("fib_level"),
                "fib_ratio": fta_result.get("fib_ratio"),
                "nearest_keylevel": fta_result.get("key_level"),
            },
        )
        _notify_precision_zone(directive.pair, zone_status, fta_result.get("alignment_score"))
        risk_payload.setdefault("price_now", fta_context["price_now"])
        risk_payload.setdefault("fta_layer10", fta_result)

    base_risk_percent = _coerce_float(risk_payload.get("risk_percent"))
    _apply_risk_modifier(risk_payload, risk_modifier)
    adjusted_risk_percent = _coerce_float(risk_payload.get("risk_percent"))
    effective_risk_percent = adjusted_risk_percent or base_risk_percent or 1.0
    if effective_risk_percent < 0:
        effective_risk_percent = 0.0

    risk_payload["account"] = balance
    risk_payload["entry_price"] = directive.entry_price
    risk_payload["stop_loss"] = directive.stop_loss

    if mtf_summary:
        _apply_risk_modifier(risk_payload, mtf_summary.get("risk_modifier"))
        risk_payload["mtf_alignment"] = mtf_summary.get("alignment_score")
        risk_payload["mtf_confluence"] = mtf_summary.get("final_confluence")
        risk_payload["mtf_direction"] = mtf_summary.get("direction")
        risk_payload["mtf_confidence"] = mtf_summary.get("confidence")
        risk_payload["mtf_signals"] = mtf_summary.get("signals", [])
    adaptive_risk_summary = calculate_adaptive_risk(
        account_balance=balance,
        risk_percent=effective_risk_percent,
        entry_price=directive.entry_price,
        stop_loss_price=directive.stop_loss,
        pair=directive.pair,
    )

    risk_payload.setdefault("adaptive_summary", adaptive_risk_summary)

    if mtf_result:
        risk_payload.setdefault("multi_timeframe", mtf_result)

    log_path = vault.save(directive.pair, risk_payload)
    print(f"[VAULT SYNC] Risk data saved → {log_path}")

    patch_result: Dict[str, Any] | None = None
    if isinstance(directive.twms_payload, dict):
        patch_input = dict(directive.twms_payload)
        if directive.wlwci is not None:
            patch_input.setdefault("wlwci", directive.wlwci)
        patch_result = TWMS_PATCH.integrate_with_twms(patch_input)
        _log_patch_event(patch_result)

    base_report: Dict[str, Any] = {}
    if isinstance(directive.final_report_data, dict):
        base_report = dict(directive.final_report_data)

    timeframe_payload: Mapping[str, Mapping[str, Any]]
    if base_report and isinstance(base_report.get("timeframes"), Mapping):
        timeframe_payload = base_report["timeframes"]  # type: ignore[assignment]
    else:
        timeframe_payload = _collect_timeframes(base_report)

    metrics = _collect_metrics(base_report, patch_result, risk_payload, directive.wlwci)
    integrator_result: Dict[str, Any] | None = None
    if timeframe_payload and metrics:
        has_bias = any(
            isinstance(frame.get("bias"), str) and frame["bias"].strip() for frame in timeframe_payload.values()
        )
        if has_bias:
            try:
                integrator_result = MULTI_TF_INTEGRATOR.integrate(timeframe_payload, metrics)
            except ValueError:
                integrator_result = None

    if integrator_result:
        _apply_integrator_to_risk(risk_payload, integrator_result)

    log_path = vault.save(directive.pair, risk_payload)
    print(f"[VAULT SYNC] Risk data saved → {log_path}")

    adaptive_snapshot: Dict[str, Any] | None = None
    adaptive_log_path: str | None = None

    if adaptive_context:
        pair = str(adaptive_context.get("pair", "UNKNOWN")).upper()
        confidence = float(adaptive_context.get("confidence", 0.0))
        mode = str(adaptive_context.get("mode", "normal"))
        entry_price = float(adaptive_context.get("entry_price", 0.0))
        stop_loss = float(adaptive_context.get("stop_loss", 0.0))
        balance_ctx = float(adaptive_context.get("balance", DEFAULT_ACCOUNT_BALANCE))
        pip_value_ctx = float(adaptive_context.get("pip_value", 9.1 if "JPY" in pair else 10.0))

        risk_percent = calculate_dynamic_risk(confidence, mode)
        if mtf_result:
            risk_percent *= risk_modifier
        lot_size = calculate_lot_size(balance_ctx, entry_price, stop_loss, pip_value_ctx, risk_percent * 100)
        risk_amount = round(balance_ctx * risk_percent, 2)
        adaptive_snapshot = {
            "pair": pair,
            "confidence": round(confidence, 3),
            "mode": mode,
            "risk_percent": round(risk_percent * 100, 2),
            "risk_amount": risk_amount,
            "lot_size": lot_size,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "balance": balance_ctx,
            "pip_value": pip_value_ctx,
        }
        if mtf_result:
            adaptive_snapshot["risk_modifier"] = round(risk_modifier, 3)
            adaptive_snapshot["mtf_alignment"] = mtf_result.get("alignment_score")
            adaptive_snapshot["mtf_confluence"] = mtf_result.get("final_confluence")
        risk_fraction = calculate_dynamic_risk(confidence, mode)
        quote_to_usd_rate = 1.0
        if not pair.endswith("USD") and pip_value_ctx > 0:
            quote_to_usd_rate = pip_value_ctx / 10.0

        adaptive_snapshot = calculate_adaptive_risk(
            account_balance=balance_ctx,
            risk_percent=risk_fraction * 100,
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            pair=pair,
            quote_to_usd_rate=quote_to_usd_rate,
        )
        adaptive_snapshot.update(
            {
                "confidence": round(confidence, 3),
                "mode": mode,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "pip_value": round(pip_value_ctx, 2),
            }
        )

        vault_adaptive = VaultRiskSync()
        adaptive_log_path = vault_adaptive.save(pair, adaptive_snapshot)
        print("[LAYER 12][ADAPTIVE RISK] " f"{pair} → {adaptive_snapshot} (log: {adaptive_log_path})")

    feedback = RiskFeedbackCalibrator(vault_path="data/vault/risk_logs/")
    recent_data = feedback.load_risk_data(limit=limit)
    calibration_result = feedback.calibrate(recent_data)
    saved_path = feedback.save_calibration()

    print(f"[FEEDBACK] Calibrated → {calibration_result}")
    if saved_path:
        print(f"[FEEDBACK] Snapshot persisted → {saved_path}")

    final_data: Dict[str, Any] = dict(base_report)
    final_data.setdefault("pair", directive.pair)
    final_data.setdefault("phase", final_data.get("phase", directive.mode))
    final_data.setdefault("direction", final_data.get("direction", "-"))
    final_data.setdefault("entry", directive.entry_price)
    final_data.setdefault("sl", directive.stop_loss)
    final_data.setdefault("tp1", final_data.get("tp1", "-"))
    final_data.setdefault("tp2", final_data.get("tp2", "-"))
    if fundamental_context:
        final_data.setdefault("fundamental_context", fundamental_context)

    if isinstance(pip_lookup, (int, float)):
        final_data.setdefault("pip_value", pip_lookup)

    if mtf_summary:
        if final_data.get("direction") in {None, "-", ""}:
            final_data["direction"] = mtf_summary.get("direction", final_data.get("direction"))
        final_data.setdefault("mtf_direction", mtf_summary.get("direction"))
        final_data.setdefault("mtf_alignment", mtf_summary.get("alignment_score"))
        final_data.setdefault("mtf_confluence", mtf_summary.get("final_confluence"))
        final_data.setdefault("mtf_confidence", mtf_summary.get("confidence"))
        final_data.setdefault("risk_modifier", mtf_summary.get("risk_modifier"))

    risk_percent_value = risk_payload.get("risk_percent")
    risk_display: Any
    if isinstance(risk_percent_value, (int, float)):
        risk_display = f"{risk_percent_value:.2f}%"
    else:
        risk_display = risk_percent_value or "-"

    final_data.setdefault("lot", risk_payload.get("lot_size", "-"))
    final_data.setdefault("risk", final_data.get("risk", risk_display))
    final_data.setdefault("rr", final_data.get("rr", "-"))
    final_data.setdefault("confidence", round(directive.confidence, 3))
    final_data.setdefault("mode", directive.mode)
    final_data.setdefault(
        "exec_status", final_data.get("exec_status", risk_payload.get("mode", "PENDING"))
    )

    if isinstance(risk_payload.get("confidence"), (int, float)):
        final_data.setdefault("rc", risk_payload.get("confidence"))
    final_data.setdefault("integrity", final_data.get("integrity", "-"))

    if fta_result:
        final_data.setdefault("precision_zone", fta_result.get("precision_zone"))
        final_data.setdefault("precision_tolerance", fta_result.get("precision_tolerance"))
        final_data.setdefault("fta_alignment_score", fta_result.get("alignment_score"))
        final_data.setdefault("fta_layer10", fta_result)
        final_data.setdefault("precision_entry", risk_payload.get("precision_entry"))
        final_data.setdefault("precision_entry_price", risk_payload.get("precision_entry_price"))
        final_data.setdefault("precision_stop_loss", risk_payload.get("precision_stop_loss"))
        final_data.setdefault("precision_risk_percent", risk_payload.get("precision_risk_percent"))
        final_data.setdefault("precision_lot_size", risk_payload.get("precision_lot_size"))
        final_data.setdefault("precision_risk_amount", risk_payload.get("precision_risk_amount"))
        final_data.setdefault("precision_note", risk_payload.get("precision_note"))

    if patch_result:
        final_data.setdefault("ema_strength", patch_result.get("ema_strength"))
        final_data.setdefault("wlwci_adj", patch_result.get("wlwci_adjusted"))
        final_data.setdefault("wlwci", patch_result.get("wlwci"))
        final_data.setdefault("twms_bias", patch_result.get("twms_bias"))
        final_data.setdefault("wl_base", patch_result.get("wlwci"))
        if "divergence_confidence" in patch_result:
            final_data.setdefault("divergence_conf", patch_result.get("divergence_confidence"))

    if integrator_result:
        final_data["alignment_score"] = f"{integrator_result['alignment_score']:+.2f}"
        final_data["trend_alignment"] = f"{integrator_result['trend_alignment']:.2f}"
        final_data["final_confluence"] = f"{integrator_result['final_confluence']:.2f}"
        final_data["confidence"] = round(integrator_result["confidence"], 3)
        final_data["mode"] = str(integrator_result["mode"]).title()
        final_data["direction"] = integrator_result["direction"]
        final_data["entry_delay"] = "YES" if integrator_result["entry_delay"] else "NO"
        final_data["sync_status"] = integrator_result["sync_status"]
        final_data["system_status"] = integrator_result["system_status"]

    if adaptive_snapshot:
        final_data.setdefault("reflex_integrity", adaptive_snapshot.get("confidence"))

    if mtf_result:
        final_data.setdefault("alignment_score", mtf_result.get("alignment_score"))
        final_data.setdefault("final_confluence", mtf_result.get("final_confluence"))
        final_data.setdefault("risk_modifier", mtf_result.get("risk_modifier"))
        final_data.setdefault("mtf_confidence", mtf_result.get("confidence"))
        final_data.setdefault("mtf_direction", mtf_result.get("direction"))
        final_data.setdefault("mtf_timeframes", mtf_result.get("timeframes"))
        final_data.setdefault("mtf_alignment", {k: v for k, v in mtf_result.items() if k != "timeframes"})
        if final_data.get("direction") in {"-", None, ""}:
            final_data["direction"] = mtf_result.get("direction", final_data.get("direction"))

    calibration_payload: Dict[str, Any] | None = None
    if isinstance(calibration_result, CalibrationSummary):
        calibration_payload = calibration_result.as_dict()
    elif isinstance(calibration_result, dict):
        calibration_payload = calibration_result

    if calibration_payload:
        final_data.setdefault("cognition", calibration_payload.get("new_confidence_weight"))

    final_data.setdefault("alignment_score", "-")
    final_data.setdefault("trend_alignment", "-")
    final_data.setdefault("final_confluence", "-")
    final_data.setdefault("sync_status", "-")
    final_data.setdefault("entry_delay", "-")
    final_data.setdefault("mc_conf", final_data.get("mc_conf", "-"))
    final_data.setdefault("divergence_conf", final_data.get("divergence_conf", "-"))
    final_data.setdefault("reflex_integrity", final_data.get("reflex_integrity", "-"))
    final_data.setdefault("wlwci_adj", final_data.get("wlwci_adj", "-"))
    final_data.setdefault("ema_strength", final_data.get("ema_strength", "-"))
    final_data.setdefault("system_status", final_data.get("system_status", "ACTIVE"))
    final_data.setdefault("final_conclusion", final_data.get("final_conclusion", "-"))

    execution_status = "WAIT"
    execution_note = "Parameter eksekusi tidak lengkap."
    entry_candidate = (
        _coerce_float(final_data.get("entry"))
        or _coerce_float(risk_payload.get("entry_price"))
        or _coerce_float(directive.entry_price)
    )
    price_candidate = _coerce_float(risk_payload.get("price_now")) or _coerce_float(final_data.get("price_now"))
    rc_candidate = (
        _coerce_float(final_data.get("rc"))
        or _coerce_float(risk_payload.get("confidence"))
        or _coerce_float(directive.confidence)
    )
    wlwci_candidate = (
        _coerce_float(final_data.get("wlwci"))
        or _coerce_float(risk_payload.get("wlwci"))
        or _coerce_float(risk_payload.get("wlwci_adj"))
    )
    if wlwci_candidate is None and directive.wlwci is not None:
        wlwci_candidate = _coerce_float(directive.wlwci)
    conf12_candidate = _coerce_float(final_data.get("CONF12")) or _coerce_float(final_data.get("conf12"))

    if entry_candidate is not None and price_candidate is not None and rc_candidate is not None and wlwci_candidate is not None:
        execution_status, execution_note = _INSTANT_EXECUTION_GUARD.execute(
            pair=directive.pair,
            price_now=float(price_candidate),
            entry=float(entry_candidate),
            conf12=conf12_candidate,
            rc=float(rc_candidate),
            wlwci=float(wlwci_candidate),
        )
    elif price_candidate is None:
        execution_note = "Data harga belum tersedia untuk evaluasi."

    final_data["execution_mode"] = "Instant" if execution_status == "EXECUTE" else "Pending"
    final_data["execution_note"] = execution_note
    final_data["instant_execution_status"] = execution_status
    risk_payload["execution_mode"] = final_data["execution_mode"]
    risk_payload["execution_note"] = execution_note
    risk_payload["instant_execution_status"] = execution_status

    try:
        report = generate_final_output(final_data)
        print(report)
        journal_dir = Path("vault/journal")
        journal_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        pair_label = str(final_data.get("pair", directive.pair or "UNKNOWN")).replace("/", "")
        report_path = journal_dir / f"{pair_label}_Layer12_{timestamp}.txt"
        report_path.write_text(report, encoding="utf-8")
    except Exception:  # pragma: no cover - telemetry only
        pass

    try:
        pair_value = directive.pair
        entry_value = _coerce_float(risk_payload.get("entry_price")) or _coerce_float(final_data.get("entry")) or float(directive.entry_price)
        stop_value = _coerce_float(risk_payload.get("stop_loss")) or _coerce_float(final_data.get("sl")) or float(directive.stop_loss)

        pip_factor = 100.0 if "JPY" in pair_value.upper() else 10000.0
        sl_distance = abs(entry_value - stop_value) * pip_factor if entry_value is not None and stop_value is not None else 0.0

        risk_percent_value = _coerce_float(risk_payload.get("risk_percent"))
        if risk_percent_value is None:
            risk_field = final_data.get("risk")
            if isinstance(risk_field, str):
                risk_field = risk_field.replace("%", "").strip()
            risk_percent_value = _coerce_float(risk_field)
        if risk_percent_value is None:
            risk_percent_value = 0.0

        lot_value = _coerce_float(risk_payload.get("lot_size")) or _coerce_float(final_data.get("lot")) or 0.0

        conf12_value = _coerce_float(final_data.get("confidence")) or _coerce_float(risk_payload.get("confidence")) or float(directive.confidence)

        note_value = (
            str(
                final_data.get("final_conclusion")
                or directive.notes
                or final_data.get("note")
                or ""
            ).strip()
        )
        if not note_value:
            note_value = "Layer-12 precision feedback"

        alignment_score = _coerce_float(fta_result.get("alignment_score")) if fta_result else None
        precision_zone_flag = bool(alignment_score and alignment_score > 0.85)
        if not precision_zone_flag and fta_result:
            status = str(fta_result.get("precision_zone", "")).upper()
            precision_zone_flag = status in {"PRECISION_ZONE", "TIER-1", "TIER1", "TIER-2", "TIER2"}

        _FUSION_LOGGER.write(
            pair_value,
            float(entry_value),
            float(stop_value),
            float(sl_distance),
            float(risk_percent_value),
            float(lot_value),
            float(conf12_value),
            note_value,
            precision_zone_flag,
        )
        _FUSION_LOGGER.summary(pair_value, note_value, float(conf12_value), precision_zone_flag)
    except Exception as exc:  # pragma: no cover - telemetry only
        print(f"[WARN] Fusion Log Feedback gagal: {exc}")

    return VaultSyncResult(
        pair=directive.pair,
        risk_payload=risk_payload,
        vault_log_path=log_path,
        calibration=calibration_result,
        mtf_summary=mtf_summary,
        adaptive_snapshot=adaptive_snapshot,
        adaptive_log_path=adaptive_log_path,
        calibration_path=str(saved_path) if saved_path else None,
        ema_patch=patch_result,
        integrator=integrator_result,
        fta_alignment=fta_result,
        fundamental_context=fundamental_context,
    )


ModeLiteral = Literal["normal", "reflexive", "aggressive"]


__all__ = [
    "AGIReasoningOutput",
    "AGIExecutionRiskManager",
    "TradeBias",
    "TradeDecision",
    "Layer12Output",
    "ProtoAGIEngine",
    "run_layer_12",
    "auto_risk_injection",
]


@dataclass(slots=True)
class AGIReasoningOutput:
    pair: str
    confidence: float
    mode: ModeLiteral
    entry_price: float
    stop_loss: float
    notes: str = ""
    twms_payload: Dict[str, Any] | None = None
    wlwci: float | None = None
    final_report_data: Dict[str, Any] | None = None
    timeframe_metrics: Dict[str, Dict[str, Any]] | None = None

    def as_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "pair": self.pair,
            "confidence": round(self.confidence, 3),
            "mode": self.mode,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "notes": self.notes,
        }
        if self.twms_payload is not None:
            payload["twms_payload"] = self.twms_payload
        if self.wlwci is not None:
            payload["wlwci"] = self.wlwci
        if self.final_report_data is not None:
            payload["final_report_data"] = self.final_report_data
        if self.timeframe_metrics is not None:
            payload["timeframe_metrics"] = self.timeframe_metrics
        return payload


class AGIExecutionRiskManager:
    """Adaptive risk calibration for Layer 12 execution integrity."""

    def __init__(self, balance: float = DEFAULT_ACCOUNT_BALANCE, pip_value: float = 9.1) -> None:
        if balance <= 0:
            raise ValueError("Balance must be positive")
        if pip_value <= 0:
            raise ValueError("Pip value must be positive")
        self.balance = balance
        self.pip_value = pip_value

    def compute_trade_risk(
        self,
        *,
        pair: str,
        confidence: float,
        mode: str,
        entry: float,
        sl: float,
        alignment_score: int | None = None,
    ) -> Dict[str, Any]:
        assessment: RiskAssessment = calculate_risk(
            self.balance,
            drawdown=0.0,
            confidence=confidence,
            reflex_coherence=confidence,
            mode=mode,
            pair=pair,
            entry_price=entry,
            stop_loss=sl,
            pip_value=self.pip_value,
            persist=True,
            alignment_score=alignment_score,
        )
        risk_amount = assessment.risk_amount
        return {
            "pair": pair,
            "confidence": assessment.confidence,
            "mode": assessment.mode,
            "risk_percent": assessment.adjusted_risk,
            "risk_amount": risk_amount,
            "lot_size": assessment.lot_size,
            "vault_log_path": assessment.vault_log_path,
            "alignment_score": assessment.alignment_score,
            "calibration": assessment.calibration.as_dict()
            if isinstance(assessment.calibration, CalibrationSummary)
            else assessment.calibration,
        }

    def update_balance(self, balance: float) -> None:
        if balance <= 0:
            raise ValueError("Balance must be positive")
        self.balance = balance


@dataclass(slots=True, frozen=True)
class TradeBias:
    direction: Literal["buy", "sell", "neutral"]
    confidence: float
    rationale: str | None = None

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "direction": self.direction,
            "confidence": round(self.confidence, 3),
        }
        if self.rationale:
            payload["rationale"] = self.rationale
        return payload


@dataclass(slots=True, frozen=True)
class TradeDecision:
    pair: str
    entry_price: float
    stop_loss: float
    mode: ModeLiteral
    bias: TradeBias
    risk_percent: float | None = None
    lot_size: float | None = None
    payload: Dict[str, Any] | None = None

    def as_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "pair": self.pair,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "mode": self.mode,
            "bias": self.bias.as_dict(),
        }
        if self.risk_percent is not None:
            data["risk_percent"] = round(self.risk_percent, 4)
        if self.lot_size is not None:
            data["lot_size"] = round(self.lot_size, 3)
        if self.payload is not None:
            data["payload"] = self.payload
        return data


@dataclass(slots=True, frozen=True)
class Layer12Output:
    decision: TradeDecision
    diagnostics: Dict[str, Any]
    vault_log_path: str | None = None
    adaptive_log_path: str | None = None
    calibration_path: str | None = None

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "decision": self.decision.as_dict(),
            "diagnostics": self.diagnostics,
        }
        if self.vault_log_path is not None:
            payload["vault_log_path"] = self.vault_log_path
        if self.adaptive_log_path is not None:
            payload["adaptive_log_path"] = self.adaptive_log_path
        if self.calibration_path is not None:
            payload["calibration_path"] = self.calibration_path
        return payload


class ProtoAGIEngine:
    """High-level orchestrator that wraps :func:`run_layer_12`."""

    def __init__(self, *, vault_sync: VaultSyncProtocol | None = None) -> None:
        self._vault_sync = vault_sync

    def run(
        self,
        directive: AGIReasoningOutput,
        *,
        balance: float = DEFAULT_ACCOUNT_BALANCE,
        pip_value: float | None = None,
        limit: int = 10,
        adaptive_context: Dict[str, Any] | None = None,
    ) -> Layer12Output:
        result = run_layer_12(
            directive,
            balance=balance,
            pip_value=pip_value,
            vault_sync=self._vault_sync,
            limit=limit,
            adaptive_context=adaptive_context,
        )

        bias_value = _detect_bias(result.risk_payload.get("trend_direction")) or _detect_bias(
            result.risk_payload.get("direction")
        ) or _detect_bias(result.risk_payload.get("bias"))
        if bias_value is None:
            bias_value = "neutral"
        bias_map = {"bullish": "buy", "bearish": "sell"}
        direction = bias_map.get(bias_value, bias_value)
        if direction not in {"buy", "sell", "neutral"}:
            direction = "neutral"

        confidence = _coerce_float(result.risk_payload.get("confidence"))
        if confidence is None:
            confidence = float(directive.confidence)

        trade_bias = TradeBias(
            direction=direction,  # type: ignore[arg-type]
            confidence=float(confidence),
            rationale=str(
                result.risk_payload.get("integrator_mode")
                or result.risk_payload.get("mode")
                or directive.mode
            ),
        )

        entry_value = _coerce_float(result.risk_payload.get("entry_price"))
        stop_value = _coerce_float(result.risk_payload.get("stop_loss"))
        risk_percent = _coerce_float(result.risk_payload.get("risk_percent"))
        lot_size = _coerce_float(result.risk_payload.get("lot_size"))

        mode_value = str(result.risk_payload.get("mode", directive.mode)).lower()
        mode_literal: ModeLiteral
        if mode_value in {"normal", "reflexive", "aggressive"}:
            mode_literal = mode_value  # type: ignore[assignment]
        else:
            mode_literal = "normal"

        decision = TradeDecision(
            pair=result.pair,
            entry_price=entry_value if entry_value is not None else directive.entry_price,
            stop_loss=stop_value if stop_value is not None else directive.stop_loss,
            mode=mode_literal,
            bias=trade_bias,
            risk_percent=risk_percent,
            lot_size=lot_size,
            payload=dict(result.risk_payload),
        )

        diagnostics = {
            key: value
            for key, value in {
                "calibration": result.calibration,
                "mtf_summary": result.mtf_summary,
                "adaptive_snapshot": result.adaptive_snapshot,
                "ema_patch": result.ema_patch,
                "integrator": result.integrator,
                "fta_alignment": result.fta_alignment,
                "fundamental_context": result.fundamental_context,
            }.items()
            if value is not None
        }

        return Layer12Output(
            decision=decision,
            diagnostics=diagnostics,
            vault_log_path=result.vault_log_path,
            adaptive_log_path=result.adaptive_log_path,
            calibration_path=result.calibration_path,
        )

    def __call__(self, directive: AGIReasoningOutput, **kwargs: Any) -> Layer12Output:
        return self.run(directive, **kwargs)


def auto_risk_injection(
    pair: str,
    confidence: float,
    mode: str,
    entry: float,
    sl: float,
    *,
    quote_to_usd_rate: float = 1.0,
) -> Dict[str, Any]:
    normalized_pair = pair.upper()
    pip_value = 9.1 if "JPY" in normalized_pair else 10.0
    if not normalized_pair.endswith("USD"):
        quote_to_usd_rate = pip_value / 10.0

    risk_fraction = calculate_dynamic_risk(confidence, mode)
    snapshot = calculate_adaptive_risk(
        account_balance=DEFAULT_ACCOUNT_BALANCE,
        risk_percent=risk_fraction * 100,
        entry_price=entry,
        stop_loss_price=sl,
        pair=normalized_pair,
        quote_to_usd_rate=quote_to_usd_rate,
    )
    snapshot.update(
        {
            "confidence": round(confidence, 3),
            "mode": mode,
            "account": DEFAULT_ACCOUNT_BALANCE,
            "entry_price": entry,
            "stop_loss": sl,
        }
    )

    vault = VaultRiskSync()
    vault_log_path = vault.save(normalized_pair, snapshot)
    snapshot["vault_log_path"] = vault_log_path

    print(f"[AUTO-RISK ENGINE v5.3.2] {normalized_pair} → {snapshot}")
    return snapshot
