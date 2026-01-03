from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


CLOUD_LOG_PATH = Path("data/logs/cloud_events.jsonl")


def cloud_log_event(event: str, payload: Dict[str, Any]) -> None:
    os.makedirs(CLOUD_LOG_PATH.parent, exist_ok=True)
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "payload": payload,
    }
    with open(CLOUD_LOG_PATH, "a", encoding="utf-8") as log_file:
        json.dump(record, log_file, ensure_ascii=False)
        log_file.write("\n")


class CloudLoggerService:
    """Simple logger that writes structured events to the cloud log file."""

    def info(self, message: str, payload: Dict[str, Any] | None = None) -> None:
        cloud_log_event("info", {"message": message, **(payload or {})})

    def warning(self, message: str, payload: Dict[str, Any] | None = None) -> None:
        cloud_log_event("warning", {"message": message, **(payload or {})})

    def error(self, message: str, payload: Dict[str, Any] | None = None) -> None:
        cloud_log_event("error", {"message": message, **(payload or {})})
