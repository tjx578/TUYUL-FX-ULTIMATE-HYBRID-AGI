"""Real-time Fundamental Daemon for TUYUL FX v5.3.3."""

from __future__ import annotations

import json
import time

import redis

from core_fundamental.fundamental_auto_feed_v_533 import FundamentalAutoFeed


class FundamentalRealtimeDaemon:
    """Push fundamental feed snapshots to Redis at a fixed interval."""

    def __init__(self, api_key: str, redis_host: str = "localhost", redis_port: int = 6379):
        self.feed = FundamentalAutoFeed(api_key)
        self.redis_client = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
        )
        self.channel = "tuyul_fundamental_feed"

    def run(self, interval: int = 60) -> None:
        if interval <= 0:
            raise ValueError("interval must be a positive number of seconds")
        print("[DAEMON] 🚀 TUYUL Fundamental Feed v5.3.3 active.")
        print(f"[INFO] Data pushed to Redis channel: {self.channel}")

        while True:
            try:
                result = self.feed.compute_fundamental_score()
                payload = json.dumps(result)
                self.redis_client.publish(self.channel, payload)

                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"Fundamental Score: {result['fundamental_score']} | "
                    f"Bias: {result['macro_bias']} | "
                    f"VIX: {result['volatility_index']}"
                )
                time.sleep(interval)
            except Exception as exc:
                print(f"[ERROR] Fundamental feed error: {exc}")
                time.sleep(interval * 2)


def launch_daemon(
    api_key: str,
    interval: int = 60,
    redis_host: str = "localhost",
    redis_port: int = 6379,
) -> None:
    daemon = FundamentalRealtimeDaemon(api_key=api_key, redis_host=redis_host, redis_port=redis_port)
    daemon.run(interval=interval)


if __name__ == "__main__":
    launch_daemon(api_key="REAL_KEY", interval=60)
