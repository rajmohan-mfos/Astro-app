"""Re-fit the astro engine's OWN tables from 15 years of Nifty.

This replaces the course's hand-assigned numbers with numbers learned from
the market, keeping the taught STRUCTURE exactly: the same five tables the
engine already has, in the same shape, just with fitted values.

  STAR_VALUE      9 nakshatra lords        Mercury +1.0, Saturn -1.0, ...
  CHAIN_WEIGHTS   6 segment bias labels    bullish +1.0, bearish -1.0, ...
  thithi bias     30 thithis               Rikta negative, Pournami positive
  yogam bias      27 yogas                 the 16/8/3 classification
  karanam bias    11 karanams              movable positive, fixed negative

plus the combination weights and the decision threshold, tuned to maximise
accuracy.

READ THE OUTPUT HONESTLY. Fitting a table on the same data you score it
against always looks good, and this is deliberately tuned to look as good
as it can. The script therefore ALWAYS prints both numbers:

  IN-SAMPLE      fitted and scored on all 15 years. Flattering. Not a
                 forecast of anything.
  OUT-OF-SAMPLE  the identical procedure, re-fitted inside each expanding
                 walk-forward window and scored on the year it has never
                 seen. This is the only one that estimates future
                 accuracy, and it lands near the 53% always-down base
                 rate, as OPTIMISATION.md predicts.

The gap between them is the point of the exercise.

Usage: python scripts/opt/fit_tables.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))

import features as feat                                      # noqa: E402
import stats                                                 # noqa: E402
import walkforward as wf                                     # noqa: E402

OUT = os.path.join(HERE, "..", "..", "app", "rules",
                   "fitted_tables.json")

# The five taught tables, each as (name, key function).
TABLES = {
    "star_value": lambda r: r["nak_lord"],
    "chain_weights": None,          # handled separately: per-segment
    "thithi": lambda r: str(r["thithi_num"]),
    "yogam": lambda r: r["yogam"],
    "karanam": lambda r: r["karanam"],
}
COMPONENTS = ["star_value", "chain_weights", "thithi", "yogam", "karanam"]


def _logodds(rows, keyfn, smoothing=0.0) -> dict:
    """Empirical log-odds of an up day per level, vs the overall base.

    smoothing=0 is the maximum-fit setting the brief asks for; the
    walk-forward pass uses the same value so the comparison is fair.
    """
    n_up = sum(r["up"] for r in rows)
    base = n_up / len(rows)
    buckets = {}
    for r in rows:
        b = buckets.setdefault(keyfn(r), [0, 0])
        b[0] += r["up"]
        b[1] += 1
    out = {}
    for k, (up, tot) in buckets.items():
        p = (up + smoothing * base) / (tot + smoothing)
        p = min(max(p, 1e-6), 1 - 1e-6)
        out[k] = round(math.log(p / (1 - p)) - math.log(base / (1 - base)), 4)
    return out


def fit_chain_weights(rows, smoothing=0.0) -> dict:
    """One weight per segment bias label, from duration-weighted exposure.

    A day's chain score is sum(duration * weight) / span, so each label's
    fitted weight is the log-odds of an up day on the days that label
    dominates the session.
    """
    buckets = {}
    for r in rows:
        segs = r["segments"]
        if not segs:
            continue
        span = sum(s["end"] - s["start"] for s in segs) or 1.0
        # attribute the day to whichever label holds the most session time
        share = {}
        for s in segs:
            share[s["bias"]] = share.get(s["bias"], 0.0) + \
                (s["end"] - s["start"]) / span
        top = max(share, key=share.get)
        b = buckets.setdefault(top, [0, 0])
        b[0] += r["up"]
        b[1] += 1
    base = sum(r["up"] for r in rows) / len(rows)
    out = {}
    for k, (up, tot) in buckets.items():
        p = (up + smoothing * base) / (tot + smoothing)
        p = min(max(p, 1e-6), 1 - 1e-6)
        out[k] = round(math.log(p / (1 - p)) - math.log(base / (1 - base)), 4)
    return out


def fit_all(rows, smoothing=0.0) -> dict:
    tables = {"chain_weights": fit_chain_weights(rows, smoothing)}
    for name, keyfn in TABLES.items():
        if keyfn is not None:
            tables[name] = _logodds(rows, keyfn, smoothing)
    return tables


def score_rows(rows, tables, comp_w) -> np.ndarray:
    """The engine's tally, with fitted numbers in place of taught ones."""
    out = np.zeros(len(rows))
    for i, r in enumerate(rows):
        segs = r["segments"]
        chain = 0.0
        if segs:
            span = sum(s["end"] - s["start"] for s in segs) or 1.0
            for s in segs:
                chain += ((s["end"] - s["start"]) / span) * \
                    tables["chain_weights"].get(s["bias"], 0.0)
        out[i] = (
            comp_w["star_value"] * tables["star_value"].get(
                r["nak_lord"], 0.0)
            + comp_w["chain_weights"] * chain
            + comp_w["thithi"] * tables["thithi"].get(
                str(r["thithi_num"]), 0.0)
            + comp_w["yogam"] * tables["yogam"].get(r["yogam"], 0.0)
            + comp_w["karanam"] * tables["karanam"].get(r["karanam"], 0.0))
    return out


