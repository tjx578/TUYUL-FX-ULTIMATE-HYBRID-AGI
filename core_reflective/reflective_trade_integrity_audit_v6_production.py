"""
🧾 Reflective Trade Integrity Audit v6 — Production Mode
--------------------------------------------------------
Melakukan audit integritas penuh terhadap semua eksekusi reflektif.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Dict, Any

LOG_PATH = Path("data/logs/reflective_audit_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def reflective_trade_integrity_audit_v6_production(
    plan: Dict[str, Any], execution: Dict[str, Any], vault_integrity: float
) -> Dict[str, Any]:
    deviation = abs(plan["tp"] - execution["tp"]) + abs(plan["sl"] - execution["sl"])
    integrity_score = round(vault_integrity * (1 - deviation / 2), 3)
    audit_status = "PASS" if integrity_score >= 0.95 else "WARN" if integrity_score >= 0.9 else "FAIL"

    result = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "plan_entry": plan["entry"],
        "execution_entry": execution["entry"],
        "type": plan["type"],
        "integrity_score": integrity_score,
        "audit_status": audit_status,
        "vault_integrity": vault_integrity,
        "note": "Reflective Integrity Audit v6 (Quad Vault)",
    }

    _log(result)
    return result


def _log(data: Dict[str, Any]) -> None:
    with open(LOG_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(data) + "\n")


__all__ = ["reflective_trade_integrity_audit_v6_production"]
