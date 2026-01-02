"""
enums_cognitive_constants.py – TUYUL FX ULTIMATE HYBRID AGI 🧠⚡
===============================================================

Kumpulan enumerasi dan konstanta kognitif global.
Digunakan di seluruh modul reasoning (TWMS, Reflex, Fusion, Reflective).
Tujuannya untuk menjaga konsistensi semantik antar layer reasoning AGI.
"""

from enum import Enum, IntEnum


# ==========================================================
# 🧠 COGNITIVE REASONING ENUMS
# ==========================================================


class CognitiveBias(Enum):
    """Jenis bias kognitif utama sistem reflektif."""

    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"
    SIDEWAYS = "Sideways"
    UNDEFINED = "Undefined"


class MarketRegime(IntEnum):
    """Rezim pasar reflektif (Layer TWMS & Fusion)."""

    RANGE = 0
    TREND = 1
    EXPANSION = 2
    REVERSAL = 3


class ReflexState(Enum):
    """Keadaan refleks-emosi dalam reasoning cycle."""

    SYNCED = "Synced"
    DESYNCED = "Desynced"
    LOCKOUT = "Lockout"
    REVIEW = "Review"


class ConfidenceLevel(IntEnum):
    """Level kepercayaan sistem reflektif (0–100)."""

    LOW = 50
    MEDIUM = 70
    HIGH = 85
    EXTREME = 95


class FusionMode(Enum):
    """Mode penggabungan reasoning pada Fusion Layer."""

    STANDARD = "Standard Fusion"
    REFLECTIVE = "Reflective Coherence"
    HYBRID = "Hybrid Adaptive"
    AUTONOMOUS = "Autonomous Mode"


class ReflectivePhase(IntEnum):
    """Tahapan kesadaran reflektif dalam siklus REE."""

    INITIALIZATION = 1
    FUSION_LOCK = 2
    ADAPTIVE_FEEDBACK = 3
    REFLECTIVE_EXPANSION = 4
    COHERENCE_STABILIZATION = 5


# ==========================================================
# ⚙️ COGNITIVE METRICS CONSTANTS
# ==========================================================

COHERENCE_THRESHOLD = 0.90  # minimum required for reflective lock
INTEGRITY_MINIMUM = 0.88  # minimum system integrity before sync
CONF12_REQUIRED = 0.92  # fusion confidence requirement
REE_FEEDBACK_INTERVAL = 3600  # reflective learning refresh (seconds)
TRQ3D_DEFAULT_ALPHA = 1.02  # default α reflective multiplier
TRQ3D_DEFAULT_BETA = 0.97  # default β reflective stabilizer
TRQ3D_DEFAULT_GAMMA = 1.11  # default γ reflective expansion


# ==========================================================
# 🧩 META–LEARNING & ADAPTIVE CONSTANTS
# ==========================================================

META_LEARNING_RATE = 0.015  # global REE learning rate
META_RESILIENCE_INDEX = 0.93  # threshold to prevent overfitting
META_RESONANCE_LIMIT = 0.95  # coherence cap in feedback cycle
ADAPTIVE_RISK_WEIGHT = 0.018  # max fraction for adaptive risk engine


# ==========================================================
# 🔍 REFLEXIVE & TWMS LINKING
# ==========================================================

REFLEX_GATE_PASS = 0.80  # Reflex coherence pass limit
TWMS_WEIGHT_D1 = 0.30
TWMS_WEIGHT_H4 = 0.40
TWMS_WEIGHT_H1 = 0.30


# ==========================================================
# 🧾 UTILITY ENUMS
# ==========================================================


class LayerID(Enum):
    """Penanda layer utama pipeline TUYUL FX."""

    L1_TWMS = "L1 – TWMS Cognitive Alignment"
    L5_REFLEX = "L5 – Reflex Emotion Core"
    L10_FTA = "L10 – Fundamental–Technical Alignment"
    L11_RISK = "L11 – Adaptive Risk Engine"
    L11_5_FUND = "L11.5 – Fundamental Drive"
    L12_FUSION = "L12 – Fusion Spectre Core"
    L15_REFLECTIVE = "L15 – Reflective Trade Plan"
    L16_EXECUTION = "L16 – Reflective Execution Bridge"
    L17_META = "L17 – Meta Learning Driver"


# ==========================================================
# ✅ HELPER DICTIONARIES
# ==========================================================

REFLECTIVE_STATUS_MAP = {
    "ready": "System ready – coherence stable.",
    "sync": "Reflective lock achieved – harmonic coherence.",
    "training": "REE meta-learning running adaptive tuning.",
    "idle": "System stable – awaiting next reflective cycle.",
    "error": "Reflective instability detected – reinit required.",
}

COGNITIVE_SYMBOLS = {
    "🧠": "Cognitive reasoning core active.",
    "⚡": "Reflex emotion synchronization engaged.",
    "💹": "Fusion spectral convergence achieved.",
    "🐺": "Reflective AGI lock – Wolf Mode active.",
}


# ==========================================================
# 🧩 DEBUGGING UTIL
# ==========================================================

if __name__ == "__main__":
    print("🧠 TUYUL FX Cognitive Constants Loaded")
    print("Bias Types:", [b.value for b in CognitiveBias])
    print("Fusion Mode:", [f.value for f in FusionMode])
    print(f"Coherence Threshold: {COHERENCE_THRESHOLD}")
    print(f"Meta Learning Rate: {META_LEARNING_RATE}")
