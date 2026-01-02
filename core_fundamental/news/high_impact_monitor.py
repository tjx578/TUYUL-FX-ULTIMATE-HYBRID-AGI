"""
high_impact_monitor.py – TUYUL FX AGI v5.3.3+
=============================================

Memantau jadwal berita berdampak tinggi (high-impact news events) seperti CPI,
NFP, GDP, dan keputusan suku bunga dari sumber ekonomi global.
Memberikan skor risiko reflektif yang mempengaruhi modul Adaptive Risk dan
Fusion Layer.

Author : TUYUL KARTEL DEV TEAM
Version: v5.3.3+
"""

from __future__ import annotations

import datetime
import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class HighImpactMonitor:
    """📰 Monitor berita ekonomi berdampak tinggi dengan evaluasi reflektif."""

    def __init__(self, api_key: str = "DEMO_KEY") -> None:
        self.api_base = "https://financialmodelingprep.com/api/v3"
        self.api_key = api_key
        self.calendar_endpoint = f"{self.api_base}/economic_calendar"

    def fetch_calendar(self, days_ahead: int = 2) -> List[Dict[str, Any]]:
        """Ambil data kalender ekonomi global untuk beberapa hari ke depan."""
        horizon = max(days_ahead, 0)
        now = datetime.datetime.utcnow()
        window_end = now + datetime.timedelta(days=horizon)

        try:
            response = requests.get(
                self.calendar_endpoint,
                params={"apikey": self.api_key},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("Gagal mengambil data kalender ekonomi: %s", exc)
            return []
        except ValueError as exc:
            logger.error("Gagal mem-parsing respons kalender ekonomi: %s", exc)
            return []

        upcoming_events: List[Dict[str, Any]] = []
        for item in data:
            event_time = self._parse_datetime(item.get("date"))
            if event_time and now <= event_time <= window_end:
                upcoming_events.append(item)

        return upcoming_events

    def calculate_impact_score(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Hitung skor risiko reflektif berdasarkan jumlah dan jenis event berdampak tinggi."""
        high_impact_events = [
            event for event in events if event.get("impact", "").lower() == "high"
        ]
        medium_impact_events = [
            event for event in events if event.get("impact", "").lower() == "medium"
        ]

        total_high = len(high_impact_events)
        total_medium = len(medium_impact_events)
        risk_index = min(1.0, (total_high * 0.07) + (total_medium * 0.03))

        if risk_index >= 0.7:
            risk_mode = "HIGH_RISK"
        elif risk_index >= 0.4:
            risk_mode = "CAUTION"
        else:
            risk_mode = "NORMAL"

        return {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "high_impact_count": total_high,
            "medium_impact_count": total_medium,
            "risk_index": round(risk_index, 3),
            "risk_mode": risk_mode,
            "source": "FMP_API_v5.3.3",
        }

    def get_high_impact_summary(self, days_ahead: int = 2) -> Dict[str, Any]:
        """Ambil ringkasan risiko berdasarkan kalender ekonomi."""
        events = self.fetch_calendar(days_ahead)
        return self.calculate_impact_score(events)

    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime.datetime]:
        if not date_str:
            return None

        cleaned = date_str.replace("Z", "")
        try:
            return datetime.datetime.fromisoformat(cleaned)
        except ValueError:
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = HighImpactMonitor()
    result = monitor.get_high_impact_summary(days_ahead=3)
    print("📰 TUYUL FX – High Impact News Monitor")
    print(result)
