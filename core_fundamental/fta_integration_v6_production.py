from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict

import numpy as np

from core_meta.neural_connector_v6_production import (
    NeuralConnector,
    NeuralEventType,
    RepoMetadata,
)
from core_reflective.reflective_logger import log_reflective_event
from server_api.services.cloud_logger_service import cloud_log_event


FTA_LOG_PATH = "data/logs/fta_log.jsonl"


@dataclass
class AlignmentResult:
    timestamp: str
    alignment_index: float
    confidence: float
    direction: str
    regime_state: str
    fundamental_component: float
    technical_component: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FTAIntegrationEngine:
    """Fundamental–Technical Alignment Engine (Layer 7–10)."""

    def __init__(self, redis_url: str = "redis://localhost:6379") -> None:
        self.neural = NeuralConnector(
            RepoMetadata(
                repo_id="fta-integrator-001",
                repo_name="Fundamental–Technical Alignment",
                repo_type="fta_bridge",
                version="6.0r∞",
                layer="L7–10",
                capabilities=[],
            ),
            redis_url=redis_url,
            channel_prefix="tuyul_neural",
        )

    async def start(self) -> None:
        await self.neural.connect()

    async def stop(self) -> None:
        await self.neural.disconnect()

    def compute_alignment(
        self,
        fundamental_sentiment: float,
        news_impact: float,
        macro_bias: float,
        fusion_bias: float,
        twms_strength: float,
        reflective_bias: float,
    ) -> Dict[str, Any]:
        """Compute alignment score using normalized fundamental and technical inputs."""

        fundamental_component = self._calculate_fundamental_component(
            fundamental_sentiment=fundamental_sentiment,
            news_impact=news_impact,
            macro_bias=macro_bias,
        )
        technical_component = self._calculate_technical_component(
            fusion_bias=fusion_bias,
            twms_strength=twms_strength,
            reflective_bias=reflective_bias,
        )

        alignment_score = np.tanh((fundamental_component + technical_component) / 1.5)
        confidence = float(np.clip(abs(alignment_score), 0.0, 1.0))

        regime = self._derive_regime(confidence)
        direction = self._derive_direction(alignment_score)

        result = AlignmentResult(
            timestamp=datetime.utcnow().isoformat(),
            alignment_index=round(float(alignment_score), 4),
            confidence=round(confidence, 3),
            direction=direction,
            regime_state=regime,
            fundamental_component=round(float(fundamental_component), 4),
            technical_component=round(float(technical_component), 4),
        )

        self._save_log(result)
        log_reflective_event("FTA_ALIGNMENT", result.to_dict())
        cloud_log_event("fta.integration", result.to_dict())

        return result.to_dict()

    async def broadcast_alignment(self, result: Dict[str, Any]) -> None:
        """Broadcast alignment result to neural layer for reflective sync."""

        payload = {
            "alignment_index": result["alignment_index"],
            "confidence": result["confidence"],
            "regime_state": result["regime_state"],
            "direction": result["direction"],
            "timestamp": result["timestamp"],
        }

        await self.neural.publish(
            event_type=NeuralEventType.REFLECTIVE_SYNC, payload=payload
        )

        log_reflective_event("FTA_BROADCAST", payload)
        cloud_log_event("fta.broadcast", payload)

    def _calculate_fundamental_component(
        self, fundamental_sentiment: float, news_impact: float, macro_bias: float
    ) -> float:
        sentiment = self._normalize_input(fundamental_sentiment)
        impact = self._normalize_input(news_impact)
        bias = self._normalize_input(macro_bias)
        return (sentiment * 0.4) + (impact * 0.2) + (bias * 0.4)

    def _calculate_technical_component(
        self, fusion_bias: float, twms_strength: float, reflective_bias: float
    ) -> float:
        fusion = self._normalize_input(fusion_bias)
        twms = self._normalize_input(twms_strength)
        reflective = self._normalize_input(reflective_bias)
        return (fusion * 0.5) + (twms * 0.3) + (reflective * 0.2)

    @staticmethod
    def _derive_direction(alignment_score: float) -> str:
        if alignment_score > 0.2:
            return "BULLISH"
        if alignment_score < -0.2:
            return "BEARISH"
        return "NEUTRAL"

    @staticmethod
    def _derive_regime(confidence: float) -> str:
        if confidence > 0.8:
            return "EXPANSION"
        if confidence < 0.4:
            return "COMPRESSION"
        return "NEUTRAL"

    @staticmethod
    def _normalize_input(value: float) -> float:
        return float(np.clip(value, -1.0, 1.0))

    @staticmethod
    def _save_log(data: AlignmentResult) -> None:
        os.makedirs(os.path.dirname(FTA_LOG_PATH), exist_ok=True)
        with open(FTA_LOG_PATH, "a", encoding="utf-8") as log_file:
            json.dump(data.to_dict(), log_file, ensure_ascii=False)
            log_file.write("\n")


if __name__ == "__main__":
    import asyncio

    engine = FTAIntegrationEngine()

    async def run_demo() -> None:
        await engine.start()
        result = engine.compute_alignment(
            fundamental_sentiment=0.65,
            news_impact=0.5,
            macro_bias=0.8,
            fusion_bias=0.7,
            twms_strength=0.85,
            reflective_bias=0.6,
        )
        await engine.broadcast_alignment(result)
        print("FTA Result:", json.dumps(result, indent=2))
        await engine.stop()

    asyncio.run(run_demo())
