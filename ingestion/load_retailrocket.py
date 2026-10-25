"""Load RetailRocket `events.csv` into DuckDB `bronze.events`.

RetailRocket's public dataset: 4.5 months of real behaviour from an e-commerce site.
Columns: timestamp (ms since epoch), visitorid, event (view | addtocart | transaction), itemid, transactionid.
Source (free sign-in): https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset
Licence: CC BY-NC-SA 4.0. Save the file as data/raw/events.csv.

Usage
    python ingestion/load_retailrocket.py --db warehouse/product.duckdb --csv data/raw/events.csv
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import duckdb

EXPECTED = ["timestamp", "visitorid", "event", "itemid", "transactionid"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default="warehouse/product.duckdb")
    ap.add_argument("--csv", default="data/raw/events.csv")
    args = ap.parse_args()
    csv = Path(args.csv)
    if not csv.exists():
        raise SystemExit(f"{csv} not found: download RetailRocket from Kaggle (see this file's docstring).")

    t0 = time.perf_counter()
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(args.db) as con:
        cols = [d[0] for d in con.execute(f"select * from read_csv('{csv.as_posix()}', header=true) limit 0").description]
        if cols != EXPECTED:
            raise SystemExit(f"unexpected columns {cols}")
        con.execute("create schema if not exists bronze")
        con.execute(f"""
            create or replace table bronze.events as
            select cast(timestamp as bigint) as timestamp, cast(visitorid as bigint) as visitorid,
                   event, cast(itemid as bigint) as itemid, cast(transactionid as bigint) as transactionid
            from read_csv('{csv.as_posix()}', header=true)""")
        rows, visitors = con.execute("select count(*), count(distinct visitorid) from bronze.events").fetchone()
        kinds = dict(con.execute("select event, count(*) from bronze.events group by 1").fetchall())
    print(f"bronze.events {rows:,} rows, {visitors:,} visitors, {kinds} in {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
