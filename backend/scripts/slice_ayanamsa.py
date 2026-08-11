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
from app import engine, transit                           # noqa: E402
from app.rules import graph, panchang_rules               # noqa: E402
from compare_ayanamsa import (cast, scores, binom_two_sided,  # noqa: E402
                              wilson, WEIGHTS)
from slice_backtest import fetch_intraday                 # noqa: E402

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]
LORD_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
              "Saturn", "Rahu", "Ketu"]
FAMILIES = ["Nanda", "Bhadra", "Jaya", "Rikta", "Purna"]
SESSION = (9.25, 15.5)
IST = datetime.timezone(datetime.timedelta(hours=5.5))


def thithi_family(num: int) -> str:
    in_paksha = (num - 1) % 15 + 1
    return next((f for f, members, _, _ in panchang_rules.THITHI_FAMILIES
                 if in_paksha in members), "?")


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


def horai_slice():
    """Compare the two ayanamsas at SEGMENT granularity on 60-minute bars.

    The daily test collapses each session to one number, so the two
    ayanamsas can only differ when the whole day's sign flips (12 times in
    5 years). Scoring each hourly bar against the chain segment covering
    it tests the intraday shape directly and gives the ayanamsas far more
    chances to diverge — the fairest test available to them.

    Horai windows are ayanamsa-invariant (horai_timeline takes no ayanamsa
    argument — it depends only on sunrise/sunset and the weekday), so the
    buckets are identical under both and only the segment bias differs.
    """
    bars = fetch_intraday()
    seg_cache, horai_cache = {}, {}
    tagged = []
    for dt, ret in bars:
        d = dt.date()
        mid = dt.hour + dt.minute / 60 + 0.5
        if not (SESSION[0] <= mid <= SESSION[1]):
            continue
        if d not in seg_cache:
            try:
                seg_cache[d] = {
                    m: graph.build_segments(cast(d, m))
                    for m in (engine.KP, engine.LAHIRI)}
                horai_cache[d] = transit.horai_timeline(
                    d.year, d.month, d.day, 5.5, 13.0827, 80.2707)
            except Exception:
                seg_cache[d] = horai_cache[d] = None
        if not seg_cache[d] or not horai_cache[d]:
            continue
        lord = next((s["lord"] for s in horai_cache[d]
                     if s["start"] <= mid < s["end"]), None)
        if lord is None:
            continue

        def bias_at(mode):
            seg = next((s for s in seg_cache[d][mode]
                        if s["start"] <= mid < s["end"]), None)
            return WEIGHTS.get(seg["bias"], 0.0) if seg else 0.0

        tagged.append({"date": d, "lord": lord, "ret": ret, "up": ret > 0,
                       "kp": bias_at(engine.KP),
                       "la": bias_at(engine.LAHIRI)})

    print("\n" + "=" * 84)
    print(f"BY HORAI — {len(tagged)} hourly bars over {len(seg_cache)} "
          f"sessions, scored per SEGMENT")
    print("=" * 84)
    disc_all = [t for t in tagged if t["kp"] != 0 and t["la"] != 0
                and (t["kp"] > 0) != (t["la"] > 0)]
    print(f"  segment directions disagree on {len(disc_all)}/{len(tagged)} "
          f"bars = {len(disc_all)/len(tagged)*100:.1f}%")
    print(f"\n  {'horai':<10s} {'bars':>6s} {'KP hit':>15s} "
          f"{'Lahiri hit':>15s} {'disagree':>9s} {'up-rate':>8s}")
    by_lord = defaultdict(list)
    for t in tagged:
        by_lord[t["lord"]].append(t)
    for lord in LORD_ORDER:
        rs = by_lord.get(lord)
        if not rs:
            continue
        out = []
        for key in ("kp", "la"):
            sel = [t for t in rs if t[key] != 0]
            h = sum(1 for t in sel if (t[key] > 0) == t["up"])
            out.append(f"{h/len(sel)*100:5.1f}% (n={len(sel):4d})"
                       if sel else "        —")
        disc = [t for t in rs if t["kp"] != 0 and t["la"] != 0
                and (t["kp"] > 0) != (t["la"] > 0)]
        up = sum(1 for t in rs if t["up"])
        print(f"  {lord:<10s} {len(rs):6d} {out[0]:>15s} {out[1]:>15s} "
              f"{len(disc):9d} {up/len(rs)*100:7.1f}%")

    for key, name in (("kp", "KP"), ("la", "Lahiri")):
        sel = [t for t in tagged if t[key] != 0]
        h = sum(1 for t in sel if (t[key] > 0) == t["up"])
        print(f"\n  {name:<7s} all bars: {h}/{len(sel)} = "
              f"{h/len(sel)*100:.1f}%")
    if disc_all:
        kp_h = sum(1 for t in disc_all if (t["kp"] > 0) == t["up"])
        la_h = len(disc_all) - kp_h
        print(f"  on the {len(disc_all)} disagreement bars: KP {kp_h}, "
              f"Lahiri {la_h} — exact two-sided p = "
              f"{binom_two_sided(max(kp_h, la_h), len(disc_all)):.3f}")

        # Bars are NOT independent: when a day's segment differs, several
        # consecutive bars inherit the same disagreement AND largely the
        # same market move. Collapse to one vote per session before
        # reading anything into the bar-level split.
        by_day = defaultdict(list)
        for t in disc_all:
            by_day[t["date"]].append(t)
        print(f"\n  BUT those {len(disc_all)} bars fall on only "
              f"{len(by_day)} distinct sessions — they are not independent.")
        print(f"  {'session':<12s} {'bars':>5s}  {'KP right':>9s}   returns")
        wins = 0
        for d in sorted(by_day):
            rs = by_day[d]
            k = sum(1 for t in rs if (t["kp"] > 0) == t["up"])
            wins += k > len(rs) / 2
            print(f"  {d!s:<12s} {len(rs):5d}  {k:4d}/{len(rs):<4d}   "
                  f"{[round(t['ret'], 2) for t in rs]}")
        p = binom_two_sided(max(wins, len(by_day) - wins), len(by_day))
        print(f"\n  one vote per session: KP {wins}, Lahiri "
              f"{len(by_day) - wins} — exact two-sided p = {p:.3f}"
              f"  ({'NOT ' if p >= 0.05 else ''}significant)")
        flat = sum(1 for t in disc_all if abs(t["ret"]) < 0.1)
        print(f"  {flat}/{len(disc_all)} of the disagreement bars moved "
              f"less than 0.1% — the 'wins' are mostly on flat bars.")


