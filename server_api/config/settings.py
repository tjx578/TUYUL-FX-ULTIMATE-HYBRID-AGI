"""Runtime settings for the Reflective API gateway.

This lightweight settings holder avoids external dependencies while still
allowing environment-driven overrides for common API gateway options.
"""

from __future__ import annotations

import os
from typing import List


class Settings:
	"""Container for basic API configuration values."""

	def __init__(self) -> None:
		self.app_title: str = os.getenv(
			"TUYUL_API_TITLE", "TUYUL FX Reflective API Gateway"
		)
		self.app_version: str = os.getenv("TUYUL_API_VERSION", "6.0r∞")
		self.app_description: str = os.getenv(
			"TUYUL_API_DESCRIPTION",
			"Hybrid Reflective AGI Orchestration Gateway — Quad Vault System",
		)
		self.contact: dict[str, str] = {
			"author": os.getenv("TUYUL_API_AUTHOR", "Tuyul FX AGI Team"),
			"email": os.getenv("TUYUL_API_CONTACT", "reflective@tuyulfx.ai"),
		}
		self.cors_allow_origins: List[str] = self._parse_origins(
			os.getenv("CORS_ALLOW_ORIGINS", "*")
		)

	@staticmethod
	def _parse_origins(raw_origins: str) -> List[str]:
		if not raw_origins:
			return ["*"]
		if raw_origins.strip() == "*":
			return ["*"]
		return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
