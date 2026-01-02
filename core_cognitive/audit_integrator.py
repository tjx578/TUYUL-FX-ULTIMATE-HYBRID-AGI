"""Audit trail integration utilities."""

from __future__ import annotations

from datetime import datetime
import json
import os
from typing import Any

from logs.logger_handler import log_audit as _log_audit_entry

AUDIT_PATH = os.path.join("data", "journals", "audit_journal.json")


def _format_detail(details: dict[str, Any]) -> str:
    return " ".join(f"{key}={value}" for key, value in details.items())


def audit_event(event_type: str, details: dict[str, Any]) -> dict[str, Any]:
    """Persist an audit log entry and return the recorded payload."""

    os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "details": details,
    }
    with open(AUDIT_PATH, "a", encoding="utf-8") as log_file:
        json.dump(entry, log_file)
        log_file.write("\n")

    _log_audit_entry(f"{event_type} {_format_detail(details)}".strip())
    return entry


__all__ = ["audit_event"]
