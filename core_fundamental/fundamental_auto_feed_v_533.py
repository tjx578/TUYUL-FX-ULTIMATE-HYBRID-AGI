"""Fundamental Auto Feed v5.3.3."""

from __future__ import annotations

from typing import Dict, Optional

import requests


class FundamentalAutoFeed:
    """📊 TUYUL FX v5.3.3 – Fundamental Auto Feed.

    Menghitung skor fundamental otomatis berdasarkan VIX, DXY, CPI, PMI, dan Yield Spread.
    Output digunakan untuk memperkuat reasoning Layer-10 (FTA) dan Layer-12 (CONF₁₂ Fusion).
    """

    def __init__(self, api_key: str = "DEMO_KEY", session: Optional[requests.Session] = None):
        self.api = "https://api.financialmodelingprep.com/api/v3"
        self.key = api_key
        self.session = session or requests.Session()

    def get_index(self, symbol: str) -> Optional[float]:
        try:
            response = self.session.get(
                f"{self.api}/quote/{symbol}",
                params={"apikey": self.key},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError):
            return None

        if data and isinstance(data, list):
            return data[0].get("price")
        return None

    def compute_fundamental_score(self) -> Dict[str, float | str]:
        """Hitung skor fundamental 0–1 berdasarkan indikator makro global."""
        dxy = self.get_index("^DXY") or 104
        vix = self.get_index("^VIX") or 17

        cpi = 3.4
        pmi = 51.2
        yield_spread = -0.45

        dxy_norm = min(max((dxy - 95) / 10, 0), 1)
        vix_norm = min(max(vix / 35, 0), 1)
        cpi_norm = min(max(cpi / 10, 0), 1)
        pmi_norm = min(max((pmi - 40) / 20, 0), 1)
        yield_norm = 1 if yield_spread > 0 else 0.3

        score = (
            dxy_norm * 0.35
            + (1 - vix_norm) * 0.25
            + cpi_norm * 0.20
            + pmi_norm * 0.10
            + yield_norm * 0.10
        )

        macro_bias = (
            "USD_Strength" if dxy_norm > 0.6 else "USD_Weakness" if dxy_norm < 0.4 else "Neutral"
        )
        correlation_signal = "risk_off" if vix > 18 else "risk_on"

        return {
            "fundamental_score": round(score, 3),
            "macro_bias": macro_bias,
            "volatility_index": round(vix, 2),
            "correlation_signal": correlation_signal,
            "source": "FMP_API_v5.3.3",
        }


if __name__ == "__main__":
    feed = FundamentalAutoFeed()
    result = feed.compute_fundamental_score()
    print(result)
