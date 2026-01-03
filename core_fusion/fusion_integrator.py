"""
🧠 TUYUL FX Ultimate Hybrid AGI – Fusion Integrator v5.3.3+

Layer L12 – Reflective Fusion Integrator
Menggabungkan:
  • Fundamental Context (L11.5)
  • Technical Meta Signal (L10)
  • Adaptive Risk Model (L11)
  • Weekly Macro Cache (L11.3)
Menjalankan synthesis → CONF₁₂ reasoning → output ke Reflective Journal.

Author : TUYUL-KARTEL-FX AGI Dev Team
Version: 5.3.3+
Date   : 2026-01-02
"""

from __future__ import annotations
import json
import os
from datetime import datetime
from statistics import mean
from typing import Dict, Any

# ===================================================================
# 🔹 Utility Loaders
# ===================================================================

def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

# ===================================================================
# 🔹 Fusion Integrator Core
# ===================================================================

class FusionIntegrator:
    """Core Reflective Fusion Integrator (Layer 12)"""

    def __init__(
        self,
        fundamental_path: str = "data/vault/logs/fundamental_feed_log.json",
        weekly_cache_path: str = "data/vault/logs/weekly_outlook_cache.json"
    ):
        self.fundamental_path = fundamental_path
        self.weekly_cache_path = weekly_cache_path

        self.fundamental_data = _load_json(fundamental_path)
        self.weekly_cache = _load_json(weekly_cache_path)

    # ---------------------------------------------------------------
    # 🧩 MAIN FUSION LOGIC
    # ---------------------------------------------------------------

    def fuse_reflective_context(self) -> Dict[str, Any]:
        """Gabungkan konteks makro (L11.3–L11.5) → reasoning CONF₁₂"""
        entries = self.fundamental_data.get("entries", [])
        regional = self.weekly_cache.get("regional_summary", {})
        pairs = self.weekly_cache.get("pair_bias_matrix", {})

        if not entries or not regional:
            return {"status": "INCOMPLETE", "reason": "Missing input data"}

        latest = entries[0]  # Ambil snapshot terakhir
        avg_conf = mean([x.get("confidence", 0.0) for x in entries])

        fusion_output = {
            "timestamp": datetime.utcnow().isoformat(),
            "fusion_version": "v5.3.3+",
            "macro_bias": latest.get("macro_bias"),
            "fundamental_score": latest.get("fundamental_score"),
            "volatility_index": latest.get("volatility_index"),
            "average_confidence": round(avg_conf, 3),
            "weekly_regime": self.weekly_cache.get("macro_overview", {}).get(
                "global_risk_sentiment", "Unknown"
            ),
            "pair_focus": latest.get("pair_focus"),
            "pair_bias_matrix": pairs,
            "regional_confidence_avg": round(
                mean([r.get("confidence", 0.0) for r in regional.values()]), 3
            ),
        }

        # Derive final synthesis
        bias_strength = "BULLISH" if fusion_output["fundamental_score"] >= 0.65 else (
            "BEARISH" if fusion_output["fundamental_score"] <= 0.35 else "NEUTRAL"
        )

        # Reflective alignment scoring
        alignment_score = self._compute_alignment_score(
            fusion_output["fundamental_score"], avg_conf, fusion_output["volatility_index"]
        )

        synthesis = {
            "fusion_summary": f"{bias_strength} – {fusion_output['weekly_regime']} environment",
            "bias_strength": bias_strength,
            "alignment_score": alignment_score,
            "fusion_integrity": round(alignment_score / 100, 3),
            "macro_theme": self.weekly_cache.get("macro_themes", []),
        }

        return {"fusion_output": fusion_output, "synthesis": synthesis, "status": "OK"}

    # ---------------------------------------------------------------
    # ⚙️ Reflective Coherence Computation
    # ---------------------------------------------------------------

    def _compute_alignment_score(self, score: float, conf: float, vix: float) -> float:
        """Hitung alignment score 0–100 antara makro, confidence, dan volatilitas"""
        score_factor = score * 100
        conf_factor = conf * 100
        vix_penalty = max(0, (vix - 15) * 1.5)  # penalti bila VIX > 15

        raw = (score_factor * 0.45) + (conf_factor * 0.45) - vix_penalty
        return max(0.0, min(100.0, raw))

    # ---------------------------------------------------------------
    # 🧠 Vault Sync Output
    # ---------------------------------------------------------------

    def save_to_vault(
        self, output_path: str = "data/vault/fusion/fusion_reflective_log.json"
    ) -> str:
        """Simpan hasil fusion ke Vault untuk Layer-15"""
        fusion_result = self.fuse_reflective_context()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(fusion_result, f, indent=2)

        print(f"[FusionIntegrator] ✅ Reflective fusion log saved → {output_path}")
        return output_path


# ===================================================================
# 🧪 TEST MODE
# ===================================================================

if __name__ == "__main__":
    integrator = FusionIntegrator()
    result = integrator.fuse_reflective_context()

    print("🧠 Reflective Fusion Result (L12):")
    print(json.dumps(result, indent=2))

    # Optional save test
    integrator.save_to_vault()
