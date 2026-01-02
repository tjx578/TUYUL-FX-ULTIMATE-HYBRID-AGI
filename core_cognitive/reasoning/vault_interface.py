"""Vault Interface – Persist AGI reasoning outputs into the knowledge vault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from data.agi.vault_sync_log import VaultSyncLog


class VaultInterface:
    """Manage storage and logging of reasoning records."""

    def __init__(self) -> None:
        self.vault_path = Path("knowledge_vault/reasoning_records")
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.sync_log = VaultSyncLog()

    def store_reasoning(self, record: Dict[str, object]) -> Dict[str, object]:
        """Persist reasoning record and log the synchronization event."""

        timestamp = str(record.get("timestamp"))
        safe_timestamp = timestamp.replace(":", "_")
        file_path = self.vault_path / f"record_{safe_timestamp}.json"
        with file_path.open("w", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2)
        self.sync_log.log_sync(1, "success")
        return {"stored": True, "path": str(file_path)}

