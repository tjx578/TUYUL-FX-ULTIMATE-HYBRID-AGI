"""High Impact Monitor – TUYUL FX AGI v5.3.3+."""
"""
high_impact_monitor.py – TUYUL FX AGI v5.3.3+

Memantau jadwal berita berdampak tinggi (high-impact news events) seperti CPI,
NFP, GDP, dan keputusan suku bunga dari sumber ekonomi global.
Memberikan skor risiko reflektif yang mempengaruhi modul Adaptive Risk dan
Fusion Layer.

Author : TUYUL KARTEL DEV TEAM
Version: v5.3.3+
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Sequence

import requests


class HighImpactMonitor:
    """📡 Memantau event ekonomi berdampak tinggi dan menghitung indeks risiko mingguan."""

    def __init__(
        self, api_key: str = "DEMO_KEY", session: Optional[requests.Session] = None
    ):
        self.api_key = api_key
        self.session = session or requests.Session()

    def get_high_impact_summary(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Ringkasan risiko berita global.

        Berorientasi pada stabilitas: jika API gagal, fallback ke jadwal statis agar tetap
        deterministik.
        """
        events = self._fetch_calendar(days_ahead=days_ahead)
        risk_index = self._compute_risk_index(events)
        risk_mode = self._resolve_risk_mode(risk_index)

        return {
            "as_of": datetime.datetime.utcnow().isoformat(),
            "days_ahead": days_ahead,
            "risk_index": round(risk_index, 2),
            "risk_mode": risk_mode,
            "events": events,
            "source": "TUYUL_HIM_v5.3.3",
        }

    def _fetch_calendar(self, days_ahead: int) -> List[Dict[str, Any]]:
        """Ambil jadwal event; fallback ke sampel lokal jika API gagal."""
        calendar: List[Dict[str, Any]] = []

        try:
            response = self.session.get(
                "https://api.financialmodelingprep.com/api/v3/economic_calendar",
                params={
                    "apikey": self.api_key,
                    "from": datetime.date.today(),
                    "to": datetime.date.today(),
                },
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
            calendar = self._normalize_events(data, days_ahead=days_ahead)
        except (requests.RequestException, ValueError):
            calendar = self._fallback_events()

        if not calendar:
            calendar = self._fallback_events()
        return calendar

    def _normalize_events(
        self, payload: Sequence[Dict[str, Any]], days_ahead: int
    ) -> List[Dict[str, Any]]:
        end_date = datetime.date.today() + datetime.timedelta(days=days_ahead)
        events: List[Dict[str, Any]] = []
        for item in payload:
            try:
                event_date = datetime.date.fromisoformat(item.get("date", ""))
            except ValueError:
                continue
            if event_date > end_date:
                continue
            impact = item.get("impact", "").lower() or "medium"
            events.append(
                {
                    "title": item.get("event", "Unknown"),
                    "currency": item.get("country", "GLB"),
                    "impact": impact,
                    "forecast": item.get("forecast"),
                    "previous": item.get("previous"),
                }
            )
        return events

    def _fallback_events(self) -> List[Dict[str, Any]]:
        """Fallback deterministik agar pipeline tetap berjalan."""
        return [
            {
                "title": "US CPI YoY",
                "currency": "USD",
                "impact": "high",
                "forecast": 3.2,
                "previous": 3.4,
            },
            {
                "title": "ECB Rate Decision",
                "currency": "EUR",
                "impact": "high",
                "forecast": 4.5,
                "previous": 4.5,
            },
            {
                "title": "US Initial Jobless Claims",
                "currency": "USD",
                "impact": "medium",
                "forecast": 222,
                "previous": 230,
            },
            {
                "title": "China PMI Manufacturing",
                "currency": "CNY",
                "impact": "medium",
                "forecast": 50.1,
                "previous": 49.9,
            },
        ]

    def _compute_risk_index(self, events: Sequence[Dict[str, Any]]) -> float:
        if not events:
            return 0.3

        weights = {"high": 1.0, "medium": 0.65, "low": 0.35}
        weighted = [weights.get(event.get("impact", "low"), 0.35) for event in events]
        avg_weight = sum(weighted) / len(weighted)

        usd_events = sum(1 for event in events if event.get("currency") == "USD")
        usd_bias = min(usd_events / max(len(events), 1), 1)

        risk_index = min(avg_weight * 0.7 + usd_bias * 0.3, 1)
        return risk_index

    def _resolve_risk_mode(self, index: float) -> str:
        if index >= 0.75:
            return "ALERT"
        if index >= 0.6:
            return "CAUTION"
        if index >= 0.4:
            return "STABLE"
        return "CALM"


if __name__ == "__main__":
    monitor = HighImpactMonitor()
    summary = monitor.get_high_impact_summary()
    print(summary)
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
