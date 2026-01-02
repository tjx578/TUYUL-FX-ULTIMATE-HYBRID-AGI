"""Integrator patch linking Fundamental Auto Feed with Proto AGI Engine.

This module injects the fundamental auto-feed signal directly into the Proto
AGI Engine (Layer-12) run pipeline, ensuring macro awareness is included
whenever trading directives are produced.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Mapping, MutableMapping, Sequence

from core_fundamental.fundamental_auto_feed_v_533 import FundamentalAutoFeed
from core_orchestrator.proto_agi_engine_v533 import AGIReasoningOutput, ProtoAGIEngine


def _last_numeric(values: Sequence[Any] | None) -> float | None:
    if not values:
        return None
    try:
        return float(values[-1])
    except (TypeError, ValueError):
        return None


def _min_numeric(values: Sequence[Any] | None) -> float | None:
    if not values:
        return None
    numeric_values = []
    for value in values:
        try:
            numeric_values.append(float(value))
        except (TypeError, ValueError):
            continue
    return min(numeric_values) if numeric_values else None


def _average_numeric(values: Sequence[Any] | None) -> float | None:
    if not values:
        return None
    numeric_values = []
    for value in values:
        try:
            numeric_values.append(float(value))
        except (TypeError, ValueError):
            continue
    if not numeric_values:
        return None
    return sum(numeric_values) / len(numeric_values)


class TuyulGPTBridgeWithFundamentals:
    """Integrator Patch v5.3.3 – Fundamental + AGI Fusion.

    Bridge that enriches market directives with macro fundamentals before
    executing the Proto AGI Engine. Every request is augmented with a
    ``fundamental_score`` that the downstream Layer-12 pipeline can consume.
    """

    def __init__(
        self,
        engine: ProtoAGIEngine | None = None,
        feed: FundamentalAutoFeed | None = None,
    ) -> None:
        self.engine = engine or ProtoAGIEngine()
        self.fundamental_feed = feed or FundamentalAutoFeed()

    def handle_request(
        self,
        pair: str,
        timeframe: str,
        market_data: Mapping[str, Any],
    ) -> Dict[str, Any]:
        fundamentals = self.fundamental_feed.compute_fundamental_score()

        augmented_market: MutableMapping[str, Any] = dict(market_data)
        augmented_market["fundamental_score"] = fundamentals["fundamental_score"]

        entry_price = _last_numeric(augmented_market.get("closes")) or _last_numeric(
            augmented_market.get("prices")
        )
        stop_loss = _min_numeric(augmented_market.get("lows"))
        confidence = float(fundamentals.get("fundamental_score", 0.75)) or 0.75
        wlwci = _average_numeric(augmented_market.get("returns"))

        directive = AGIReasoningOutput(
            pair=pair,
            confidence=confidence,
            mode="normal",
            entry_price=entry_price if entry_price is not None else 0.0,
            stop_loss=stop_loss if stop_loss is not None else 0.0,
            twms_payload={
                "timeframe": timeframe,
                "bias": augmented_market.get("bias", "neutral"),
                "fundamental_score": fundamentals["fundamental_score"],
                "macro_bias": fundamentals.get("macro_bias"),
                "volatility_index": fundamentals.get("volatility_index"),
            },
            wlwci=wlwci,
            final_report_data={
                "timeframe": timeframe,
                "prices": augmented_market.get("prices"),
                "highs": augmented_market.get("highs"),
                "lows": augmented_market.get("lows"),
                "closes": augmented_market.get("closes"),
                "volumes": augmented_market.get("volumes"),
                "returns": augmented_market.get("returns"),
                "fundamental_score": fundamentals["fundamental_score"],
                "fundamental_context": fundamentals,
            },
        )

        result = self.engine.run(directive)

        decision_payload = result.decision.as_dict()
        diagnostics = result.diagnostics

        fusion_trace = {
            "fusion_layers": list(diagnostics.keys()),
            "risk_modifier": diagnostics.get("mtf_summary", {}).get("risk_modifier"),
        }

        return {
            "pair": pair,
            "timeframe": timeframe,
            "timestamp": datetime.utcnow().isoformat(),
            "layer12": decision_payload,
            "fusion_trace": fusion_trace,
            "fundamental_context": fundamentals,
        }


if __name__ == "__main__":
    dummy_data = {
        "prices": [1.105, 1.107, 1.109],
        "highs": [1.110, 1.112, 1.113],
        "lows": [1.100, 1.103, 1.105],
        "closes": [1.107, 1.109, 1.111],
        "volumes": [1000, 1200, 900],
        "returns": [0.0012, 0.0010, 0.0008],
    }

    bridge = TuyulGPTBridgeWithFundamentals()
    output = bridge.handle_request("XAUUSD", "H1", dummy_data)
    print(output)
