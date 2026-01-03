from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict


class CloudLoggerService:
    """Reflective logging fan-out to local vault logs and optional cloud sync."""

    def __init__(self) -> None:
        self.local_log_path = Path("data/logs/reflective_system_log.json")
        self.cycle_log_path = Path("data/logs/reflective_cycle_log.json")
        self.meta_log_path = Path("data/logs/reflective_evolution_log.json")
        self.cloud_log_path = Path("data/logs/cloud_events.jsonl")
        self.journal_dir = Path("quad_vaults/journal_vault/session_logs")
        self.enabled_cloud_sync = True

    # 🧩 1️⃣ Catat Informasi Reflektif
    def info(self, message: str, payload: Dict[str, Any] | None = None) -> None:
        self._write_local_log("INFO", message, payload)

    # 🧩 2️⃣ Catat Peringatan
    def warn(self, message: str, payload: Dict[str, Any] | None = None) -> None:
        self._write_local_log("WARNING", message, payload)

    # 🧩 3️⃣ Catat Kesalahan
    def error(self, message: str, payload: Dict[str, Any] | None = None) -> None:
        self._write_local_log("ERROR", message, payload)

    # 🧩 4️⃣ Catat Siklus Reflektif
    def log_cycle(self, cycle_result: Dict[str, Any]) -> None:
        self._append_json(self.cycle_log_path, cycle_result)
        self._mirror_to_vault("cycle", cycle_result)

    # 🧩 5️⃣ Catat Evolusi Meta Reflektif
    def log_meta_evolution(self, evolution_result: Dict[str, Any]) -> None:
        self._append_json(self.meta_log_path, evolution_result)
        if self.enabled_cloud_sync:
            self._append_json(self.cloud_log_path, {"event": "meta", "data": evolution_result})

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------
    def _write_local_log(self, level: str, message: str, payload: Dict[str, Any] | None = None) -> None:
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "message": message,
            "payload": payload or {},
        }
        self._append_json(self.local_log_path, record)
        self._mirror_to_vault("log", record)
        if self.enabled_cloud_sync:
            self._append_json(self.cloud_log_path, {"event": level.lower(), "data": record})

    def _mirror_to_vault(self, category: str, entry: Dict[str, Any]) -> None:
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        daily = self.journal_dir / f"reflective_log_{date.today().strftime('%Y%m%d')}.json"
        vault_entry = {"category": category, **entry}
        self._append_json(daily, vault_entry)

    def _append_json(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as log_file:
            json.dump(data, log_file)
            log_file.write("\n")


# Runtime helper
cloud_logger_service = CloudLoggerService()
