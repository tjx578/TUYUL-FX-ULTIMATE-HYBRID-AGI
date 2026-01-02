"""
integrity_engine.py – TUYUL FX HYBRID AGI 🧠⚙️
=============================================

Modul pengujian koherensi dan integritas kognitif reflektif.
Bertugas memastikan semua komponen reasoning (Cognitive, Reflex, Fusion, Meta)
berada dalam kondisi selaras dan stabil sebelum menjalankan Reflective Cycle.

Author: TUYUL FX Dev Division 🐺
Version: v5.8r++
"""

from __future__ import annotations
import json
import platform
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from core_cognitive.enums_cognitive_constants import (
    COHERENCE_THRESHOLD,
    INTEGRITY_MINIMUM,
    CONF12_REQUIRED,
    META_RESONANCE_LIMIT,
    REFLECTIVE_STATUS_MAP,
)

LOG_PATH = Path("data/integrity/system_integrity.json")
COHERENCE_LOG = Path("data/integrity/coherence_index.json")


class IntegrityEngine:
    """🧠 Engine utama pengujian integritas reflektif."""

    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat()
        self.system = platform.system()
        self.version = "v5.8r++"
        self.results: Dict[str, Any] = {}

    def evaluate_coherence(
        self, fusion_conf: float, wlwci: float, rcadj: float
    ) -> float:
        """Hitung indeks koherensi gabungan dari parameter reflektif utama."""
        coherence = round((fusion_conf * 0.4 + wlwci * 0.35 + rcadj * 0.25), 3)
        self.results["fusion_conf"] = fusion_conf
        self.results["wlwci"] = wlwci
        self.results["rcadj"] = rcadj
        self.results["coherence_index"] = coherence
        return coherence

    def validate_integrity(
        self,
        coherence_index: float,
        ree_integrity: float,
        reflective_integrity: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Menilai stabilitas keseluruhan integritas reflektif sistem."""
        reflective_integrity = reflective_integrity or ree_integrity
        avg_integrity = statistics.fmean([ree_integrity, reflective_integrity])
        status = "sync" if coherence_index >= COHERENCE_THRESHOLD else "training"
        integrity_state = (
            "PASS"
            if avg_integrity >= INTEGRITY_MINIMUM and coherence_index >= COHERENCE_THRESHOLD
            else "REVIEW"
        )

        integrity_score = round((avg_integrity + coherence_index) / 2, 3)
        integrity_snapshot = {
            "timestamp": self.timestamp,
            "system": self.system,
            "version": self.version,
            "coherence_index": coherence_index,
            "ree_integrity": ree_integrity,
            "reflective_integrity": reflective_integrity,
            "integrity_score": integrity_score,
            "status": status,
            "integrity_state": integrity_state,
            "summary": REFLECTIVE_STATUS_MAP.get(status, "unknown"),
        }

        self.results.update(integrity_snapshot)
        return integrity_snapshot

    def save_snapshot(self, output_path: Path = LOG_PATH) -> str:
        """Simpan hasil evaluasi integritas ke Vault."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.results, indent=2))
        return str(output_path)

    def verify_system_state(
        self, fusion_conf: float, wlwci: float, rcadj: float, ree_integrity: float
    ) -> Dict[str, Any]:
        """Jalankan evaluasi penuh terhadap koherensi dan integritas reflektif."""
        coherence_index = self.evaluate_coherence(fusion_conf, wlwci, rcadj)
        snapshot = self.validate_integrity(coherence_index, ree_integrity)
        snapshot["log_path"] = self.save_snapshot()
        return snapshot

    def is_stable(self, threshold: float = META_RESONANCE_LIMIT) -> bool:
        """Cek apakah sistem berada dalam batas resonansi aman."""
        coherence = self.results.get("coherence_index", 0)
        return coherence >= threshold


# ==========================================================
# 🧩 CLI / Debug Utility
# ==========================================================

if __name__ == "__main__":
    print("🧠 TUYUL FX AGI – Reflective Integrity Engine v5.8r++")
    engine = IntegrityEngine()

    # Simulasi input dari Fusion Layer (CONF₁₂, WLWCI, RCAdj)
    fusion_conf = 0.93
    wlwci = 0.92
    rcadj = 0.88
    ree_integrity = 0.91

    snapshot = engine.verify_system_state(
        fusion_conf=fusion_conf, wlwci=wlwci, rcadj=rcadj, ree_integrity=ree_integrity
    )

    print(json.dumps(snapshot, indent=2))
    if engine.is_stable():
        print("\n✅ System coherence stable – Reflective sync locked. ⚡🐺")
    else:
        print("\n⚠️ Resonance below optimal range – initiating meta-adjustment cycle.")
