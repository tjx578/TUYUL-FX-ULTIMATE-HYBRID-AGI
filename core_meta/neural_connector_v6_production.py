"""
🧠 TUYUL FX NEURAL CONNECTOR v6.0r∞
Integrasi konektivitas antar modul (Fusion–Reflective–REE–Vault)

Fungsi:
- Sinkronisasi real-time antar repo reflective intelligence
- Mendukung reflective broadcast: Fusion, FTA, REE, Vault
- Auto-register ke Quad Vault neural registry
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

import redis.asyncio as redis
from pydantic import BaseModel, Field


class NeuralEventType(str, Enum):
    """Jenis sinyal dalam jaringan TUYUL Reflective Network."""

    VAULT_UPDATE = "vault.update"
    FUSION_CYCLE_COMPLETE = "fusion.cycle.complete"
    REFLECTIVE_SYNC = "reflective.sync"
    REE_CYCLE_COMPLETE = "ree.cycle.complete"
    META_FEEDBACK = "meta.feedback"
    REQUEST_ANALYSIS = "request.analysis"
    REQUEST_EXECUTION = "request.execution"
    REQUEST_REE_UPDATE = "request.ree_update"
    REQUEST_VAULT_SYNC = "request.vault_sync"
    REPO_REGISTERED = "repo.registered"
    REPO_HEALTH_CHECK = "repo.health_check"
    REPO_OFFLINE = "repo.offline"
    ERROR_RAISED = "system.error"
    CONFIG_SYNC = "system.config_sync"


class RepoCapability(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    average_latency_ms: Optional[float] = None


class RepoMetadata(BaseModel):
    repo_id: str
    repo_name: str
    repo_type: str
    version: str
    layer: str
    capabilities: List[RepoCapability]
    status: str = "online"
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)


class NeuralEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: NeuralEventType
    source_repo_id: str
    target_repo_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    ttl: int = 300


Handler = Callable[[NeuralEvent], Union[Awaitable[Any], Any]]


class NeuralConnector:
    """Konektor neuron untuk sinkronisasi antar modul reflective AGI."""

    def __init__(
        self,
        repo_metadata: RepoMetadata,
        redis_url: str = "redis://localhost:6379",
        channel_prefix: str = "tuyul_neural",
        heartbeat_interval: int = 10,
        logger: Optional[logging.Logger] = None,
    ):
        self.meta = repo_metadata
        self.redis_url = redis_url
        self.channel_prefix = channel_prefix
        self.heartbeat_interval = heartbeat_interval
        self.logger = logger or self._setup_logger()
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.handlers: Dict[NeuralEventType, List[Handler]] = {}
        self.is_running = False
        self.tasks: List[asyncio.Task] = []

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"neural.{self.meta.repo_name}")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s | 🧠 %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    async def connect(self) -> None:
        """Connect ke jaringan neural TUYUL."""
        self.redis_client = await redis.from_url(
            self.redis_url, encoding="utf-8", decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe(
            f"{self.channel_prefix}:broadcast",
            f"{self.channel_prefix}:repo:{self.meta.repo_id}",
        )
        self.is_running = True
        await self._register_repo()
        self.tasks = [
            asyncio.create_task(self._heartbeat_loop(), name="neural-heartbeat"),
            asyncio.create_task(self._listener_loop(), name="neural-listener"),
        ]
        self.logger.info("✅ Connected: %s (%s)", self.meta.repo_name, self.meta.layer)

    async def disconnect(self) -> None:
        """Graceful disconnect."""
        if not self.is_running:
            return
        self.is_running = False
        await self._await_tasks()
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        self.logger.info("🛑 Disconnected: %s", self.meta.repo_name)

    async def publish(
        self,
        event_type: NeuralEventType,
        payload: Dict[str, Any],
        target_repo_id: Optional[str] = None,
    ) -> None:
        """Kirim event ke jaringan."""
        if not self.redis_client:
            raise RuntimeError("Redis client belum terhubung.")
        event = NeuralEvent(
            event_type=event_type,
            source_repo_id=self.meta.repo_id,
            payload=payload,
            target_repo_id=target_repo_id,
        )
        channel = (
            f"{self.channel_prefix}:broadcast"
            if not target_repo_id
            else f"{self.channel_prefix}:repo:{target_repo_id}"
        )
        await self.redis_client.publish(channel, event.model_dump_json())
        self.logger.info("📡 Published %s to %s", event_type, channel)

    def on(
        self,
        event_type: NeuralEventType,
        handler: Optional[Handler] = None,
    ) -> Callable[[Handler], Handler]:
        """Daftarkan handler event."""

        def decorator(fn: Handler) -> Handler:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(fn)
            self.logger.info("📥 Handler registered for %s", event_type)
            return fn

        if handler:
            return decorator(handler)
        return decorator

    async def _register_repo(self) -> None:
        """Daftarkan repo ke neural registry (Quad Vault awareness)."""
        if not self.redis_client:
            raise RuntimeError("Redis client belum terhubung.")
        key = f"{self.channel_prefix}:registry:{self.meta.repo_id}"
        await self.redis_client.set(
            key, self.meta.model_dump_json(), ex=self.heartbeat_interval * 5
        )
        await self.publish(
            NeuralEventType.REPO_REGISTERED,
            {"repo": self.meta.repo_name, "layer": self.meta.layer},
        )

    async def _heartbeat_loop(self) -> None:
        """Kirim heartbeat ke network."""
        while self.is_running:
            if not self.redis_client:
                self.logger.error("Redis client tidak tersedia untuk heartbeat.")
                break
            await self.redis_client.set(
                f"{self.channel_prefix}:heartbeat:{self.meta.repo_id}",
                datetime.utcnow().isoformat(),
                ex=self.heartbeat_interval * 3,
            )
            await self.publish(
                NeuralEventType.REPO_HEALTH_CHECK,
                {"repo": self.meta.repo_name, "status": "alive"},
            )
            await asyncio.sleep(self.heartbeat_interval)

    async def _listener_loop(self) -> None:
        """Terima sinyal dari jaringan TUYUL."""
        while self.is_running:
            if not self.pubsub:
                self.logger.error("PubSub tidak tersedia untuk listener.")
                break
            msg = await self.pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if msg and msg["type"] == "message":
                await self._dispatch_event(msg["data"])
            await asyncio.sleep(0.1)

    async def _dispatch_event(self, data: str) -> None:
        try:
            event = NeuralEvent.model_validate_json(data)
        except Exception as exc:
            self.logger.error("❌ Listener error: %s", exc)
            return
        if event.source_repo_id == self.meta.repo_id:
            return
        handlers = self.handlers.get(event.event_type, [])
        for handler in handlers:
            result = handler(event)
            if asyncio.iscoroutine(result):
                await result

    async def _await_tasks(self) -> None:
        if not self.tasks:
            return
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks = []
