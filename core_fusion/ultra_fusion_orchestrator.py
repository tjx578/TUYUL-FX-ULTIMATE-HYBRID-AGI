from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from core_fusion.bias_neutralizer import BiasNeutralizer, BiasNeutralizationResult
from core_fusion.fusion_integrator import FusionIntegrator
from core_fusion.montecarlo_confidence import MonteCarloConfidence, MonteCarloResult


FUSION_VAULT_PATH = "data/vault/fusion/ultra_fusion_log.json"


@dataclass(frozen=True)
class FusionTrace:
    fusion_integrator: Dict[str, Any]
    bias_neutralizer: Dict[str, Any]
    montecarlo_result: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "fusion_integrator": self.fusion_integrator,
            "bias_neutralizer": self.bias_neutralizer,
            "montecarlo_result": self.montecarlo_result,
        }


class UltraFusionOrchestrator:
    """Layer 12.9-13.0 reflective fusion pipeline coordinator."""

    def __init__(
        self,
        *,
        integrator: FusionIntegrator | None = None,
        neutralizer: BiasNeutralizer | None = None,
        montecarlo: MonteCarloConfidence | None = None,
    ) -> None:
        self.integrator = integrator or FusionIntegrator()
        self.neutralizer = neutralizer or BiasNeutralizer()
        self.montecarlo = montecarlo or MonteCarloConfidence(simulations=5000, seed=42)

    def run_fusion_cycle(self) -> Dict[str, Any]:
        """Execute a full Ultra Fusion cycle and aggregate results."""
        fusion_data = self.integrator.fuse_reflective_context()
        if fusion_data.get("status") != "OK":
            return {"status": "FAILED", "reason": "Incomplete fusion data"}

        fusion_output = fusion_data["fusion_output"]
        synthesis = fusion_data["synthesis"]

        fundamental_score = float(fusion_output["fundamental_score"])
        coherence = float(synthesis["alignment_score"])
        volatility_index = float(fusion_output["volatility_index"])

        bias_result = self._neutralize_bias(
            fundamental_score=fundamental_score,
            coherence=coherence,
            volatility_index=volatility_index,
        )

        mc_result = self._run_montecarlo(
            bias_result=bias_result,
            volatility_index=volatility_index,
        )

        ultra_context = self._build_ultra_context(
            synthesis=synthesis,
            fusion_output=fusion_output,
            bias_result=bias_result,
            mc_result=mc_result,
        )

        fusion_trace = FusionTrace(
            fusion_integrator=fusion_output,
            bias_neutralizer=bias_result.as_dict(),
            montecarlo_result=mc_result.as_dict(),
        )

        return {
            "status": "OK",
            "ultra_context": ultra_context,
            "fusion_trace": fusion_trace.as_dict(),
        }

    def save_to_vault(self, path: str = FUSION_VAULT_PATH) -> str:
        """Persist the latest Ultra Fusion context to the vault."""
        result = self.run_fusion_cycle()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2)
        print(f"[UltraFusion] Ultra Fusion Context saved -> {path}")
        return path

    def _neutralize_bias(
        self,
        *,
        fundamental_score: float,
        coherence: float,
        volatility_index: float,
    ) -> BiasNeutralizationResult:
        return self.neutralizer.neutralize(
            fundamental_bias=fundamental_score,
            fusion_bias=(fundamental_score + coherence / 100) / 2,
            sentiment_index=0.55,
            volatility_index=volatility_index,
        )

    def _run_montecarlo(
        self,
        *,
        bias_result: BiasNeutralizationResult,
        volatility_index: float,
    ) -> MonteCarloResult:
        return self.montecarlo.run(
            base_bias=bias_result.neutralized_bias,
            coherence=bias_result.reflective_coherence,
            volatility_index=volatility_index,
            confidence_weight=1.05,
        )

    def _build_ultra_context(
        self,
        *,
        synthesis: Dict[str, Any],
        fusion_output: Dict[str, Any],
        bias_result: BiasNeutralizationResult,
        mc_result: MonteCarloResult,
    ) -> Dict[str, Any]:
        final_conf12_score = round(
            (bias_result.fusion_confidence * 0.5 + mc_result.reflective_integrity * 0.5) / 1.1,
            2,
        )

        reflective_summary = (
            "Fusion cycle completed: "
            f"{synthesis['fusion_summary']} | "
            f"CONF12={final_conf12_score} | "
            f"Reliability={mc_result.reliability_score * 100:.1f}% | "
            f"Bias={bias_result.bias_state}"
        )

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fusion_integrity": synthesis["fusion_integrity"],
            "neutralized_bias": bias_result.neutralized_bias,
            "bias_state": bias_result.bias_state,
            "reflective_coherence": bias_result.reflective_coherence,
            "fusion_confidence": bias_result.fusion_confidence,
            "montecarlo_confidence": mc_result.mean_confidence,
            "reliability_score": mc_result.reliability_score,
            "stability_index": mc_result.stability_index,
            "reflective_integrity": mc_result.reflective_integrity,
            "final_CONF12_score": final_conf12_score,
            "fusion_summary": synthesis["fusion_summary"],
            "macro_theme": synthesis["macro_theme"],
            "regime": fusion_output["weekly_regime"],
            "reflective_summary": reflective_summary,
        }


if __name__ == "__main__":
    print("TUYUL FX - Ultra Fusion Orchestrator v5.3.3+ (Test Mode)")
    orchestrator = UltraFusionOrchestrator()
    result = orchestrator.run_fusion_cycle()

    print("\n--- ULTRA FUSION CONTEXT ---")
    print(json.dumps(result["ultra_context"], indent=2))

    orchestrator.save_to_vault()
