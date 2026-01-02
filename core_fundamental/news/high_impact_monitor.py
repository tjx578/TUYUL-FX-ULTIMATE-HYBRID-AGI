"""High Impact Monitor – TUYUL FX AGI v5.3.3+."""

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
