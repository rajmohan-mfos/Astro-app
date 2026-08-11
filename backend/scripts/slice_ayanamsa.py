"""Slice the KP-vs-Lahiri comparison by weekday and by nakshatra lord.

Reuses the cast/score helpers from compare_ayanamsa.py so both scripts
score days identically.

Two cautions the output repeats, because they govern how the tables can
be read:

1. The two ayanamsas disagree on only ~1% of days, so slicing spreads 12
   discordant days across 5 weekdays or 9 lords. Per-bucket discordant
   counts are 0-3 and support no inference whatsoever. The per-bucket HIT
   RATES (n~200 weekday, n~130 lord) are worth showing; the per-bucket
   winner is not.

2. The nakshatra lord is ITSELF ayanamsa-dependent — the Moon can sit in
   different nakshatras under the two zodiacs, so a day can land in
   different buckets. Days are bucketed by the KP lord (the production
   method) and the disagreement rate is reported separately.

Usage: python scripts/slice_ayanamsa.py
"""
import csv
import datetime
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from app import engine                                    # noqa: E402
from app.rules import graph                               # noqa: E402
from compare_ayanamsa import (cast, scores, binom_two_sided,  # noqa: E402
                              wilson)

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]
LORD_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
              "Saturn", "Rahu", "Ketu"]


def nak_lord(chart: dict) -> str:
    moon = next(g for g in chart["grahas"] if g["name"] == "Moon")
    return graph.nak_lord_of(moon["lon"])


def table(title: str, buckets: dict, order: list):
    print("\n" + "=" * 84)
    print(title)
    print("=" * 84)
    print(f"  {'bucket':<11s} {'n':>5s} {'KP hit':>15s} {'Lahiri hit':>15s} "
          f"{'disagree':>9s} {'up-rate':>8s}")
    for key in order:
        rs = buckets.get(key)
        if not rs:
            continue
        kp_sel = [r for r in rs if r["kp_chain"] != 0]
        la_sel = [r for r in rs if r["la_chain"] != 0]
        kp_h = sum(1 for r in kp_sel if (r["kp_chain"] > 0) == r["up"])
        la_h = sum(1 for r in la_sel if (r["la_chain"] > 0) == r["up"])
        disc = [r for r in rs if r["kp_chain"] != 0 and r["la_chain"] != 0
                and (r["kp_chain"] > 0) != (r["la_chain"] > 0)]
        up = sum(1 for r in rs if r["up"])
        kp_s = f"{kp_h/len(kp_sel)*100:5.1f}% (n={len(kp_sel):3d})" \
            if kp_sel else "        —"
        la_s = f"{la_h/len(la_sel)*100:5.1f}% (n={len(la_sel):3d})" \
            if la_sel else "        —"
        print(f"  {key:<11s} {len(rs):5d} {kp_s:>15s} {la_s:>15s} "
              f"{len(disc):9d} {up/len(rs)*100:7.1f}%")


def main():
    src = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                       "backtest", "nifty_backtest.csv")
    with open(src, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out = []
    lord_mismatch = 0
    for r in rows:
        d = datetime.date.fromisoformat(r["date"])
        try:
            kp_chart, la_chart = cast(d, engine.KP), cast(d, engine.LAHIRI)
            kp_chain, _ = scores(d, engine.KP)
            la_chain, _ = scores(d, engine.LAHIRI)
        except Exception as e:
            print(f"skip {d}: {e}")
            continue
        kl, ll = nak_lord(kp_chart), nak_lord(la_chart)
        if kl != ll:
            lord_mismatch += 1
        out.append({"date": d, "up": float(r["ret_pct"]) > 0,
                    "ret": float(r["ret_pct"]),
                    "kp_chain": kp_chain, "la_chain": la_chain,
                    "weekday": WEEKDAYS[d.weekday()],
                    "kp_lord": kl, "la_lord": ll})

    n = len(out)
    disc_all = [r for r in out if r["kp_chain"] != 0 and r["la_chain"] != 0
                and (r["kp_chain"] > 0) != (r["la_chain"] > 0)]
    print(f"{n} trading days  ({out[0]['date']} -> {out[-1]['date']})")
    print(f"chain directions disagree on {len(disc_all)} days "
          f"({len(disc_all)/n*100:.1f}%)")
    print(f"NAKSHATRA LORD itself differs on {lord_mismatch} days "
          f"({lord_mismatch/n*100:.1f}%) — the slice variable is not "
          f"ayanamsa-neutral;\n  days are bucketed by the KP lord below.")

    by_wd = defaultdict(list)
    by_lord = defaultdict(list)
    for r in out:
        by_wd[r["weekday"]].append(r)
        by_lord[r["kp_lord"]].append(r)

    table("BY WEEKDAY", by_wd, WEEKDAYS[:5])
    table("BY NAKSHATRA LORD (Moon's star lord at sunrise, KP)",
          by_lord, LORD_ORDER)

    # where do the 12 discordant days actually fall?
    print("\n" + "=" * 84)
    print("THE DISCORDANT DAYS — every day the two methods disagree")
    print("=" * 84)
    print(f"  {'date':<12s} {'weekday':<10s} {'KP lord':<9s} "
          f"{'La lord':<9s} {'KP':>6s} {'Lahiri':>7s} {'ret%':>7s} {'winner'}")
    kp_w = la_w = 0
    for r in sorted(disc_all, key=lambda x: x["date"]):
        kp_ok = (r["kp_chain"] > 0) == r["up"]
        win = "KP" if kp_ok else "Lahiri"
        kp_w += kp_ok
        la_w += not kp_ok
        print(f"  {r['date']!s:<12s} {r['weekday']:<10s} {r['kp_lord']:<9s} "
              f"{r['la_lord']:<9s} {r['kp_chain']:+6.2f} "
              f"{r['la_chain']:+7.2f} {r['ret']:+7.2f} {win}")
    print(f"\n  KP wins {kp_w}, Lahiri wins {la_w} — exact two-sided "
          f"p = {binom_two_sided(max(kp_w, la_w), len(disc_all)):.3f}")

    print("\n" + "-" * 84)
    print("READING THIS: the discordant column sums to "
          f"{len(disc_all)} across all buckets. Any per-bucket")
    print("difference between the KP and Lahiri hit rates is driven by at "
          "most a handful of")
    print("days and is not evidence of anything. The hit-rate columns are "
          "each ~±7pp at these")
    print("sample sizes, and 14 more comparisons have just been added to "
          "the ~30 in RESULTS.md.")


if __name__ == "__main__":
    main()
