"""Compare the KP and Lahiri ayanamsas as predictors of Nifty direction.

Both are run through the IDENTICAL rule stack — sunrise cast, degree
counting, the same bias table and panchang tally — so the only difference
is the 0.097 deg zodiac offset. Reuses the dates and open/close from
knowledge/backtest/nifty_backtest.csv (both ayanamsa-independent), so the
sample matches the published RESULTS.md exactly.

The two agree on the overwhelming majority of days, so overall hit rates
are nearly uninformative. The decisive comparison is the DISCORDANT days —
those where the two predict opposite directions — evaluated with an exact
McNemar test, which is the correct test for paired binary outcomes.

Usage: python scripts/compare_ayanamsa.py
"""
import csv
import datetime
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import engine, transit                           # noqa: E402
from app.rules import graph, panchang_rules               # noqa: E402

LAT, LON, TZ = 13.0827, 80.2707, 5.5
WEIGHTS = {"bullish": 1.0, "sideways-bullish": 0.5, "sideways": 0.0,
           "angle": 0.0, "sideways-bearish": -0.5, "bearish": -1.0}
VAL = {"positive": 1, "negative": -1, "very negative": -1, "neutral": 0}


def cast(d: datetime.date, mode: int) -> dict:
    """Sunrise cast on the given ayanamsa — cast_chart with a knob."""
    rise = transit.sunrise_hour(d.year, d.month, d.day, TZ, LAT, LON)
    hh, mm = int(rise), round((rise % 1) * 60)
    if mm == 60:
        hh, mm = hh + 1, 0
    return engine.compute(d.year, d.month, d.day, hh, mm, TZ, LAT, LON,
                          ayanamsa_mode=mode)


def scores(d: datetime.date, mode: int):
    c = cast(d, mode)
    segs = graph.build_segments(c)
    total = sum((s["end"] - s["start"]) * WEIGHTS.get(s["bias"], 0.0)
                for s in segs)
    chain = total / (15.5 - 9.25)
    pan = c["panchang"]
    tally = (VAL[panchang_rules.thithi_bias(pan["thithi"]["num"])[0]]
             + 0.5 * VAL[panchang_rules.yogam_bias(pan["yogam"]["name"])[0]]
             + VAL[panchang_rules.karanam_bias(pan["karanam"]["name"])[0]])
    return chain, tally


def binom_two_sided(b: int, n: int) -> float:
    """Exact two-sided binomial p-value against p=0.5 (McNemar)."""
    if n == 0:
        return 1.0
    def pmf(k):
        return math.comb(n, k) * 0.5 ** n
    obs = pmf(b)
    return min(1.0, sum(pmf(k) for k in range(n + 1)
                        if pmf(k) <= obs + 1e-12))


def wilson(hits: int, n: int) -> tuple[float, float]:
    """95% Wilson score interval, in percent."""
    if n == 0:
        return (0.0, 0.0)
    z, p = 1.96, hits / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return ((c - h) * 100, (c + h) * 100)


def report(label: str, hits: int, n: int):
    if n == 0:
        print(f"{label:46s}      —")
        return
    lo, hi = wilson(hits, n)
    print(f"{label:46s} {hits:4d}/{n:4d} = {hits/n*100:5.1f}%  "
          f"[{lo:4.1f}, {hi:4.1f}]")


