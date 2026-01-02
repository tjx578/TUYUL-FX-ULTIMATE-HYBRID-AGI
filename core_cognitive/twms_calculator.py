"""TWMS v2.2 Calculator - Core Engine
====================================

Comprehensive TWMS scoring system dengan dynamic weight distribution dan real-time
evaluation capability.

Author: Tuyul Kartel Dev Team
Version: 2.2
Date: 2025-10-29
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from enum import Enum
import logging
import yaml


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Timeframe(Enum):
    """Supported timeframes"""

    W1 = "W1"
    D1 = "D1"
    H4 = "H4"
    H1 = "H1"
    M15 = "M15"


@dataclass
class TWMSInput:
    """Input data structure untuk TWMS calculation"""

    # MFI-CCI Alignment
    mfi_d1: float
    mfi_h4: float
    mfi_h1: float
    cci_d1: float
    cci_h4: float
    cci_h1: float

    # RSI Position
    rsi_d1: float
    rsi_h4: float
    rsi_h1: float

    # Distance Factor
    distance: float  # Distance from key level (in %)

    # Smart Money
    smart_money_scenario: str
    smart_money_confidence: float

    # Multi-TF Trend Alignment
    trend_w1: str  # "bullish", "bearish", "sideways"
    trend_d1: str
    trend_h4: str

    # Metadata
    pair: str
    timestamp: Optional[str] = None


@dataclass
class TWMSResult:
    """TWMS calculation result"""

    total_score: int  # Out of 12
    component_scores: Dict[str, float]
    breakdown: Dict[str, Dict]
    is_exceptional: bool  # >= 11/12
    is_perfect: bool  # == 12/12
    recommendation: str
    confidence: float  # Overall confidence in setup

    def __str__(self) -> str:
        status = "PERFECT" if self.is_perfect else "EXCEPTIONAL" if self.is_exceptional else \
            "BELOW_THRESHOLD"
        return (
            f"TWMS Score: {self.total_score}/12 [{status}]\n"
            f"Recommendation: {self.recommendation}\n"
            f"Confidence: {self.confidence:.1f}%"
        )


class TWMSCalculator:
    """
    TWMS v2.2 Calculator dengan dynamic weighting dan comprehensive validation.

    Features:
    - Dynamic weight distribution (D1: 30%, H4: 40%, H1: 30%)
    - Component-by-component scoring
    - Exceptional criteria validation
    - Confidence calculation
    """

    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        Initialize TWMS Calculator dengan configuration.

        Args:
            config_path: Path ke configuration file
        """
        self.config = self._load_config(config_path)
        self.weights = self.config["twms"]["weights"]
        self.components = self.config["twms"]["components"]
        self.minimum_score = self.config["twms"]["minimum_score"]
        self.perfect_score = self.config["twms"]["perfect_score"]

        logger.info("TWMS Calculator v2.2 initialized")
        logger.info(
            "Weights - D1: %s, H4: %s, H1: %s",
            self.weights["d1"],
            self.weights["h4"],
            self.weights["h1"],
        )

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration dari YAML file"""
        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                return yaml.safe_load(config_file)
        except FileNotFoundError:
            logger.warning("Config file not found: %s, using defaults", config_path)
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Default configuration jika file tidak ditemukan"""
        return {
            "twms": {
                "minimum_score": 11,
                "perfect_score": 12,
                "weights": {"d1": 0.30, "h4": 0.40, "h1": 0.30},
                "components": {
                    "mfi_cci_alignment": {"max_score": 3, "weight": 0.25},
                    "rsi_position": {"max_score": 2, "weight": 0.20},
                    "multi_tf_alignment": {"max_score": 3, "weight": 0.25},
                    "distance_factor": {"max_score": 2, "weight": 0.15},
                    "smart_money": {"max_score": 2, "weight": 0.15},
                },
            }
        }

    def calculate(self, input_data: TWMSInput) -> TWMSResult:
        """
        Calculate TWMS score dari input data.

        Args:
            input_data: TWMSInput object dengan semua required data

        Returns:
            TWMSResult object dengan detailed breakdown
        """
        logger.info("Calculating TWMS for %s", input_data.pair)

        # Calculate each component
        mfi_cci_score, mfi_cci_breakdown = self._calculate_mfi_cci_alignment(input_data)
        rsi_score, rsi_breakdown = self._calculate_rsi_position(input_data)
        multi_tf_score, multi_tf_breakdown = self._calculate_multi_tf_alignment(input_data)
        distance_score, distance_breakdown = self._calculate_distance_factor(input_data)
        sm_score, sm_breakdown = self._calculate_smart_money(input_data)

        # Aggregate scores
        component_scores = {
            "mfi_cci_alignment": mfi_cci_score,
            "rsi_position": rsi_score,
            "multi_tf_alignment": multi_tf_score,
            "distance_factor": distance_score,
            "smart_money": sm_score,
        }

        total_score = int(sum(component_scores.values()))

        # Build breakdown
        breakdown = {
            "mfi_cci_alignment": mfi_cci_breakdown,
            "rsi_position": rsi_breakdown,
            "multi_tf_alignment": multi_tf_breakdown,
            "distance_factor": distance_breakdown,
            "smart_money": sm_breakdown,
        }

        # Determine status
        is_perfect = total_score == self.perfect_score
        is_exceptional = total_score >= self.minimum_score

        # Generate recommendation
        recommendation = self._generate_recommendation(total_score, component_scores)

        # Calculate confidence
        confidence = self._calculate_confidence(total_score, component_scores, input_data)

        result = TWMSResult(
            total_score=total_score,
            component_scores=component_scores,
            breakdown=breakdown,
            is_exceptional=is_exceptional,
            is_perfect=is_perfect,
            recommendation=recommendation,
            confidence=confidence,
        )

        logger.info("TWMS Result: %s/12 (Confidence: %.1f%%)", total_score, confidence)
        return result

    def _calculate_mfi_cci_alignment(
        self,
        data: TWMSInput,
    ) -> Tuple[float, Dict]:
        """
        Calculate MFI-CCI Alignment score (max 3 points).

        Logic:
        - D1 alignment: 1 point
        - H4 alignment: 1 point
        - H1 alignment: 1 point

        Alignment = MFI and CCI both oversold OR both overbought
        """
        score = 0.0
        breakdown = {}

        # D1 alignment (weight: 30%)
        d1_aligned = self._check_alignment(data.mfi_d1, data.cci_d1)
        if d1_aligned:
            score += self.weights["d1"] * 3
        breakdown["d1"] = {"aligned": d1_aligned, "mfi": data.mfi_d1, "cci": data.cci_d1}

        # H4 alignment (weight: 40%)
        h4_aligned = self._check_alignment(data.mfi_h4, data.cci_h4)
        if h4_aligned:
            score += self.weights["h4"] * 3
        breakdown["h4"] = {"aligned": h4_aligned, "mfi": data.mfi_h4, "cci": data.cci_h4}

        # H1 alignment (weight: 30%)
        h1_aligned = self._check_alignment(data.mfi_h1, data.cci_h1)
        if h1_aligned:
            score += self.weights["h1"] * 3
        breakdown["h1"] = {"aligned": h1_aligned, "mfi": data.mfi_h1, "cci": data.cci_h1}

        # Round to nearest 0.5
        score = round(score * 2) / 2
        score = min(score, 3.0)  # Cap at 3

        return score, breakdown

    def _check_alignment(self, mfi: float, cci: float) -> bool:
        """Check if MFI and CCI are aligned (both oversold or both overbought)"""
        oversold = mfi < 30 and cci < -100
        overbought = mfi > 70 and cci > 100
        return oversold or overbought

    def _calculate_rsi_position(self, data: TWMSInput) -> Tuple[float, Dict]:
        """
        Calculate RSI Position score (max 2 points).

        Logic:
        - D1 RSI in optimal range: weighted points
        - H4 RSI in optimal range: weighted points
        - H1 RSI in optimal range: weighted points

        Optimal ranges:
        - Bullish: RSI 40-60 (not overbought)
        - Bearish: RSI 40-60 (not oversold)
        """
        score = 0.0
        breakdown = {}

        # D1 RSI
        d1_optimal = self._is_rsi_optimal(data.rsi_d1)
        if d1_optimal:
            score += self.weights["d1"] * 2
        breakdown["d1"] = {"optimal": d1_optimal, "value": data.rsi_d1}

        # H4 RSI
        h4_optimal = self._is_rsi_optimal(data.rsi_h4)
        if h4_optimal:
            score += self.weights["h4"] * 2
        breakdown["h4"] = {"optimal": h4_optimal, "value": data.rsi_h4}

        # H1 RSI
        h1_optimal = self._is_rsi_optimal(data.rsi_h1)
        if h1_optimal:
            score += self.weights["h1"] * 2
        breakdown["h1"] = {"optimal": h1_optimal, "value": data.rsi_h1}

        score = round(score * 2) / 2
        score = min(score, 2.0)

        return score, breakdown

    def _is_rsi_optimal(self, rsi: float) -> bool:
        """Check if RSI is in optimal range (40-60)"""
        return 40 <= rsi <= 60

    def _calculate_multi_tf_alignment(self, data: TWMSInput) -> Tuple[float, Dict]:
        """
        Calculate Multi-TF Alignment score (max 3 points).

        Logic:
        - W1, D1, H4 all bullish = 3 points
        - W1, D1, H4 all bearish = 3 points
        - 2/3 aligned = 1-2 points (weighted)
        - <2 aligned = 0 points
        """
        trends = [data.trend_w1.lower(), data.trend_d1.lower(), data.trend_h4.lower()]
        breakdown = {"w1": data.trend_w1, "d1": data.trend_d1, "h4": data.trend_h4}

        bullish_count = trends.count("bullish")
        bearish_count = trends.count("bearish")

        if bullish_count == 3 or bearish_count == 3:
            score = 3.0
            breakdown["alignment"] = "full"
        elif bullish_count == 2 or bearish_count == 2:
            score = 2.0
            breakdown["alignment"] = "partial"
        else:
            score = 0.0
            breakdown["alignment"] = "none"

        return score, breakdown

    def _calculate_distance_factor(self, data: TWMSInput) -> Tuple[float, Dict]:
        """
        Calculate Distance Factor score (max 2 points).

        Logic:
        - Distance 0-2%: 2 points (perfect)
        - Distance 2-5%: 1 point (acceptable)
        - Distance >5%: 0 points (too far)
        """
        distance = abs(data.distance)

        if distance <= 2.0:
            score = 2.0
            category = "perfect"
        elif distance <= 5.0:
            score = 1.0
            category = "acceptable"
        else:
            score = 0.0
            category = "too_far"

        breakdown = {
            "distance": distance,
            "category": category,
            "score": score,
        }

        return score, breakdown

    def _calculate_smart_money(self, data: TWMSInput) -> Tuple[float, Dict]:
        """
        Calculate Smart Money score (max 2 points).

        Logic:
        - Confidence >= 90%: 2 points
        - Confidence 85-89%: 1.5 points
        - Confidence 80-84%: 1 point
        - Confidence < 80%: 0 points
        """
        confidence = data.smart_money_confidence

        if confidence >= 90:
            score = 2.0
        elif confidence >= 85:
            score = 1.5
        elif confidence >= 80:
            score = 1.0
        else:
            score = 0.0

        breakdown = {
            "scenario": data.smart_money_scenario,
            "confidence": confidence,
            "score": score,
        }

        return score, breakdown

    def _generate_recommendation(
        self,
        total_score: int,
        component_scores: Dict,
    ) -> str:
        """Generate execution recommendation berdasarkan score"""
        if total_score == 12:
            return "EXECUTE - Perfect setup (12/12)! Highest confidence."
        if total_score == 11:
            if component_scores["smart_money"] >= 1.5:
                return "EXECUTE - Exceptional setup (11/12) with strong Smart Money."
            return (
                "MONITOR - Good setup (11/12) but Smart Money < 85%. Wait for confirmation."
            )
        if total_score >= 9:
            return "MONITOR - Decent setup but below exceptional threshold. Wait for improvement."
        return "SKIP - Setup does not meet exceptional criteria."

    def _calculate_confidence(
        self,
        total_score: int,
        component_scores: Dict,
        data: TWMSInput,
    ) -> float:
        """
        Calculate overall confidence dalam setup.

        Formula:
        Base confidence dari TWMS score + adjustments dari component quality
        """
        base_confidence = (total_score / self.perfect_score) * 100

        adjustment = 0.0

        if total_score == 12:
            adjustment += 5.0

        if data.smart_money_confidence >= 90:
            adjustment += 3.0

        if component_scores["multi_tf_alignment"] == 3.0:
            adjustment += 2.0

        if component_scores["distance_factor"] == 2.0:
            adjustment += 2.0

        if data.smart_money_confidence < 85:
            adjustment -= 5.0

        if component_scores["mfi_cci_alignment"] < 2.0:
            adjustment -= 3.0

        confidence = base_confidence + adjustment
        confidence = max(0.0, min(100.0, confidence))

        return confidence


