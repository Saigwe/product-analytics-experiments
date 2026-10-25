"""Validate the experiment toolkit on real visitors: does it find effects that exist, and only those?

Units are (non-bot) visitors active in the experiment window (the last 28 days of data); the CUPED
covariate is each visitor's own activity in the 28 days before. Assignment is random 50/50.

1. A/A tests     : no effect exists, so ~5% of tests should come out "significant" (false positive rate).
2. Planted lifts : a known relative lift is added to treatment, for conversion (any purchase) and for
                   views per visitor. Reported: average estimated lift, interval coverage of the true
                   effect, and power, with and without CUPED.
3. SRM drill     : treatment loses 2% of units (a logging bug); the sample-ratio check must flag it.
4. Sample sizes  : users per arm needed for given lifts at this conversion rate, vs the traffic available.

Writes results/experiments.md.

Usage
    python analysis/simulate_experiments.py --db warehouse/product.duckdb --sims 500
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.stats import cuped, diff_in_means, guardrail, sample_size_per_arm, srm_check  # noqa: E402


def load_units(db: str) -> pd.DataFrame:
    with duckdb.connect(db, read_only=True) as con:
        return con.execute("""
            with bounds as (select max(activity_date) as last_day from gold.fct_user_day),
            windows as (
                select last_day - interval 27 day as exp_start, last_day as exp_end,
                       last_day - interval 55 day as pre_start, last_day - interval 28 day as pre_end
                from bounds
            ),
            exp as (
                select u.visitor_id, max(case when u.transactions > 0 then 1 else 0 end) as converted,
                       sum(u.views) as views, sum(u.sessions) as sessions
                from gold.fct_user_day u, windows w
                where u.activity_date between w.exp_start and w.exp_end
                group by 1
            ),
            pre as (
                select u.visitor_id, sum(u.views) as pre_views, max(case when u.transactions > 0 then 1 else 0 end) as pre_converted
                from gold.fct_user_day u, windows w
                where u.activity_date between w.pre_start and w.pre_end
                group by 1
            )
            select e.*, coalesce(p.pre_views, 0) as pre_views, coalesce(p.pre_converted, 0) as pre_converted
            from exp e left join pre p on p.visitor_id = e.visitor_id
        """).df()


def plant(y: np.ndarray, arm: np.ndarray, lift: float, binary: bool, rng) -> np.ndarray:
    """Return outcomes with a relative `lift` added to the treatment arm."""
    y = y.astype(float).copy()
    t = arm
    if binary:
        p0 = y[t].mean()
        q = p0 * lift / (1 - p0)                      # flip this share of non-converters -> rate x (1 + lift)
        flip = t & (y == 0) & (rng.random(len(y)) < q)
        y[flip] = 1
    else:
        y[t] = y[t] * (1 + lift)
    return y


def run(df: pd.DataFrame, sims: int, seed: int) -> str:
    rng = np.random.default_rng(seed)
    n = len(df)
    conv, views = df["converted"].to_numpy(float), df["views"].to_numpy(float)
    x_conv, x_views = df["pre_converted"].to_numpy(float), df["pre_views"].to_numpy(float)
    base_rate = conv.mean()
    lines = [f"Units: {n:,} visitors active in the last 28 days (bots excluded); baseline conversion "
             f"{base_rate:.2%}; mean views {views.mean():.2f}. Correlation with pre-period: conversion "
             f"{np.corrcoef(conv, x_conv)[0, 1]:.2f}, views {np.corrcoef(views, x_views)[0, 1]:.2f}. "
             f"{sims} simulations per row.", ""]

    # 1. A/A
    fp = {"conversion": 0, "views": 0, "views (CUPED)": 0}
    srm_flags = 0
    for _ in range(sims):
        arm = rng.random(n) < 0.5
        fp["conversion"] += diff_in_means(conv[~arm], conv[arm]).significant
        fp["views"] += diff_in_means(views[~arm], views[arm]).significant
        adj, _ = cuped(views, x_views)
        fp["views (CUPED)"] += diff_in_means(adj[~arm], adj[arm]).significant
        srm_flags += srm_check([int((~arm).sum()), int(arm.sum())])["mismatch"]
    lines += ["## 1. A/A tests (no real effect)", "", "| Metric | False positive rate (target 5%) |", "|---|---|"]
    lines += [f"| {k} | {v / sims:.1%} |" for k, v in fp.items()]
    lines += [f"| SRM false alarms (threshold p < 0.001) | {srm_flags / sims:.1%} |", ""]

    # 2. Planted lifts
    lines += ["## 2. Planted lifts", "",
              "| Metric | True lift | Mean estimated lift | 95% CI covers truth | Power (raw) | Power (CUPED) | CI width reduction (CUPED) |",
              "|---|---|---|---|---|---|---|"]
    for name, y, x, binary in (("Conversion", conv, x_conv, True), ("Views per visitor", views, x_views, False)):
        for lift in (0.02, 0.05, 0.10):
            est, cover, pw_raw, pw_cuped, width_ratio = [], 0, 0, 0, []
            for _ in range(sims):
                arm = rng.random(n) < 0.5
                yy = plant(y, arm, lift, binary, rng)
                true_diff = yy[arm].mean() - y[arm].mean()   # effect actually planted in this sample
                raw = diff_in_means(yy[~arm], yy[arm])
                adj, _ = cuped(yy, x)
                cu = diff_in_means(adj[~arm], adj[arm])
                est.append(raw.relative_lift)
                cover += raw.ci_low <= true_diff <= raw.ci_high
                pw_raw += raw.significant
                pw_cuped += cu.significant
                width_ratio.append((cu.ci_high - cu.ci_low) / (raw.ci_high - raw.ci_low))
            lines.append(f"| {name} | +{lift:.0%} | {np.mean(est):+.1%} | {cover / sims:.0%} | {pw_raw / sims:.0%} | "
                         f"{pw_cuped / sims:.0%} | {1 - np.mean(width_ratio):.0%} |")
    lines.append("")

    # 3. SRM drill
    arm = rng.random(n) < 0.5
    lost = arm & (rng.random(n) < 0.02)
    kept = ~lost
    srm = srm_check([int((~arm & kept).sum()), int((arm & kept).sum())])
    g = guardrail(views[~arm], views[arm], max_relative_drop=0.02)
    lines += ["## 3. Sample-ratio mismatch drill", "",
              f"Treatment loses 2% of its units (a logging bug): control {int((~arm & kept).sum()):,} vs treatment "
              f"{int((arm & kept).sum()):,}. SRM p-value {srm['p_value']:.2g}: **{'flagged' if srm['mismatch'] else 'not flagged'}**. "
              f"Guardrail on views with no change applied: {'pass' if g['pass'] else 'fail'} "
              f"(worst plausible change {g['worst_plausible']:+.3f} views vs allowed {g['allowed']:+.3f}).", ""]

    # 4. Sample sizes
    per_arm = n // 2
    lines += ["## 4. Sample size at this conversion rate", "",
              "| Relative lift to detect | Users per arm needed | Available per arm (28 days) | Feasible |", "|---|---|---|---|"]
    for lift in (0.02, 0.05, 0.10, 0.20):
        need = sample_size_per_arm(base_rate, lift)
        lines.append(f"| +{lift:.0%} | {need:,} | {per_arm:,} | {'yes' if need <= per_arm else 'no'} |")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default="warehouse/product.duckdb")
    ap.add_argument("--sims", type=int, default=500)
    ap.add_argument("--seed", type=int, default=9)
    ap.add_argument("--out", default=str(ROOT / "results" / "experiments.md"))
    args = ap.parse_args()
    t0 = time.perf_counter()
    body = run(load_units(args.db), args.sims, args.seed)
    text = f"# Experiment toolkit validated on real visitors\n\n{body}\n\nRun time {time.perf_counter() - t0:.0f}s.\n"
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
