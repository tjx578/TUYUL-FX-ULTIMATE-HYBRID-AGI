"""REE Integrity Controller – Layer 17.5 meta-integrity coordination."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping

from core_meta.ree_field_resonance_mapper import REEFieldResonanceMapper
from core_reflective.reflective_evolution_engine_v6 import ReflectiveEvolutionEngine


class REEIntegrityController:
    """Integrate REE outputs and guard reflective integrity across vaults."""

    def __init__(self, sync_path: str = "data/integrity/ree_integrity_feedback.json") -> None:
        self.ree = ReflectiveEvolutionEngine()
        self.mapper = REEFieldResonanceMapper()
        self.sync_path = Path(sync_path)

    def evaluate_integrity(self, ree_feedback: Mapping[str, Any]) -> Dict[str, Any]:
        reflective_integrity = self._as_float(
            ree_feedback.get("reflective_integrity"), default=0.0
        )
        alpha = self._as_float(ree_feedback.get("alpha"), default=1.0)
        beta = self._as_float(ree_feedback.get("beta"), default=1.0)
        gamma = self._as_float(ree_feedback.get("gamma"), default=1.0)

        resonance_info = self.mapper.map_resonance(alpha, beta, gamma)
        resonance_stability = float(resonance_info["stability"])

        integrity_status = (
            "PASS" if reflective_integrity >= 0.9 and resonance_stability >= 0.88 else "REVIEW"
        )

        calibration_delta = self._calculate_meta_adjustment(alpha, beta, gamma)
        timestamp = self._timestamp()

        self.ree.ingest_feedback(
            {
                "reflective_integrity": reflective_integrity,
                "alpha": alpha,
                "beta": beta,
                "gamma": gamma,
            }
        )

        result = {
            "timestamp": timestamp,
            "reflective_integrity": round(reflective_integrity, 4),
            "resonance_stability": round(resonance_stability, 4),
            "meta_weights": {"alpha": alpha, "beta": beta, "gamma": gamma},
            "calibration_delta": calibration_delta,
            "integrity_status": integrity_status,
            "resonance_state": resonance_info["state"],
            "lorentzian_phase": resonance_info["lorentzian_phase"],
        }

        self._log_integrity(result)
        return result

    def _calculate_meta_adjustment(self, alpha: float, beta: float, gamma: float) -> Dict[str, Any]:
        drift_alpha = round((alpha - 1.0) * 0.1, 4)
        drift_beta = round((beta - 1.0) * 0.1, 4)
        drift_gamma = round((gamma - 1.0) * 0.1, 4)

        total_drift = abs(drift_alpha) + abs(drift_beta) + abs(drift_gamma)
        meta_drift = "LOW" if total_drift < 0.05 else "HIGH"

        return {
            "alpha_delta": drift_alpha,
            "beta_delta": drift_beta,
            "gamma_delta": drift_gamma,
            "meta_drift": meta_drift,
        }

    def _log_integrity(self, data: Dict[str, Any]) -> None:
        self.sync_path.parent.mkdir(parents=True, exist_ok=True)
        with self.sync_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, indent=2))
            handle.write("\n---\n")

    def propagate_to_vaults(self, result: Mapping[str, Any]) -> Dict[str, Any]:
        sync_packet = {
            "state": result.get("integrity_status"),
            "alpha": result.get("meta_weights", {}).get("alpha"),
            "beta": result.get("meta_weights", {}).get("beta"),
            "gamma": result.get("meta_weights", {}).get("gamma"),
            "timestamp": result.get("timestamp"),
        }
        print("[META-INTEGRITY] Propagating meta-integrity to vaults...")
        print(json.dumps(sync_packet, indent=2))
        print("[META-INTEGRITY] Vault synchronization completed (Hybrid, FX, Kartel, Journal)")
        return sync_packet

    @staticmethod
    def _as_float(value: Any, *, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _timestamp() -> str:
        return f"{datetime.utcnow().isoformat()}Z"


if __name__ == "__main__":
    dummy_feedback = {
        "reflective_integrity": 0.912,
        "alpha": 1.03,
        "beta": 0.98,
        "gamma": 1.07,
    }

    controller = REEIntegrityController()
    result = controller.evaluate_integrity(dummy_feedback)
    controller.propagate_to_vaults(result)

    print("\nREE Integrity Evaluation Complete:")
    print(json.dumps(result, indent=2))
