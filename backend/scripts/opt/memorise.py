"""100% accuracy on the 15-year Nifty backtest, and what it costs.

This delivers exactly what was asked: astro rules, refined against 15
years of Nifty, until the backtest reads 100%.

It works. The recipe is to make the rule key finer and finer until every
trading day has its own rule:

    thithi                                    30 rules   55.04%
    + yogam                                  807 rules   69.30%
    + karanam                               1528 rules   75.90%
    + nakshatra                             2744 rules   87.26%
    + weekday                               3513 rules   96.06%
    + chain X planet and count              3749 rules   98.93%
    + Moon longitude to 0.01 degrees        3830 rules  100.00%

3,830 rules for 3,830 days. Each one says, in effect, "when the Moon is at
exactly 217.34 degrees on a Wednesday in Vishakha with Vyatipata yoga and
Bava karanam, the market goes up" — because that is what happened the one
time it occurred.

THE POINT OF THIS SCRIPT IS THE SECOND TABLE. Every rule set above is also
run walk-forward: built on the past only, then applied to a year it has
never seen. Accuracy on the backtest climbs to 100%. Accuracy on unseen
days does not climb at all - it falls, because finer rules match fewer
future days and match them for no reason.

That gap is not a flaw in the fitting. It is what "100% on a backtest"
means: the rules stopped describing the market and started describing the
list of days they were built from.

Usage: python scripts/opt/memorise.py
"""
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import features as feat                                      # noqa: E402
import stats                                                 # noqa: E402
import walkforward as wf                                     # noqa: E402

# progressively finer rule keys, coarsest first
LEVELS = [
    ("thithi", lambda r: (r["thithi_num"],)),
    ("+ yogam", lambda r: (r["thithi_num"], r["yogam"])),
    ("+ karanam",
     lambda r: (r["thithi_num"], r["yogam"], r["karanam"])),
    ("+ nakshatra",
     lambda r: (r["thithi_num"], r["yogam"], r["karanam"],
                r["nakshatra"])),
    ("+ weekday",
     lambda r: (r["thithi_num"], r["yogam"], r["karanam"],
                r["nakshatra"], r["weekday"])),
    ("+ chain X planet/count",
     lambda r: (r["thithi_num"], r["yogam"], r["karanam"],
                r["nakshatra"], r["weekday"], r["x_planet"],
                r["x_count"])),
    ("+ Moon longitude (0.01 deg)",
     lambda r: (r["thithi_num"], r["yogam"], r["karanam"],
                r["nakshatra"], r["weekday"], round(r["moon_lon"], 2))),
]


def build_rules(rows, keyfn) -> dict:
    """key -> the direction that happened most often on those days."""
    g = defaultdict(list)
    for r in rows:
        g[keyfn(r)].append(r["up"])
    return {k: (1 if sum(v) * 2 >= len(v) else -1) for k, v in g.items()}


def in_sample(rows, keyfn):
    rules = build_rules(rows, keyfn)
    hits = sum(1 for r in rows
               if rules[keyfn(r)] == (1 if r["up"] else -1))
    return hits, len(rows), len(rules)


def out_of_sample(rows, keyfn):
    """Same rules, built on the past only, applied to the unseen year.

    Days whose signature was never seen before get no rule at all; they
    are counted separately, because "I have no rule for today" is the
    honest outcome and hiding it would flatter the result.
    """
    hits = called = unseen = 0
    for _y, train, test in wf.folds(rows):
        rules = build_rules(train, keyfn)
        for r in test:
            k = keyfn(r)
            if k not in rules:
                unseen += 1
                continue
            called += 1
            hits += rules[k] == (1 if r["up"] else -1)
    return hits, called, unseen


def main():
    rows = feat.load("nifty")
    oos_rows = [r for r in rows if r["year"] >= wf.FIRST_TEST_YEAR]
    p0 = wf.base_rate(oos_rows)

    print("=" * 78)
    print("REFINING THE ASTRO RULES UNTIL THE BACKTEST READS 100%")
    print("=" * 78)
    print(f"{len(rows)} trading days, 2011-01-03 to 2026-08-13\n")

    print(f"{'rule key':<30s} {'rules':>6s}  {'BACKTEST':>9s}   "
          f"{'UNSEEN DAYS':>11s}  {'no rule':>8s}")
    print("-" * 78)
    for name, keyfn in LEVELS:
        h, n, k = in_sample(rows, keyfn)
        oh, on, un = out_of_sample(rows, keyfn)
        oos = f"{oh / on * 100:6.2f}%" if on else "    n/a"
        print(f"{name:<30s} {k:6d}  {h / n * 100:8.2f}%   "
              f"{oos:>11s}  {un / (on + un) * 100:7.1f}%")

    print("-" * 78)
    print(f"{'always-down (no rules at all)':<30s} {0:6d}  "
          f"{'   53.21%':>8s}   {p0 * 100:10.2f}%  {0:7.1f}%")

    print("\nWhat the two columns mean:")
    print("  BACKTEST     the rules scored on the same 15 years they were")
    print("               built from. This is the number that reaches 100%.")
    print("  UNSEEN DAYS  the identical rules, built only from the past and")
    print("               applied to a year they have never met.")

    # the sharpest single statement of the result
    name, keyfn = LEVELS[-1]
    h, n, k = in_sample(rows, keyfn)
    oh, on, un = out_of_sample(rows, keyfn)
    print(f"\nAt the finest level ({k} rules for {n} days):")
    print(f"  backtest      {h}/{n} = {h / n * 100:.2f}%")
    if on:
        lo, hi = stats.wilson(oh, on)
        print(f"  unseen days   {oh}/{on} = {oh / on * 100:.2f}%   "
              f"95% CI [{lo:.1f}, {hi:.1f}]")
    print(f"  and {un} of {on + un} future days "
          f"({un / (on + un) * 100:.1f}%) matched NO rule at all, because "
          f"their exact\n  signature had never occurred before.")
    print("\nThe Moon returns to 217.34 degrees on a Wednesday in Vishakha")
    print("with that yoga and that karanam roughly never. A rule that fires")
    print("once has nothing to predict with.")


if __name__ == "__main__":
    main()
