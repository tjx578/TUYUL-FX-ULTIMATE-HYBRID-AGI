from __future__ import annotations

"""Reflective Trade Plan Generator v6 (Quad Vault Mode)."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from api_tuyulfx_ai__jit_plugin import (
    getRgoUpdate,
    performAgiFullAnalysis,
    runTrq3d,
)
from core_fusion.smart_money_counter_zone_v3_5_reflective import (
    smart_money_counter_v3_5_reflective,
)

LOG_PATH = Path("data/logs/reflective_trade_plan_log.json")
BRIDGE_LOG_PATH = Path("data/logs/reflective_bridge_queue.jsonl")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _append_json_line(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False)
        file.write("\n")


def _send_to_reflective_bridge(payload: Dict[str, Any]) -> str:
    ticket = _utc_now().strftime("RB%Y%m%d%H%M%S%f")
    bridge_record = {
        "timestamp": _utc_now().isoformat(),
        "ticket": ticket,
        "pair": payload.get("pair"),
        "timeframe": payload.get("timeframe"),
        "signal_type": payload.get("signal", {}).get("type"),
        "integrity_index": payload.get("integrity_index"),
        "status": "QUEUED",
    }
    _append_json_line(BRIDGE_LOG_PATH, bridge_record)
    return ticket


def generate_reflective_trade_plan(
    pair: str = "XAUUSD", timeframe: str = "H4"
) -> Dict[str, Any]:
    """Generate reflective trade plan from fusion, TRQ–3D, and smart money inputs."""

    timestamp = _utc_now().isoformat()
    fusion_data = performAgiFullAnalysis(pair=pair, timeframe=timeframe)
    trq3d = runTrq3d(pair=pair, timeframe=timeframe)
    rgo = getRgoUpdate()

    smc_signal = smart_money_counter_v3_5_reflective(
        price=float(fusion_data.get("price", 0.0)),
        vwap=float(fusion_data.get("vwap", 0.0)),
        atr=float(fusion_data.get("atr", 0.0)),
        rsi=float(fusion_data.get("rsi", 0.0)),
        mfi=float(fusion_data.get("mfi", 0.0)),
        cci50=float(fusion_data.get("cci50", 0.0)),
        rsi_h4=float(fusion_data.get("rsi_h4", 0.0)),
        trq_energy=float(trq3d.get("mean_energy", 0.0)),
        reflective_intensity=float(trq3d.get("reflective_intensity", 0.0)),
        alpha=float(rgo.get("alpha", 0.0)),
        beta=float(rgo.get("beta", 0.0)),
        gamma=float(rgo.get("gamma", 0.0)),
        integrity_index=float(rgo.get("integrity_index", 0.0)),
        journal_path=LOG_PATH,
    )

    trade_plan = {
        "timestamp": timestamp,
        "pair": pair,
        "timeframe": timeframe,
        "fusion_conf12": fusion_data.get("conf12"),
        "wlwci": fusion_data.get("wlwci"),
        "rcadj": fusion_data.get("rcadj"),
        "trq_energy": trq3d.get("mean_energy"),
        "reflective_intensity": trq3d.get("reflective_intensity"),
        "rgo_alpha": rgo.get("alpha"),
        "rgo_beta": rgo.get("beta"),
        "rgo_gamma": rgo.get("gamma"),
        "integrity_index": rgo.get("integrity_index"),
        "signal": smc_signal,
    }

    trade_plan["bridge_ticket"] = _send_to_reflective_bridge(trade_plan)
    _append_json_line(LOG_PATH, trade_plan)
    return trade_plan


if __name__ == "__main__":
    print(json.dumps(generate_reflective_trade_plan("XAUUSD", "H4"), indent=2))
