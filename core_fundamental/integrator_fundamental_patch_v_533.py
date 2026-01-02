"""
🌐 TUYUL FX ULTIMATE — Fundamental Patch Integrator v5.3.3+
Bridges raw fundamental feeds → normalized FTA-compatible structure.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Tuple

import numpy as np

from server_api.services.cloud_logger_service import cloud_log_event
from core_reflective.reflective_logger import log_reflective_event
from core_meta.neural_connector_v6_production import (
    NeuralConnector,
    NeuralEventType,
    RepoMetadata,
)


RAW_FEED_PATH = Path("core_fundamental/logs/fundamental_feed_log.json")
PATCHED_PATH = Path("core_fundamental/logs/fundamental_patch_normalized.jsonl")
OUTLOOK_CACHE_PATH = Path("core_fundamental/logs/weekly_outlook_cache.json")
OUTLOOK_SYNC_PATH = Path("core_fundamental/news/weekly_outlook_sync.py")
EVENT_MATRIX_PATH = Path("core_fundamental/news/event_risk_matrix.json")
KNOWLEDGEBASE_PATH = Path("core_fundamental/knowledgebase/fundamental_knowledgebase.md")


@dataclass
class NormalizedFundamentalBlock:
    timestamp: str
    fundamental_sentiment: float
    macro_bias: float
    risk_tone: float
    volatility_factor: float
    news_impact: float
    weekly_bias: float
    sample_size: int
    sources: Mapping[str, bool] = field(default_factory=dict)
    context: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "fundamental_sentiment": self.fundamental_sentiment,
            "macro_bias": self.macro_bias,
            "risk_tone": self.risk_tone,
            "volatility_factor": self.volatility_factor,
            "news_impact": self.news_impact,
            "weekly_bias": self.weekly_bias,
            "sample_size": self.sample_size,
            "sources": dict(self.sources),
            "context": dict(self.context),
        }


class FundamentalPatchIntegrator:
    """Normalize raw fundamental data & align to FTA schema."""

    def __init__(self, redis_url: str = "redis://localhost:6379") -> None:
        self.neural = NeuralConnector(
            RepoMetadata(
                repo_id="fundamental-patch-001",
                repo_name="Fundamental Patch Integrator",
                repo_type="data_normalizer",
                version="5.3.3+",
                layer="L6",
                capabilities=[],
            ),
            redis_url=redis_url,
            channel_prefix="tuyul_neural",
        )

    async def start(self) -> None:
        await self.neural.connect()

    async def stop(self) -> None:
        await self.neural.disconnect()

    def normalize_feed(
        self,
        feed_entries: List[Mapping[str, Any]],
        weekly_outlook: Mapping[str, Any],
        event_matrix: List[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        base_sentiment, volatility = self._score_feed(feed_entries)
        weekly_bias, weekly_summary = self._score_weekly_outlook(weekly_outlook)
        news_impact = self._score_event_risk(event_matrix)

        if feed_entries:
            sentiment_anchor = base_sentiment
        else:
            sentiment_anchor = weekly_bias

        macro_bias = float(
            np.tanh(
                (sentiment_anchor * 1.5) + (weekly_bias * 0.35) + (news_impact * 0.25)
            )
        )
        risk_baseline = volatility if volatility > 0 else max(0.1, news_impact)
        risk_tone = float(np.clip(risk_baseline * sentiment_anchor, -1.0, 1.0))
        volatility_factor = float(np.clip((volatility + news_impact) / 2, 0.0, 1.0))

        knowledgebase_context = self._knowledgebase_digest()
        patch_block = NormalizedFundamentalBlock(
            timestamp=datetime.utcnow().isoformat(),
            fundamental_sentiment=round(float(sentiment_anchor), 4),
            macro_bias=round(float(macro_bias), 4),
            risk_tone=round(risk_tone, 4),
            volatility_factor=round(volatility_factor, 4),
            news_impact=round(news_impact, 4),
            weekly_bias=round(float(weekly_bias), 4),
            sample_size=len(feed_entries),
            sources={
                "auto_feed": bool(feed_entries),
                "weekly_outlook": bool(weekly_outlook),
                "event_risk_matrix": bool(event_matrix),
            },
            context={
                "weekly_outlook_summary": weekly_summary,
                "knowledgebase": knowledgebase_context,
                "outlook_sync": str(OUTLOOK_SYNC_PATH),
            },
        )

        self._save_patch(patch_block.as_dict())
        log_reflective_event("FUNDAMENTAL_PATCH_NORMALIZED", patch_block.as_dict())
        cloud_log_event("fundamental.patch", patch_block.as_dict())
        return patch_block.as_dict()

    async def send_to_fta(self, patch_block: Mapping[str, Any]) -> None:
        """Send normalized patch block to FTA Integration Engine."""

        if not patch_block or "fundamental_sentiment" not in patch_block:
            return

        payload = {
            "source": "fundamental_patch",
            "fundamental_sentiment": patch_block["fundamental_sentiment"],
            "macro_bias": patch_block["macro_bias"],
            "risk_tone": patch_block["risk_tone"],
            "news_impact": patch_block.get("news_impact", 0.0),
            "weekly_bias": patch_block.get("weekly_bias", 0.0),
            "timestamp": patch_block["timestamp"],
        }

        await self.neural.publish(
            event_type=NeuralEventType.REQUEST_ANALYSIS, payload=payload
        )
        log_reflective_event("FUNDAMENTAL_PATCH_BROADCAST", payload)
        cloud_log_event("fundamental.patch_broadcast", payload)

    def build_and_normalize(self) -> Dict[str, Any]:
        feed_entries = self._load_raw_feed()
        weekly_outlook = self._load_weekly_outlook()
        event_matrix = self._load_event_risk_matrix()
        return self.normalize_feed(feed_entries, weekly_outlook, event_matrix)

    @staticmethod
    def _load_raw_feed() -> List[Mapping[str, Any]]:
        if not RAW_FEED_PATH.exists():
            return []
        try:
            data = json.loads(RAW_FEED_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []

    @staticmethod
    def _load_weekly_outlook() -> Dict[str, Any]:
        if not OUTLOOK_CACHE_PATH.exists():
            return {}
        try:
            data = json.loads(OUTLOOK_CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        if isinstance(data, dict):
            return data
        return {}

    @staticmethod
    def _load_event_risk_matrix() -> List[Mapping[str, Any]]:
        if not EVENT_MATRIX_PATH.exists():
            return []
        try:
            data = json.loads(EVENT_MATRIX_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if isinstance(data, list):
            return data
        return []

    @staticmethod
    def _score_feed(feed_entries: List[Mapping[str, Any]]) -> Tuple[float, float]:
        if not feed_entries:
            return 0.0, 0.0
        sentiments = [float(entry.get("sentiment", 0.0)) for entry in feed_entries]
        impacts = [float(entry.get("impact", 1.0)) for entry in feed_entries]
        weights = np.array(impacts) / (np.sum(impacts) or 1.0)
        weighted_sentiment = float(np.dot(sentiments, weights))
        volatility_factor = float(np.clip(np.mean(impacts) / 3.0, 0.0, 1.0))
        return weighted_sentiment, volatility_factor

    @staticmethod
    def _score_weekly_outlook(outlook: Mapping[str, Any]) -> Tuple[float, str]:
        if not outlook:
            return 0.0, ""
        bias = outlook.get("bias_score")
        summary = outlook.get("summary") or outlook.get("headline") or ""
        if bias is None:
            bias = outlook.get("bias") or 0.0
        try:
            bias_value = float(bias)
        except (TypeError, ValueError):
            bias_value = 0.0
        bias_value = float(np.clip(bias_value, -1.0, 1.0))
        summary_text = summary if isinstance(summary, str) else ""
        return bias_value, summary_text

    @staticmethod
    def _score_event_risk(events: List[Mapping[str, Any]]) -> float:
        if not events:
            return 0.0
        total = 0.0
        weight = 0.0
        for event in events:
            try:
                impact = float(event.get("impact", 0.0))
                probability = float(event.get("probability", 1.0))
            except (TypeError, ValueError):
                continue
            total += impact * probability
            weight += probability
        if weight == 0:
            return 0.0
        normalized = np.clip((total / weight) / 3.0, 0.0, 1.0)
        return float(normalized)

    @staticmethod
    def _knowledgebase_digest() -> Mapping[str, Any]:
        if not KNOWLEDGEBASE_PATH.exists():
            return {}
        try:
            text = KNOWLEDGEBASE_PATH.read_text(encoding="utf-8")
        except OSError:
            return {}
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        summary = " ".join(lines[:3])[:320]
        return {
            "source": str(KNOWLEDGEBASE_PATH),
            "last_updated": datetime.utcfromtimestamp(
                KNOWLEDGEBASE_PATH.stat().st_mtime
            ).isoformat(),
            "summary": summary,
        }

    @staticmethod
    def _save_patch(data: Mapping[str, Any]) -> None:
        PATCHED_PATH.parent.mkdir(parents=True, exist_ok=True)
        with PATCHED_PATH.open("a", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
            file.write("\n")


if __name__ == "__main__":
    import asyncio

    integrator = FundamentalPatchIntegrator()

    async def run_demo() -> None:
        await integrator.start()
        patch_block = integrator.build_and_normalize()
        await integrator.send_to_fta(patch_block)
        print("✅ Normalized Fundamental Patch Block:")
        print(json.dumps(patch_block, indent=2))
        await integrator.stop()

    asyncio.run(run_demo())
