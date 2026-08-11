"""Backtest the intraday prediction engine against Nifty 50 daily data.

For each trading day: the sunrise-cast chain segments give a duration-
weighted day score (bullish +1, sideways-bullish +0.5, sideways/angle 0,
sideways-bearish -0.5, bearish -1). Predicted direction = sign(score).
Actual direction = sign(close - open) — the session shape the graph
claims to predict. Educational evaluation only.

Usage: python scripts/backtest_nifty.py [years] [place] [index]
  place = chennai (default) | mumbai
  index = nifty (default) | banknifty | metal | pharma | defence

Chennai is the default so the published RESULTS.md tables stay
reproducible; Mumbai matches the app's own default cast location (the NSE
is there). Each (place, index) pair writes its own CSV, so no run
overwrites another.
"""
import csv
import json
import os
import sys
import urllib.request
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import engine                                  # noqa: E402
from app.rules import graph, panchang_rules             # noqa: E402

PLACES = {"chennai": (13.0827, 80.2707), "mumbai": (19.076, 72.8777)}
INDICES = {
    "nifty": "%5ENSEI",
    "banknifty": "%5ENSEBANK",
    "metal": "%5ECNXMETAL",
    "pharma": "%5ECNXPHARMA",
    # The Nifty India Defence index was launched in 2024 and Yahoo serves
    # no usable history for it (one bar). MODEFENCE.NS is the Motilal
    # Oswal ETF tracking that index — a PROXY, and only from 2024-08-26,
    # so its sample is ~40% of the others'.
    "defence": "MODEFENCE.NS",
}
LAT, LON, TZ = 13.0827, 80.2707, 5.5      # set from argv in main()
WEIGHTS = {"bullish": 1.0, "sideways-bullish": 0.5, "sideways": 0.0,
           "angle": 0.0, "sideways-bearish": -0.5, "bearish": -1.0}


def fetch_nifty(years: int, symbol: str = "%5ENSEI"):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?range={years}y&interval=1d")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    res = data["chart"]["result"][0]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    days = []
    import datetime
    for t, o, c in zip(ts, q["open"], q["close"]):
        if o is None or c is None:
            continue
        d = datetime.datetime.fromtimestamp(t,
            datetime.timezone(datetime.timedelta(hours=5.5))).date()
        days.append((d, o, c))
    return days


def day_prediction(d):
    chart = engine.compute(d.year, d.month, d.day, 9, 15, TZ, LAT, LON)
    cast = graph.cast_chart(chart)
    segs = graph.build_segments(cast)
    total = sum((s["end"] - s["start"]) * WEIGHTS.get(s["bias"], 0.0)
                for s in segs)
    score = total / (15.5 - 9.25)
    pan = chart["panchang"]
    t_bias = panchang_rules.thithi_bias(pan["thithi"]["num"])[0]
    y_bias = panchang_rules.yogam_bias(pan["yogam"]["name"])[0]
    k_bias = panchang_rules.karanam_bias(pan["karanam"]["name"])[0]
    # combined panchang tally: thithi + yogam (half weight, per the guide)
    # + karanam, each +1/-1
    val = {"positive": 1, "negative": -1, "very negative": -1, "neutral": 0}
    pan_score = (val[t_bias] + 0.5 * val[y_bias] + val[k_bias])
    return score, t_bias, y_bias, pan_score


def main():
    global LAT, LON
    years = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    place = (sys.argv[2] if len(sys.argv) > 2 else "chennai").lower()
    if place not in PLACES:
        raise SystemExit(f"place must be one of {sorted(PLACES)}")
    index = (sys.argv[3] if len(sys.argv) > 3 else "nifty").lower()
    if index not in INDICES:
        raise SystemExit(f"index must be one of {sorted(INDICES)}")
    LAT, LON = PLACES[place]
    days = fetch_nifty(years, INDICES[index])
    print(f"{len(days)} trading days fetched "
          f"({days[0][0]} → {days[-1][0]})  index={index}  place={place} "
          f"({LAT}, {LON})")

    rows = []
    for d, o, c in days:
        try:
            score, t_bias, y_bias, pan_score = day_prediction(d)
        except Exception as e:
            print(f"skip {d}: {e}")
            continue
        ret = (c - o) / o * 100
        rows.append({"date": d.isoformat(), "open": round(o, 2),
                     "close": round(c, 2), "ret_pct": round(ret, 3),
                     "score": round(score, 3), "thithi_bias": t_bias,
                     "yogam_bias": y_bias, "panchang_score": pan_score})

    out_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                           "backtest")
    os.makedirs(out_dir, exist_ok=True)
    # the original Chennai/Nifty run keeps its filename so RESULTS.md and
    # the slice scripts that read it stay valid
    name = ("nifty_backtest.csv" if (place == "chennai" and index == "nifty")
            else f"{index}_backtest_{place}.csv")
    path = os.path.join(out_dir, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path}\n")

    def hit_rate(sel, label):
        n = len(sel)
        if n == 0:
            print(f"{label:44s}    —")
            return
        hits = sum(1 for r in sel
                   if (r["score"] > 0) == (r["ret_pct"] > 0))
        print(f"{label:44s} {hits:4d}/{n:4d} = {hits / n * 100:5.1f}%")

    directional = [r for r in rows if r["score"] != 0]
    up_days = sum(1 for r in rows if r["ret_pct"] > 0)
    print(f"baseline: up days (close>open)          "
          f"    {up_days:4d}/{len(rows):4d} = {up_days / len(rows) * 100:5.1f}%")
    hit_rate(directional, "engine direction, all directional days")
    hit_rate([r for r in directional if abs(r["score"]) >= 0.5],
             "engine direction, strong days (|score|>=.5)")
    hit_rate([r for r in directional if abs(r["ret_pct"]) >= 0.25],
             "engine direction, |actual move| >= 0.25%")

    print()
    for key in ("thithi_bias", "yogam_bias"):
        for bias, want in (("positive", 1), ("negative", -1),
                           ("very negative", -1)):
            sel = [r for r in rows if r[key] == bias]
            if sel:
                hits = sum(1 for r in sel if (r["ret_pct"] > 0) == (want > 0))
                label = f"{key.split('_')[0]} {bias} ({len(sel)})"
                print(f"{label:44s} matched = {hits / len(sel) * 100:5.1f}%")

    print()
    for lo, hi, label in ((0.5, 9, "panchang tally >= +0.5 (should be up)"),
                          (-9, -0.5, "panchang tally <= -0.5 (should be down)")):
        sel = [r for r in rows if lo <= r["panchang_score"] <= hi]
        if sel:
            want_up = lo > 0
            hits = sum(1 for r in sel if (r["ret_pct"] > 0) == want_up)
            print(f"{label:44s} {hits:4d}/{len(sel):4d} = "
                  f"{hits / len(sel) * 100:5.1f}%")

    combo = [r for r in directional
             if (r["score"] > 0) == (r["panchang_score"] > 0)
             and r["panchang_score"] != 0]
    if combo:
        hits = sum(1 for r in combo if (r["score"] > 0) == (r["ret_pct"] > 0))
        print(f"{'chain AND panchang agree (confluence)':44s} "
              f"{hits:4d}/{len(combo):4d} = {hits / len(combo) * 100:5.1f}%")

    by_year = defaultdict(list)
    for r in directional:
        by_year[r["date"][:4]].append(r)
    print()
    for y in sorted(by_year):
        hit_rate(by_year[y], f"  {y}")


if __name__ == "__main__":
    main()
