from __future__ import annotations

import asyncio
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict


NEURAL_LOG_PATH = "data/logs/neural_connector_log.jsonl"


@dataclass
class RepoMetadata:
    repo_id: str
    repo_name: str
    repo_type: str
    version: str
    layer: str
    capabilities: list[str]


class NeuralEventType(str, Enum):
    REFLECTIVE_SYNC = "reflective_sync"
    TELEMETRY = "telemetry"
    HEARTBEAT = "heartbeat"


class NeuralConnector:
    """
    Lightweight async connector stub for neural event propagation.
    Persists events to local log storage for observability.
    """

    def __init__(
        self, metadata: RepoMetadata, redis_url: str, channel_prefix: str = "tuyul_neural"
    ) -> None:
        self.metadata = metadata
        self.redis_url = redis_url
        self.channel_prefix = channel_prefix
        self.connected = False
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        async with self._lock:
            if self.connected:
                return
            self.connected = True
            self._write_log(
                {
                    "event": "connector_connected",
                    "channel_prefix": self.channel_prefix,
                    "redis_url": self.redis_url,
                    "metadata": asdict(self.metadata),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    async def disconnect(self) -> None:
        async with self._lock:
            if not self.connected:
                return
            self._write_log(
                {
                    "event": "connector_disconnected",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            self.connected = False

    async def publish(self, event_type: NeuralEventType, payload: Dict[str, Any]) -> None:
        if not self.connected:
            await self.connect()

        envelope = {
            "event": event_type.value,
            "channel": f"{self.channel_prefix}.{event_type.value}",
            "payload": payload,
            "metadata": asdict(self.metadata),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._write_log(envelope)

    def _write_log(self, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(NEURAL_LOG_PATH), exist_ok=True)
        with open(NEURAL_LOG_PATH, "a", encoding="utf-8") as log_file:
            json.dump(data, log_file, ensure_ascii=False)
            log_file.write("\n")
