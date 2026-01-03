"""Reflective Cloud Scheduler — temporal orchestrator for Quad Vault and Meta layer.

Runs periodic reflective cycles: bridge sync, trade plan generation, execution,
meta learning, and global audit, with logging fan-out to vault and cloud logs.
"""

from __future__ import annotations

import datetime
import threading
import time
from typing import Iterable, List, Optional

from server_api.services.cloud_logger_service import cloud_logger_service
from server_api.services.cloud_monitor_service import cloud_monitor_service
from server_api.services.ree_meta_service import ree_meta_service
from server_api.services.reflective_bridge_service import ReflectiveBridgeService, bridge_service
from server_api.services.reflective_execution_service import execution_service
from server_api.services.reflective_tradeplan_service import tradeplan_service


class CloudSchedulerService:
    """Schedule reflective cycles across Vault, Meta, and Monitoring layers."""

    def __init__(
        self,
        interval_minutes: int = 60,
        pairs: Optional[Iterable[str]] = None,
        meta_trigger_pair: str = "GBPUSD",
    ) -> None:
        self.interval = max(1, int(interval_minutes)) * 60
        self.pairs: List[str] = list(pairs) if pairs is not None else ["EURUSD", "GBPUSD", "XAUUSD"]
        self.meta_trigger_pair = meta_trigger_pair
        self.bridge = bridge_service or ReflectiveBridgeService()
        self.tradeplan = tradeplan_service
        self.execution = execution_service
        self.meta = ree_meta_service
        self.monitor = cloud_monitor_service
        self.logger = cloud_logger_service
        self.running = False
        self._thread: Optional[threading.Thread] = None

    # 🧩 1️⃣ Start scheduler in background
    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.logger.info(
            "[SCHEDULER] Reflective Cloud Scheduler started",
            {"interval_minutes": self.interval / 60, "pairs": self.pairs, "meta_trigger": self.meta_trigger_pair},
        )
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    # 🧩 2️⃣ Stop scheduler
    def stop(self) -> None:
        self.running = False
        self.logger.warn("[SCHEDULER] Reflective Cloud Scheduler stopped.")

    # 🧩 3️⃣ Run single cycle synchronously (useful for Cloud Scheduler trigger)
    def run_once(self) -> None:
        self._run_cycle()

    # ------------------------------------------------------------
    # Internal orchestration
    # ------------------------------------------------------------
    def _run_loop(self) -> None:
        while self.running:
            self._run_cycle()
            time.sleep(self.interval)

    def _run_cycle(self) -> None:
        start_time = datetime.datetime.utcnow().isoformat() + "Z"
        try:
            for pair in self.pairs:
                bridge_result = self.bridge.run_reflective_bridge(pair)
                self.logger.log_cycle({"pair": pair, **bridge_result})

                plan = self.tradeplan.generate_trade_plan(pair)
                self.execution.run_execution(pair)

                if pair == self.meta_trigger_pair:
                    meta_result = self.meta.run_meta_learning_cycle()
                    self.logger.log_meta_evolution(meta_result)

            audit = self.monitor.run_audit()
            self.logger.info("[AUDIT] Global Reflective Audit", audit)
        except Exception as exc:  # pragma: no cover - defensive path
            self.logger.error("[SCHEDULER ERROR] Reflective cycle failed", {"error": str(exc)})
        finally:
            end_time = datetime.datetime.utcnow().isoformat() + "Z"
            self.logger.info(
                "[SCHEDULER] Cycle completed",
                {"start": start_time, "end": end_time, "interval_minutes": self.interval / 60},
            )


# Runtime helper
cloud_scheduler_service = CloudSchedulerService()
