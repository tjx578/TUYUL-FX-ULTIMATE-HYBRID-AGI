from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


REFLECTIVE_LOG_PATH = Path("data/logs/reflective_log.jsonl")


def _configure_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def log_reflective_event(event: str, payload: Dict[str, Any]) -> None:
    os.makedirs(REFLECTIVE_LOG_PATH.parent, exist_ok=True)
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "payload": payload,
    }
    with open(REFLECTIVE_LOG_PATH, "a", encoding="utf-8") as log_file:
        json.dump(record, log_file, ensure_ascii=False)
        log_file.write("\n")


@dataclass
class ReflectiveLogger:
    name: str

    def __post_init__(self) -> None:
        self._logger = _configure_logger(self.name)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)
