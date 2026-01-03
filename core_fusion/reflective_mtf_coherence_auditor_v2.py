#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 Reflective MTF Coherence Auditor v2.0 (Meta Learning Integration Mode)
-------------------------------------------------------------------------
TUYUL FX ULTIMATE HYBRID AGI v5.8r++ | Quad Vault Reflective Discipline

Tujuan:
  • Audit lintas timeframe (H1–H4–D1–W1) untuk mendeteksi divergence window
  • Sinkronisasi hasil dengan Meta-Learning Reflective Layer (REE)
  • Memberikan indikator stabilitas sistem reflektif antar vault

Pipeline:
  Reflex → Fusion (MTF Alignment) → TRQ–3D → Meta-Coherence → REE Feedback
"""

from __future__ import annotations

import datetime
import json
import statistics
from pathlib import Path


LOG_PATH = Path("data/logs/multi_timeframe_alignment_log.json")
AUDIT_PATH = Path("data/integrity/mtf_coherence_audit.json")
AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)


def reflective_mtf_coherence_auditor(
    lookback: int = 20,
    divergence_threshold: float = 0.15,
    integrity_threshold: float = 0.93,
) -> dict[str, object]:
    """
    Membaca log MTF Alignment terakhir dan menghitung MTF Coherence Stability.
    """

    try:
        with open(LOG_PATH, "r") as f:
            lines = [json.loads(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        return {"status": "No MTF alignment log found"}

    if len(lines) < lookback:
        return {"status": f"Insufficient data: {len(lines)} < {lookback}"}

    recent_data = lines[-lookback:]
    bias_strengths = [x["bias_strength"] for x in recent_data if "bias_strength" in x]
    coherence_indices = [x["time_coherence_index"] for x in recent_data if "time_coherence_index" in x]
    regimes = [x["regime_state"] for x in recent_data if "regime_state" in x]

    avg_strength = statistics.mean(bias_strengths)
    var_strength = statistics.pstdev(bias_strengths)
    avg_coherence = statistics.mean(coherence_indices)

    divergence_window = var_strength > divergence_threshold
    divergence_alert = "⚠️ MTF Divergence Detected" if divergence_window else "✅ Stable Alignment"

    stability_state = "Stable" if avg_coherence >= integrity_threshold else "Degraded"

    expansion = sum(1 for x in regimes if "Strong" in x)
    disaligned = sum(1 for x in regimes if "Disaligned" in x)
    expansion_ratio = expansion / len(regimes)
    disalign_ratio = disaligned / len(regimes)

    audit = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "avg_bias_strength": round(avg_strength, 3),
        "bias_volatility": round(var_strength, 3),
        "avg_coherence_index": round(avg_coherence, 3),
        "stability_state": stability_state,
        "divergence_alert": divergence_alert,
        "expansion_ratio": round(expansion_ratio, 3),
        "disalignment_ratio": round(disalign_ratio, 3),
        "meta_reflective_state": _meta_state(expansion_ratio, disalign_ratio),
        "note": "Reflective MTF Coherence Auditor v2.0 (Meta Learning Mode)",
    }

    _write_audit(audit)
    return audit


def _meta_state(expansion_ratio: float, disalign_ratio: float) -> str:
    """Menentukan status meta-reflektif berdasarkan distribusi regime."""

    if disalign_ratio > 0.4:
        return "Meta Warning – Divergent Field"
    if expansion_ratio >= 0.7:
        return "Meta Stable – Expansion Phase"
    if 0.4 <= expansion_ratio < 0.7:
        return "Meta Neutral – Balanced Coherence"
    return "Meta Drift – Recalibration Needed"


def _write_audit(data: dict) -> None:
    with open(AUDIT_PATH, "w") as f:
        json.dump(data, f, indent=2)


__all__ = ["reflective_mtf_coherence_auditor"]
