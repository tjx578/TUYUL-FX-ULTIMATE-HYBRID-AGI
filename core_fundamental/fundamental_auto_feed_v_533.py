"""Lightweight synthetic fundamental feed for TUYUL FX v5.3.3."""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class FundamentalSnapshot:
    """Container for macro indicators used to derive a fundamental score."""

    dxy: float
    vix: float
    cpi: float
    pmi: float
    yield_spread: float


class FundamentalAutoFeed:
    """Generate a normalized fundamental snapshot for downstream consumers."""

    def __init__(self, api_key: str, seed: Optional[int] = None) -> None:
        self.api_key = api_key
        self.random = random.Random(seed or int(time.time()))

    def compute_fundamental_score(self) -> Dict[str, object]:
        snapshot = self._fetch_snapshot()
        dxy_score = self._normalize(snapshot.dxy, 98.0, 104.0)
        vix_score = self._normalize(snapshot.vix, 12.0, 35.0, invert=True)
        cpi_score = self._normalize(snapshot.cpi, 1.5, 5.0, invert=True)
        pmi_score = self._normalize(snapshot.pmi, 40.0, 60.0)
        spread_score = self._normalize(snapshot.yield_spread, -1.0, 2.0)

        raw_scores = [dxy_score, vix_score, cpi_score, pmi_score, spread_score]
        fundamental_score = round(sum(raw_scores) / len(raw_scores), 3)
        macro_bias = self._macro_bias(fundamental_score, snapshot)
        correlation_signal = self._correlation_signal(snapshot)

        return {
            "fundamental_score": fundamental_score,
            "macro_bias": macro_bias,
            "volatility_index": round(snapshot.vix, 3),
            "correlation_signal": correlation_signal,
            "source": "fundamental_auto_feed_v5.3.3",
            "timestamp": int(time.time()),
            "snapshot": snapshot.__dict__,
        }

    def _fetch_snapshot(self) -> FundamentalSnapshot:
        cycle = math.sin(time.time() / 1800.0)
        return FundamentalSnapshot(
            dxy=self._bounded(103.2 + cycle, 0.8, 98.0, 105.0),
            vix=self._bounded(17.5 - cycle, 2.5, 12.0, 35.0),
            cpi=self._bounded(3.1 + cycle, 0.7, 1.5, 6.0),
            pmi=self._bounded(51.0 + cycle * 2.0, 3.0, 40.0, 60.0),
            yield_spread=self._bounded(0.85 + cycle * 0.3, 0.45, -1.0, 2.0),
        )

    def _bounded(self, base: float, width: float, lower: float, upper: float) -> float:
        drift = self.random.uniform(-width, width)
        value = max(min(base + drift, upper), lower)
        return round(value, 3)

    def _normalize(
        self, value: float, lower: float, upper: float, invert: bool = False
    ) -> float:
        clamped = max(min(value, upper), lower)
        span = upper - lower
        if span == 0:
            return 0.0
        scaled = (clamped - lower) / span
        return 1.0 - scaled if invert else scaled

    def _macro_bias(self, score: float, snapshot: FundamentalSnapshot) -> str:
        if score >= 0.65 and snapshot.yield_spread >= 0:
            return "USD_Strength"
        if score <= 0.35 or snapshot.yield_spread < 0:
            return "USD_Weakness"
        return "Neutral"

    def _correlation_signal(self, snapshot: FundamentalSnapshot) -> str:
        if snapshot.vix < 18.0 and snapshot.pmi >= 50.0:
            return "risk_on"
        if snapshot.vix > 25.0 or snapshot.pmi < 48.0:
            return "risk_off"
        return "mixed"
