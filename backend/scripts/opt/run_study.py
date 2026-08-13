"""Produce every number in knowledge/backtest/opt/OPTIMISATION.md.

One entry point so the report is reproducible: `python scripts/opt/run_study.py`
regenerates the whole thing from the cached price series and feature table,
with no network access and no dependence on the wall-clock date.

The permutation null is the slow part and is run separately
(permutation_null.py), since it re-runs the entire search a few hundred
times; this script reads its saved JSON.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import calibration                                           # noqa: E402
import features as feat                                      # noqa: E402
import stats                                                 # noqa: E402
import tier2                                                 # noqa: E402
import walkforward as wf                                     # noqa: E402

OUT_DIR = os.path.join(HERE, "..", "..", "knowledge", "backtest", "opt")


def selected_benchmark(preds, rows) -> tuple[int, int, int]:
    """(hits, n, downs) — downs is always-down ON THE TRADED DAYS.

    Comparing a selective strategy's hit rate against the all-days base
    rate is the mistake this study nearly made: a variant that trades only
    on unusually bearish days scores well by predicting down every time.
    """
    actual = np.array([1 if r["up"] else -1 for r in rows])
    m = np.asarray(preds) != 0
    p = np.asarray(preds)[m]
    a = actual[m]
    return int((p == a).sum()), int(m.sum()), int((a == -1).sum())


def section(title):
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def main():
    for index in ("nifty", "banknifty"):
        rows = feat.load(index)
        oos = [r for r in rows if r["year"] >= wf.FIRST_TEST_YEAR]
        p0 = wf.base_rate(oos)

        section(f"{index.upper()}  —  {len(rows)} bars "
                f"{rows[0]['date']} .. {rows[-1]['date']}")
        print(f"out-of-sample window: {len(oos)} bars "
              f"({wf.FIRST_TEST_YEAR}-), always-down = {p0 * 100:.2f}%\n")

        print("BASELINES")
        for kind in ("always_down", "always_up", "momentum", "contrarian",
                     "current_engine", "current_dayscore"):
            h, n, dn = selected_benchmark(
                wf.baseline_preds(oos, kind), oos)
            bench = dn / n if n else 0.5
            print(f"  {kind:<22s} {h:5d}/{n:<5d} {h / n * 100:6.2f}%  "
                  f"same-day always-down {bench * 100:6.2f}%  "
                  f"edge {(h / n - bench) * 100:+6.2f}pp  "
                  f"z={stats.prop_z(h, n, bench):+.2f}")

        print("\nNESTED WALK-FORWARD (variant chosen inside training only)")
        h, n, picks, per_year = wf.nested_walkforward(rows)
        print(f"  {h}/{n} = {h / n * 100:.2f}%   "
              f"CI {['%.2f' % v for v in stats.wilson(h, n)]}   "
              f"vs all-days always-down {p0 * 100:.2f}%  "
              f"z={stats.prop_z(h, n, p0):+.2f}")
        print("  variant selected per year (inner-validation rate -> OOS):")
        for (y, lab, vr), (_y2, hh, nn) in zip(picks, per_year):
            print(f"    {y}  val {vr * 100:5.1f}%  ->  OOS "
                  f"{hh / nn * 100:5.1f}%  {lab}")

        print("\nBEST-OF SEARCH (optimistic; interpret only vs the null)")
        masks, hits, tot, downs = wf.best_of_search(rows)
        ok = tot >= 500
        rate = hits / np.maximum(tot, 1)
        edge = wf.edge(hits, tot, downs)
        bi = int(np.argmax(np.where(ok, rate, -1)))
        ei = int(np.argmax(np.where(ok, edge, -9)))
        print(f"  variants scored: {len(hits)} "
              f"({int(ok.sum())} with >=500 calls)")
        print(f"  best RAW rate  {rate[bi] * 100:6.2f}%  n={tot[bi]}  "
              f"but same-day always-down = "
              f"{downs[bi] / tot[bi] * 100:.2f}%  "
              f"-> edge {edge[bi] * 100:+.2f}pp")
        print(f"  best EDGE      {edge[ei] * 100:+6.2f}pp  n={tot[ei]}  "
              f"(raw {rate[ei] * 100:.2f}%)")
        print(f"  median variant edge: {np.median(edge[ok]) * 100:+.2f}pp")

    section("CALIBRATION EXPERIMENT (nifty)")
    calibration.run()

    section("TIER 2 — CEILING MODELS (nifty)")
    tier2.run()

    path = os.path.join(OUT_DIR, "permutation_null.json")
    if os.path.exists(path):
        section("PERMUTATION NULL")
        with open(path, encoding="utf-8") as f:
            for k, v in json.load(f).items():
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
