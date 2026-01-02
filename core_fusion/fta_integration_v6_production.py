from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


BRIDGE_LOG_PATH = Path("data/logs/layer12_fusion_bridge.jsonl")


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _safe_mean(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    return sum(items) / len(items)


@dataclass
class FusionFundamentalResult:
    pair: str
    timeframe: str
    timestamp: str
    fusion_confidence: float
    bias_direction: str
    coherence_score: float
    fundamental_score: float
    macro_bias: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pair": self.pair,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp,
            "fundamental_context": {
                "fundamental_score": self.fundamental_score,
                "macro_bias": self.macro_bias,
            },
            "layer12": {
                "fusion_confidence": self.fusion_confidence,
                "bias_direction": self.bias_direction,
                "coherence_score": self.coherence_score,
            },
        }


class TuyulGPTBridgeWithFundamentals:
    """
    Layer-12.5 fusion bridge that enriches AGI reasoning with fundamental context.
    """

    def __init__(self, log_path: Path = BRIDGE_LOG_PATH) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def handle_request(
        self, pair: str, timeframe: str, market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        price_change = self._price_change(market_data.get("closes", []))
        bias = self._derive_bias(price_change)
        fundamental_score = self._fundamental_score(
            returns=market_data.get("returns", []),
            volumes=market_data.get("volumes", []),
            price_change=price_change,
        )
        fusion_confidence = self._fusion_confidence(
            fundamental_score=fundamental_score,
            returns=market_data.get("returns", []),
        )
        coherence = self._coherence_score(fusion_confidence, fundamental_score)
        macro_bias = self._macro_bias_hint(fundamental_score, bias)

        result = FusionFundamentalResult(
            pair=pair,
            timeframe=timeframe,
            timestamp=timestamp,
            fusion_confidence=fusion_confidence,
            bias_direction=bias,
            coherence_score=coherence,
            fundamental_score=fundamental_score,
            macro_bias=macro_bias,
        )

        self._log_result(result)
        return result.to_dict()

    @staticmethod
    def _price_change(closes: List[float]) -> float:
        if len(closes) < 2:
            return 0.0
        start, end = closes[0], closes[-1]
        if start == 0:
            return 0.0
        return (end - start) / start

    @staticmethod
    def _derive_bias(price_change: float) -> str:
        if price_change > 0.0025:
            return "BULLISH"
        if price_change < -0.0025:
            return "BEARISH"
        return "NEUTRAL"

    @staticmethod
    def _fundamental_score(
        returns: List[float], volumes: List[float], price_change: float
    ) -> float:
        momentum = _safe_mean(returns)
        volume_trend = 0.0
        if len(volumes) >= 2 and volumes[0] != 0:
            volume_trend = (volumes[-1] - volumes[0]) / volumes[0]
        sentiment = 0.55 + (momentum * 4.5) + (price_change * 3.0)
        liquidity = 0.5 + volume_trend * 0.25
        return round(_clamp((sentiment * 0.65) + (liquidity * 0.35)), 3)

    @staticmethod
    def _fusion_confidence(
        fundamental_score: float, returns: List[float]
    ) -> float:
        stability = 1.0 - min(abs(_safe_mean(returns)) * 25, 0.35)
        confidence = (fundamental_score * 0.7) + (stability * 0.3)
        return round(_clamp(confidence), 3)

    @staticmethod
    def _coherence_score(fusion_confidence: float, fundamental_score: float) -> float:
        cohesion = 0.5 + (fusion_confidence - 0.5) * 0.6
        cohesion += (fundamental_score - 0.5) * 0.3
        return round(_clamp(cohesion), 3)

    @staticmethod
    def _macro_bias_hint(fundamental_score: float, bias: str) -> str:
        if fundamental_score > 0.7 and bias == "BULLISH":
            return "USD_Weakness"
        if fundamental_score > 0.7 and bias == "BEARISH":
            return "USD_Strength"
        return "Neutral_Macro"

    def _log_result(self, result: FusionFundamentalResult) -> None:
        with open(self.log_path, "a", encoding="utf-8") as handle:
            json.dump(result.to_dict(), handle, ensure_ascii=False)
            handle.write("\n")
