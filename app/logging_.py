"""One redacted JSON line per request in logs/requests-YYYYMMDD.jsonl (FR-5)."""
import json
import os
import pathlib
from datetime import datetime, timezone


def write(rec: dict) -> None:
    now = datetime.now(timezone.utc)
    rec = {"ts": now.isoformat(), **rec}
    rec["cost_usd_notional"] = (
        rec["tokens_in"] / 1000 * float(os.getenv("PRICE_IN_PER_1K", "0.0005"))
        + rec["tokens_out"] / 1000 * float(os.getenv("PRICE_OUT_PER_1K", "0.0015"))
    )
    path = pathlib.Path("logs") / f"requests-{now:%Y%m%d}.jsonl"
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
