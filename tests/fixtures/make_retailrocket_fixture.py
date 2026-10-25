"""Write a small RetailRocket-format events.csv for CI (same columns and units as the real file).

Visitors browse in sessions (gaps under 30 minutes inside a session, hours or days between them),
add to cart sometimes and buy less often; some come back on later days; one bot-like visitor views
thousands of items a day (the real data has these too, and the models flag them).

Usage
    python tests/fixtures/make_retailrocket_fixture.py --out data/fixture/events.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

START_MS = 1_430_622_000_000  # 2015-05-03, when the real dataset starts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("data/fixture/events.csv"))
    ap.add_argument("--visitors", type=int, default=6000)
    ap.add_argument("--days", type=int, default=70)
    ap.add_argument("--seed", type=int, default=808)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    rows, txn = [], 0
    for v in range(args.visitors):
        first_day = rng.integers(0, args.days)
        engaged = rng.random() < 0.25
        n_sessions = 1 + (rng.poisson(3) if engaged else rng.poisson(0.3))
        day = first_day
        for _ in range(n_sessions):
            if day >= args.days:
                break
            t = START_MS + int(day) * 86_400_000 + int(rng.integers(0, 86_400_000))
            for _ in range(1 + rng.poisson(2.5)):
                item = int(rng.integers(1, 5000))
                rows.append((t, v, "view", item, None))
                if rng.random() < 0.06:
                    t += int(rng.integers(5_000, 300_000))
                    rows.append((t, v, "addtocart", item, None))
                    if rng.random() < 0.35:
                        txn += 1
                        t += int(rng.integers(30_000, 900_000))
                        rows.append((t, v, "transaction", item, txn))
                t += int(rng.integers(10_000, 600_000))          # < 30 min: same session
            day += int(rng.integers(1, 15))                       # next session another day
    bot = args.visitors + 1                                       # one crawler-like visitor
    for d in range(5):
        base = START_MS + d * 86_400_000
        rows += [(base + i * 20_000, bot, "view", int(i % 5000), None) for i in range(3000)]

    df = pd.DataFrame(rows, columns=["timestamp", "visitorid", "event", "itemid", "transactionid"])
    df["transactionid"] = df["transactionid"].astype("Int64")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.sort_values("timestamp").to_csv(args.out, index=False)
    print(f"wrote {len(df):,} events for {df.visitorid.nunique():,} visitors to {args.out}")


if __name__ == "__main__":
    main()
