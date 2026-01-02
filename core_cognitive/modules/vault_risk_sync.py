from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class VaultRiskSync:
    """Persist calculated risk profiles to the vault for later calibration."""

    def __init__(self, *, vault_path: str | Path = "data/vault/risk_logs") -> None:
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)

    def save(self, pair: str, payload: dict[str, Any]) -> str:
        if not pair:
            raise ValueError("Pair symbol cannot be empty")

        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        normalized_pair = pair.replace("/", "").replace(" ", "").upper()
        file_path = self.vault_path / f"{normalized_pair}_{timestamp}.json"

        document = dict(payload)
        document["pair"] = pair
        document["timestamp"] = timestamp

        try:
            file_path.write_text(json.dumps(document, indent=2), encoding="utf-8")
        except OSError as exc:
            raise RuntimeError("Unable to persist vault risk log") from exc

        return str(file_path)
