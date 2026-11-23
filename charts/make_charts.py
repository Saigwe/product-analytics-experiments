"""README charts from results/experiments.md (written by the experiments step on the real RetailRocket data).
Usage: python charts/make_charts.py [results/experiments.md]"""
import re
import sys
from pathlib import Path

import style as st

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "experiments.md"
OUT = ROOT / "docs" / "charts"


def tables(md: str) -> dict:
    """Markdown tables keyed by the nearest heading above them."""
    out, head, rows = {}, None, []
    for line in md.splitlines() + [""]:
        if line.startswith("#"):
            head = line.lstrip("# ").strip()
        elif line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                rows.append(cells)
        elif rows:
            out[head] = [dict(zip(rows[0], r)) for r in rows[1:]]
            rows = []
    return out


def num(s: str) -> float:
    return float(s.replace("%", "").replace("+", "").replace(",", ""))


t = tables(SRC.read_text(encoding="utf-8"))
lifts = next(v for k, v in t.items() if k.startswith("2."))
views = [r for r in lifts if r["Metric"].startswith("Views")]
conv = [r for r in lifts if r["Metric"].startswith("Conversion")]
f, (a1, a2) = st.plt.subplots(1, 2, figsize=(8, 3.3), dpi=150, sharey=True)
for ax, rows, name in ((a1, conv, "Conversion"), (a2, views, "Views per visitor")):
    xs = range(len(rows))
    b1 = ax.bar([i - 0.2 for i in xs], [num(r["Power (raw)"]) / 100 for r in rows], 0.38, color=st.MUTED, label="Plain t-test")
    b2 = ax.bar([i + 0.2 for i in xs], [num(r["Power (CUPED)"]) / 100 for r in rows], 0.38, color=st.S[0], label="CUPED")
    st.vbar_labels(ax, b1, lambda v: f"{v:.0%}")
    st.vbar_labels(ax, b2, lambda v: f"{v:.0%}")
    ax.set_xticks(list(xs), [f"{r['True lift']} lift" for r in rows])
    ax.set_ylim(0, 1.12)
    st.fmt(ax, "y", "pct")
a1.set_ylabel("Power: share of 500 tests that detect it")
st.head(a1, "Conversion: CUPED can't help", "Pre-period conversion barely predicts it", legend=True)
st.head(a2, "Views: CUPED adds power", "Pre-period views correlate 0.58")
st.save(f, OUT / "power_cuped.png")

ss = next(v for k, v in t.items() if k.startswith("4."))
f, ax = st.fig(8, 3.2)
need = [num(r["Users per arm needed"]) for r in ss]
have = num(ss[0]["Available per arm (28 days)"])
bars = ax.bar(range(len(ss)), need, 0.55, color=[st.S[0] if n <= have else st.MUTED for n in need])
ax.axhline(have, color=st.CRITICAL, lw=1.2, label=f"Visitors available per arm in 28 days: {have:,.0f}")
ax.set_yscale("log")
ax.yaxis.set_major_formatter(st.FuncFormatter(lambda v, _: f"{v:,.0f}"))
st.vbar_labels(ax, bars, lambda v: f"{v:,.0f}")
ax.set_xticks(range(len(ss)), [f"Detect a {r['Relative lift to detect']} lift" for r in ss])
st.head(ax, "At a 0.78% conversion rate, only a 20% lift is testable in a month",
        "Users per arm needed for 80% power (log scale)", legend=True)
st.save(f, OUT / "sample_size.png")
print(f"wrote charts to {OUT}")
