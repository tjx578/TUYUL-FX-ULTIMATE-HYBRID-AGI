"""Reflective notifier — sends structured alerts to webhook/console/logs."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from core_reflective.reflective_logger import ReflectiveLogger


class Notifier:
	"""Lightweight reflective notification publisher."""

	def __init__(self, webhook_url: Optional[str] = None, enabled: bool = False) -> None:
		self.logger = ReflectiveLogger("notifier")
		self.webhook_url = webhook_url or os.getenv("REFLECTIVE_WEBHOOK_URL") or ""
		self.enabled = enabled or bool(self.webhook_url)
		self.timeout = 5

	# 🧩 1️⃣ Kirim Notifikasi Reflektif ke Channel
	def send(self, level: str, message: str, payload: Dict[str, Any] | None = None) -> None:
		entry = {
			"timestamp": datetime.utcnow().isoformat() + "Z",
			"level": level.upper(),
			"message": message,
			"payload": payload or {},
		}

		# Log locally regardless of webhook status
		self.logger.log(entry, category="notification")

		if not self.enabled or not self.webhook_url:
			return

		try:
			requests.post(
				self.webhook_url,
				data=json.dumps(entry),
				headers={"Content-Type": "application/json"},
				timeout=self.timeout,
			)
		except Exception as exc:  # pragma: no cover - external I/O
			self.logger.error({"event": "notifier_error", "error": str(exc)})

	# 🧩 2️⃣ Shortcut: Notifikasi Reflektif Khusus
	def success(self, message: str, payload: Dict[str, Any] | None = None) -> None:
		self.send("SUCCESS", message, payload)

	def warn(self, message: str, payload: Dict[str, Any] | None = None) -> None:
		self.send("WARNING", message, payload)

	def error(self, message: str, payload: Dict[str, Any] | None = None) -> None:
		self.send("ERROR", message, payload)


# Runtime helper
notifier = Notifier()
