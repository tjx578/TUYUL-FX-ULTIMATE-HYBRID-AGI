#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧩 Divergence Subsystem — Fusion Spectre v6+
--------------------------------------------
TUYUL FX ULTIMATE HYBRID AGI v5.8r++ | Quad Vault Reflective Discipline Mode

Berfungsi sebagai entry-point reflektif untuk seluruh modul divergence.
Menangani auto-registration ke Journal & Vault saat runtime.

Submodules:
  • cci_mfi_divergence_detector_v6_production — deteksi divergence CCI–MFI reflektif
"""

from __future__ import annotations
import datetime
import json
from pathlib import Path

# === Metadata Reflective Module ===
__version__ = "6.0r++"
__build__ = "reflective-production"
__author__ = "TUYUL FX AGI Core Team"
__description__ = "Divergence Subsystem — Reflective Analyzer (CCI × MFI)"
__vault_layer__ = "Fusion Spectre Layer"
__integrity_tag__ = f"FusionDivergence_{__version__}"

# === Import modul utama ===
from .cci_mfi_divergence_detector_v6_production import cci_mfi_divergence_detector_v6

__all__ = [
    "cci_mfi_divergence_detector_v6",
    "__version__",
    "__build__",
    "__vault_layer__",
    "__integrity_tag__",
]

# === Auto-registration ke Vault System ===
VAULT_PATH = Path("data/integrity/system_integrity.json")
VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)


def _register_to_vault():
    """Daftarkan modul divergence ke Vault saat pertama kali di-load."""
    entry = {
        "module": __integrity_tag__,
        "version": __version__,
        "build": __build__,
        "vault_layer": __vault_layer__,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "status": "Registered",
    }

    try:
        if VAULT_PATH.exists():
            with open(VAULT_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data["FusionDivergence"] = entry

        with open(VAULT_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[WARN] Vault registration failed: {e}")


_register_to_vault()