def main():
    src = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                       "backtest", "nifty_backtest.csv")
    with open(src, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"{len(rows)} trading days  ({rows[0]['date']} -> {rows[-1]['date']})\n")

    out = []
    for r in rows:
        d = datetime.date.fromisoformat(r["date"])
        ret = float(r["ret_pct"])
        try:
            kp_chain, kp_pan = scores(d, engine.KP)
            la_chain, la_pan = scores(d, engine.LAHIRI)
        except Exception as e:
            print(f"skip {d}: {e}")
            continue
        out.append({"date": d, "ret": ret, "up": ret > 0,
                    "kp_chain": kp_chain, "la_chain": la_chain,
                    "kp_pan": kp_pan, "la_pan": la_pan})

    n = len(out)
    up = sum(1 for r in out if r["up"])
    print(f"BASELINE  share of up days (close > open): "
          f"{up}/{n} = {up/n*100:.1f}%")
    print(f"          always-predict-DOWN scores {(n-up)/n*100:.1f}% "
          f"by doing nothing\n")

    # ---- headline: chain direction -------------------------------------
    print("=" * 78)
    print("CHAIN DIRECTION  (predicted = sign of duration-weighted score)")
    print("=" * 78)
    for key, name in (("kp_chain", "KP"), ("la_chain", "Lahiri")):
        sel = [r for r in out if r[key] != 0]
        hits = sum(1 for r in sel if (r[key] > 0) == r["up"])
        report(f"  {name}: all directional days", hits, len(sel))
    for key, name in (("kp_chain", "KP"), ("la_chain", "Lahiri")):
        sel = [r for r in out if abs(r[key]) >= 0.5]
        hits = sum(1 for r in sel if (r[key] > 0) == r["up"])
        report(f"  {name}: strong days (|score| >= 0.5)", hits, len(sel))

    # ---- agreement and the decisive discordant slice -------------------
    both = [r for r in out if r["kp_chain"] != 0 and r["la_chain"] != 0]
    same_dir = [r for r in both
                if (r["kp_chain"] > 0) == (r["la_chain"] > 0)]
    disc = [r for r in both if (r["kp_chain"] > 0) != (r["la_chain"] > 0)]
    print(f"\n  agree on direction : {len(same_dir)}/{len(both)} = "
          f"{len(same_dir)/len(both)*100:.1f}%")
    print(f"  DISAGREE           : {len(disc)}/{len(both)} = "
          f"{len(disc)/len(both)*100:.1f}%   <- the only days that can "
          f"separate them")
    if disc:
        kp_hits = sum(1 for r in disc if (r["kp_chain"] > 0) == r["up"])
        la_hits = sum(1 for r in disc if (r["la_chain"] > 0) == r["up"])
        print()
        report("    KP on disagreement days", kp_hits, len(disc))
        report("    Lahiri on disagreement days", la_hits, len(disc))
        p = binom_two_sided(max(kp_hits, la_hits), len(disc))
        print(f"    exact McNemar two-sided p = {p:.3f}"
              f"   ({'NOT ' if p >= 0.05 else ''}significant at 0.05)")

    # ---- panchang tally -------------------------------------------------
    print("\n" + "=" * 78)
    print("PANCHANG TALLY  (thithi + 1/2 yogam + karanam)")
    print("=" * 78)
    for key, name in (("kp_pan", "KP"), ("la_pan", "Lahiri")):
        sel = [r for r in out if r[key] != 0]
        hits = sum(1 for r in sel if (r[key] > 0) == r["up"])
        report(f"  {name}: tally sign vs day direction", hits, len(sel))
    pboth = [r for r in out if r["kp_pan"] != 0 and r["la_pan"] != 0]
    pdisc = [r for r in pboth if (r["kp_pan"] > 0) != (r["la_pan"] > 0)]
    print(f"\n  panchang tallies disagree on {len(pdisc)}/{len(pboth)} days "
          f"= {len(pdisc)/len(pboth)*100:.1f}%")
    if pdisc:
        kp_hits = sum(1 for r in pdisc if (r["kp_pan"] > 0) == r["up"])
        la_hits = sum(1 for r in pdisc if (r["la_pan"] > 0) == r["up"])
        report("    KP on disagreement days", kp_hits, len(pdisc))
        report("    Lahiri on disagreement days", la_hits, len(pdisc))
        p = binom_two_sided(max(kp_hits, la_hits), len(pdisc))
        print(f"    exact McNemar two-sided p = {p:.3f}")

    # ---- per year -------------------------------------------------------
    print("\n" + "=" * 78)
    print("PER YEAR (chain direction)")
    print("=" * 78)
    by_year = defaultdict(list)
    for r in out:
        by_year[r["date"].year].append(r)
    print(f"  {'year':6s} {'KP':>16s} {'Lahiri':>16s}")
    for y in sorted(by_year):
        rs = by_year[y]
        line = f"  {y:<6d}"
        for key in ("kp_chain", "la_chain"):
            sel = [r for r in rs if r[key] != 0]
            h = sum(1 for r in sel if (r[key] > 0) == r["up"])
            line += f" {h:4d}/{len(sel):4d}={h/len(sel)*100:5.1f}%" \
                if sel else f"{'—':>16s}"
        print(line)

    dest = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                        "backtest", "ayanamsa_compare.csv")
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "ret_pct", "kp_chain", "la_chain",
                    "kp_panchang", "la_panchang"])
        for r in out:
            w.writerow([r["date"].isoformat(), r["ret"],
                        round(r["kp_chain"], 3), round(r["la_chain"], 3),
                        r["kp_pan"], r["la_pan"]])
    print(f"\nper-day data -> {os.path.normpath(dest)}")


if __name__ == "__main__":
    main()