def main():
    src = os.path.join(os.path.dirname(__file__), "..", "knowledge",
                       "backtest", "nifty_backtest.csv")
    with open(src, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out = []
    lord_mismatch = 0
    fam_mismatch = [0]
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
        kf = thithi_family(kp_chart["panchang"]["thithi"]["num"])
        lf = thithi_family(la_chart["panchang"]["thithi"]["num"])
        if kf != lf:
            fam_mismatch[0] += 1
        out.append({"date": d, "up": float(r["ret_pct"]) > 0,
                    "ret": float(r["ret_pct"]),
                    "kp_chain": kp_chain, "la_chain": la_chain,
                    "weekday": WEEKDAYS[d.weekday()],
                    "kp_lord": kl, "la_lord": ll, "family": kf})

    n = len(out)
    disc_all = [r for r in out if r["kp_chain"] != 0 and r["la_chain"] != 0
                and (r["kp_chain"] > 0) != (r["la_chain"] > 0)]
    print(f"{n} trading days  ({out[0]['date']} -> {out[-1]['date']})")
    print(f"chain directions disagree on {len(disc_all)} days "
          f"({len(disc_all)/n*100:.1f}%)")
    print(f"NAKSHATRA LORD itself differs on {lord_mismatch} days "
          f"({lord_mismatch/n*100:.1f}%) — the slice variable is not "
          f"ayanamsa-neutral;\n  days are bucketed by the KP lord below.")

    print(f"THITHI FAMILY differs on {fam_mismatch[0]} days — thithi is a "
          f"Moon-MINUS-Sun elongation, so\n  the ayanamsa cancels exactly "
          f"and these buckets are identical under both zodiacs.")

    by_wd = defaultdict(list)
    by_lord = defaultdict(list)
    by_fam = defaultdict(list)
    for r in out:
        by_wd[r["weekday"]].append(r)
        by_lord[r["kp_lord"]].append(r)
        by_fam[r["family"]].append(r)

    table("BY WEEKDAY", by_wd, WEEKDAYS[:5])
    table("BY NAKSHATRA LORD (Moon's star lord at sunrise, KP)",
          by_lord, LORD_ORDER)
    table("BY THITHI FAMILY (identical buckets under both ayanamsas)",
          by_fam, FAMILIES)

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

    horai_slice()


if __name__ == "__main__":
    main()
