"""
weekly_outlook_sync.py – TUYUL FX AGI v5.3.3+
=============================================

Membangun laporan mingguan risiko fundamental dan event ekonomi besar.
Menyediakan ringkasan reflektif untuk sinkronisasi dengan Kartel Vault & Journal Vault.

Author : TUYUL KARTEL DEV TEAM
Version: v5.3.3+
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict, List

from core_fundamental.fundamental_auto_feed_v_533 import FundamentalAutoFeed
from core_fundamental.news.high_impact_monitor import HighImpactMonitor


class WeeklyOutlookSync:
    """🧭 TUYUL FX – Weekly Fundamental & Risk Outlook Generator."""

    def __init__(
        self,
        api_key: str = "DEMO_KEY",
        vault_path: str = "data/logs/weekly_outlook_cache.json",
    ):
        self.monitor = HighImpactMonitor(api_key)
        self.feed = FundamentalAutoFeed(api_key)
        self.vault_path = Path(vault_path)

    def generate_outlook(self, pairs: List[str] | None = None) -> Dict[str, Any]:
        """Bangun laporan fundamental mingguan lintas-pair FX."""
        print("[OUTLOOK] 🔁 Generating weekly fundamental outlook...")
        pairs = pairs or [
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "AUDUSD",
            "USDCAD",
            "XAUUSD",
            "NZDUSD",
        ]

        news_summary = self.monitor.get_high_impact_summary(days_ahead=7)
        fundamental_summary = self.feed.compute_fundamental_score()

        bias_level = self._derive_global_bias(fundamental_summary, news_summary)

        report = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "fundamental_score": fundamental_summary["fundamental_score"],
            "macro_bias": fundamental_summary["macro_bias"],
            "news_risk_index": news_summary["risk_index"],
            "risk_mode": news_summary["risk_mode"],
            "global_bias_level": bias_level,
            "pairs_affected": pairs,
            "correlation_signal": fundamental_summary["correlation_signal"],
            "source": "TUYUL_WOLF_WEEKLY_SYNC_v5.3.3",
        }

        self._save_to_vault(report)
        return report

    def _derive_global_bias(self, fundamental: Dict[str, Any], news: Dict[str, Any]) -> str:
        """Gabungkan bias fundamental & risiko berita menjadi bias global reflektif."""
        score = fundamental["fundamental_score"]
        risk = news["risk_index"]

        if risk >= 0.7 and score >= 0.65:
            return "RISK-OFF_BULLISH"
        if risk >= 0.7 and score < 0.5:
            return "RISK-OFF_BEARISH"
        if risk < 0.4 and score >= 0.65:
            return "RISK-ON_BULLISH"
        if risk < 0.4 and score < 0.45:
            return "RISK-ON_BEARISH"
        return "NEUTRAL_CONSOLIDATION"

    def _save_to_vault(self, report: Dict[str, Any]) -> None:
        """Simpan laporan mingguan ke cache vault."""
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.vault_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(report, indent=2))
            f.write("\n---\n")
        print(f"[OUTLOOK] 💾 Weekly outlook saved → {self.vault_path}")


if __name__ == "__main__":
    outlook = WeeklyOutlookSync()
    result = outlook.generate_outlook()
    print("\n🧭 TUYUL FX – Weekly Outlook Summary:")
    print(json.dumps(result, indent=2))
