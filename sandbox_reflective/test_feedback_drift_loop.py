"""
Feedback Drift Loop Tester v6.0r++
----------------------------------------
Part of the TUYUL FX Reflective Sandbox system.
Simulates α–β–γ feedback drift and recovery to test
adaptive learning stability under dynamic reflective field stress.
"""

import json
import os
import random
import time
from datetime import datetime
from typing import Dict, Any

from core_meta.ree_feedback_interface import REEFeedbackInterface
from core_meta.ree_adaptive_analysis import REEAdaptiveAnalysis
from core_meta.ree_integrity_controller import REEIntegrityController
from core_reflective.reflective_logger import ReflectiveLogger


class FeedbackDriftLoopTester:
    """
    🧩 Feedback Drift Loop Tester
    Runs multiple cycles to stress-test α–β–γ learning feedback and recovery.
    """

    def __init__(self) -> None:
        self.logger = ReflectiveLogger("FeedbackDriftLoopTester")
        self.feedback = REEFeedbackInterface()
        self.analyzer = REEAdaptiveAnalysis()
        self.integrity = REEIntegrityController()

        self.loop_state: Dict[str, Any] = {
            "cycle": 0,
            "alpha_drift": 0.0,
            "beta_drift": 0.0,
            "gamma_drift": 0.0,
            "feedback_gain": 0.0,
            "integrity_index": 0.0,
            "reflective_coherence": 0.0,
            "recovery_triggered": False,
            "status": "idle"
        }

    # ------------------------------------------------------------
    # 🚀 RUN FEEDBACK LOOP TEST
    # ------------------------------------------------------------
    def run(self, loops: int = 10) -> Dict[str, Any]:
        """Run reflective feedback drift test loop."""
        self.logger.log(f"Running Feedback Drift Loop Test for {loops} cycles...")
        self.loop_state["status"] = "running"
        records = []

        for i in range(1, loops + 1):
            self.loop_state["cycle"] = i
            self.logger.log(f"Cycle {i} — Simulating α–β–γ feedback drift...")

            # Step 1: Simulate artificial drift
            alpha_drift = round(random.uniform(-0.02, 0.02), 5)
            beta_drift = round(random.uniform(-0.015, 0.015), 5)
            gamma_drift = round(random.uniform(-0.018, 0.018), 5)

            drift = {
                "alpha_drift": alpha_drift,
                "beta_drift": beta_drift,
                "gamma_drift": gamma_drift,
                "mean_drift": round((alpha_drift + beta_drift + gamma_drift) / 3, 5)
            }

            # Step 2: Analyze drift impact and learning gain
            drift_result = self.analyzer.compute_reflective_drift()
            gain = self.feedback.compute_learning_feedback()

            # Step 3: Evaluate integrity
            integrity = self.integrity.evaluate_integrity()
            recovery_triggered = integrity["integrity_index"] < 0.93

            record = {
                "cycle_id": i,
                "drift": drift,
                "drift_analysis": drift_result,
                "learning_feedback": gain,
                "integrity": integrity,
                "recovery_triggered": recovery_triggered,
                "timestamp": datetime.utcnow().isoformat()
            }

            self.loop_state.update({
                "alpha_drift": alpha_drift,
                "beta_drift": beta_drift,
                "gamma_drift": gamma_drift,
                "feedback_gain": gain["learning_gain"],
                "integrity_index": integrity["integrity_index"],
                "reflective_coherence": integrity["reflective_coherence"],
                "recovery_triggered": recovery_triggered
            })

            records.append(record)

            status_msg = (
                f"Cycle {i} — Drift: {drift['mean_drift']}, "
                f"Integrity: {integrity['integrity_index']:.3f}, "
                f"Recovery: {'YES' if recovery_triggered else 'NO'}"
            )
            self.logger.log(status_msg)

            time.sleep(0.8)

        self.loop_state["status"] = "completed"
        self._save_drift_test_log(records)
        self.logger.log(f"Feedback Drift Loop Test completed for {loops} cycles.")

        return {"status": "completed", "records": records}

    # ------------------------------------------------------------
    # 💾 SAVE TEST RESULTS
    # ------------------------------------------------------------
    def _save_drift_test_log(self, records: list) -> None:
        """Save reflective drift test results to sandbox logs."""
        os.makedirs("sandbox_reflective/logs", exist_ok=True)
        path = f"sandbox_reflective/logs/drift_test_{int(time.time())}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        self.logger.log(f"Drift test log saved to {path}")


# ------------------------------------------------------------
# 🧠 USAGE EXAMPLE
# ------------------------------------------------------------
if __name__ == "__main__":
    tester = FeedbackDriftLoopTester()
    result = tester.run(loops=10)
    print(json.dumps(result, indent=2))