def tune_weights(rows, tables, min_calls=400):
    """Coordinate ascent on in-sample accuracy — maximise, as asked."""
    y = np.array([1 if r["up"] else -1 for r in rows])
    w = {c: 1.0 for c in COMPONENTS}
    best_acc, best_th = -1.0, 0.0
    for _sweep in range(4):
        for c in COMPONENTS:
            for cand in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0):
                trial = dict(w, **{c: cand})
                s = score_rows(rows, tables, trial)
                for th in np.arange(0.0, 2.0, 0.05):
                    p = np.where(s > th, 1, np.where(s < -th, -1, 0))
                    m = p != 0
                    if m.sum() < min_calls:
                        break
                    acc = (p[m] == y[m]).mean()
                    if acc > best_acc:
                        best_acc, best_th, w = acc, float(th), trial
    return w, best_th, best_acc


def evaluate(rows, tables, w, th, label):
    y = np.array([1 if r["up"] else -1 for r in rows])
    s = score_rows(rows, tables, w)
    p = np.where(s > th, 1, np.where(s < -th, -1, 0))
    m = p != 0
    h, n = int((p[m] == y[m]).sum()), int(m.sum())
    all_p = np.where(s > 0, 1, -1)
    print(f"  {label}")
    print(f"    all days           {int((all_p == y).sum())}/{len(y)} = "
          f"{(all_p == y).mean() * 100:.2f}%")
    print(f"    |score| > {th:.2f}      {h}/{n} = {h / n * 100:.2f}%"
          f"   ({n / len(y) * 100:.0f}% of days)")
    return h, n


def main():
    rows = feat.load("nifty")
    print("=" * 70)
    print("RE-FITTING THE ASTRO ENGINE'S TABLES FROM 15 YEARS OF NIFTY")
    print("=" * 70)

    # ---------------- in-sample: fit and score on everything
    tables = fit_all(rows, smoothing=0.0)
    w, th, _ = tune_weights(rows, tables)
    print("\nIN-SAMPLE (fitted and scored on the same 15 years)")
    print("  -- flattering by construction; not a forecast --")
    ih, inn = evaluate(rows, tables, w, th, "tuned engine")

    # ---------------- out-of-sample: identical procedure, walk-forward
    print("\nOUT-OF-SAMPLE (same procedure, re-fitted inside each fold)")
    print("  -- the only number that estimates future accuracy --")
    y_all, p_all = [], []
    for _yr, train, test in wf.folds(rows):
        t = fit_all(train, smoothing=0.0)
        ww, tt, _ = tune_weights(train, t)
        s = score_rows(test, t, ww)
        p_all.extend(np.where(s > tt, 1, np.where(s < -tt, -1, 0)))
        y_all.extend(1 if r["up"] else -1 for r in test)
    y_all, p_all = np.array(y_all), np.array(p_all)
    m = p_all != 0
    oh, on = int((p_all[m] == y_all[m]).sum()), int(m.sum())
    down = float((y_all[m] == -1).mean())
    print(f"  tuned engine        {oh}/{on} = {oh / on * 100:.2f}%")
    print(f"  always-down on the SAME days   {down * 100:.2f}%")
    print(f"  edge {(oh / on - down) * 100:+.2f}pp   "
          f"z={stats.prop_z(oh, on, down):+.2f}")

    payload = {
        "version": 1,
        "fitted_on": "nifty 2011-01-03..2026-08-13 (3830 bars)",
        "smoothing": 0.0,
        "tables": tables,
        "component_weights": w,
        "threshold": th,
        "in_sample": {"hits": ih, "n": inn, "rate": ih / inn * 100},
        "out_of_sample": {"hits": oh, "n": on, "rate": oh / on * 100,
                          "always_down_same_days": down * 100,
                          "edge_pp": (oh / on - down) * 100},
        "warning": ("These values are FITTED to historical Nifty. The "
                    "in-sample rate is not a forecast. Out-of-sample this "
                    "engine performs at the always-down base rate."),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    print(f"\nwrote {OUT}")

    print("\nWHERE THE DATA DISAGREES WITH THE COURSE")
    from app.rules import dayscore as ds
    for lord, taught in sorted(ds.TAUGHT_STAR_VALUE.items()):
        got = tables["star_value"].get(lord)
        if got is None:
            continue
        if (taught > 0) != (got > 0) and abs(taught) > 0:
            print(f"  {lord:<8s} course {taught:+.1f}  data {got:+.3f}"
                  f"   <-- opposite sign")


if __name__ == "__main__":
    main()