def create_sample_input() -> TWMSInput:
    """Create sample input untuk testing"""
    return TWMSInput(
        mfi_d1=25.0,
        mfi_h4=28.0,
        mfi_h1=30.0,
        cci_d1=-120.0,
        cci_h4=-110.0,
        cci_h1=-95.0,
        rsi_d1=45.0,
        rsi_h4=48.0,
        rsi_h1=52.0,
        distance=1.5,
        smart_money_scenario="accumulation",
        smart_money_confidence=88.0,
        trend_w1="bullish",
        trend_d1="bullish",
        trend_h4="bullish",
        pair="GBPJPY",
        timestamp="2025-10-29 10:00:00",
    )


if __name__ == "__main__":
    print("=" * 60)
    print("TWMS v2.2 Calculator - Test Run")
    print("=" * 60)

    calculator = TWMSCalculator(config_path="../config/settings.yaml")

    sample = create_sample_input()

    print("\nInput Data:")
    print(f"Pair: {sample.pair}")
    print(f"Smart Money: {sample.smart_money_scenario} ({sample.smart_money_confidence}%)")
    print(f"Distance: {sample.distance}%")
    print(f"Trends: W1={sample.trend_w1}, D1={sample.trend_d1}, H4={sample.trend_h4}")

    result = calculator.calculate(sample)

    print(f"\n{result}")
    print("\nComponent Breakdown:")
    for component, score in result.component_scores.items():
        print(f"  {component}: {score}")

    print("\n" + "=" * 60)
