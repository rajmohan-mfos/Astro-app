"""Train and export the volatility model that app/volmodel.py serves.

This is the one thing in the whole study that WORKS, so it gets the
opposite treatment from the astro engine: instead of hunting for a reason
to believe it, the job here is to state precisely how much it is worth.

WHAT IT IS. Six features — the mean daily high-low range over the previous
1, 3, 5, 10, 21 and 63 sessions — into a logistic regression predicting
whether today's |close-open| lands above the training window's median.
That is all. No astrology; the astro features were measured to make this
model significantly WORSE (OPTIMISATION.md section 9).

WHY RANGE AND NOT |ret|. Decided before any accuracy was computed: the
high-low range correlates +0.314 with tomorrow's |ret|, against +0.215 for
|ret| itself, because a range uses the whole session rather than two
points of it. The accuracy comparison came afterwards and agreed
(+1.38pp paired, p=0.030). Adding |ret| back on top of range is worth
+0.46pp, CI [-0.53, +1.41], p=0.356 — nothing — so it is left out.

TRAINING IS OFFLINE ON PURPOSE. sklearn is a study-only dependency
(requirements-research.txt). The runtime in app/volmodel.py is pure
stdlib and reads the exported JSON, so the API and the PythonAnywhere bot
stay dependency-light and the deploy zip does not grow.

Usage: python scripts/opt/train_volmodel.py
"""
import json
import os
import random
import sys

import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression

CONFIDENCES = (0.80, 0.90, 0.95)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))

import prices                                                # noqa: E402
import stats                                                 # noqa: E402
from app import volmodel                                     # noqa: E402

WEIGHTS_PATH = os.path.join(HERE, "..", "..", "app",
                            "volmodel_weights.json")
FIRST_TEST_YEAR = 2016


def series(index="nifty"):
    bars = prices.load(index)
    o = np.array([b["open"] for b in bars])
    c = np.array([b["close"] for b in bars])
    absret = np.abs((c - o) / o * 100)
    years = np.array([int(b["date"][:4]) for b in bars])
    X = np.array([volmodel.features(bars, i) for i in range(len(bars))])
    return bars, X, absret, years


def walk_forward(X, absret, years):
    """Concatenated out-of-sample probabilities. Never looks forward."""
    P, Y, YR = [], [], []
    for y in range(FIRST_TEST_YEAR, int(years.max()) + 1):
        tr, te = years < y, years == y
        if not te.any() or not tr.any():
            continue
        med = float(np.median(absret[tr]))
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        m = LogisticRegression(C=1.0, max_iter=4000)
        m.fit((X[tr] - mu) / sd, (absret[tr] > med).astype(int))
        P.extend(m.predict_proba((X[te] - mu) / sd)[:, 1])
        Y.extend((absret[te] > med).astype(int))
        YR.extend(years[te])
    return np.array(P), np.array(Y), np.array(YR)


def calibration_report(P, Y, YR):
    """Accuracy is not the deliverable — calibration is.

    A 60% classifier is only usable as context if a stated 70% actually
    resolves near 70%. Brier score plus a five-bin reliability curve.
    """
    pred = (P > 0.5).astype(int)
    acc = (pred == Y).mean()
    brier = float(np.mean((P - Y) ** 2))
    # Brier for a model that always predicts the base rate
    base = float(np.mean((Y.mean() - Y) ** 2))
    print(f"  accuracy {acc * 100:.2f}%   Brier {brier:.4f}  "
          f"(base-rate model {base:.4f}, lower is better)")
    print(f"  Brier skill score vs base rate: "
          f"{(1 - brier / base) * 100:+.1f}%")

    print("\n  reliability (does a stated probability mean what it says?)")
    edges = [0.0, 0.35, 0.45, 0.55, 0.65, 1.01]
    for lo, hi in zip(edges, edges[1:]):
        m = (P >= lo) & (P < hi)
        if m.sum() < 20:
            continue
        print(f"    predicted {lo:.2f}-{hi:.2f}  n={int(m.sum()):5d}  "
              f"mean stated {P[m].mean() * 100:5.1f}%  "
              f"actually wide {Y[m].mean() * 100:5.1f}%")

    print("\n  accuracy by year (does it decay?)")
    for y in sorted(set(YR.tolist())):
        m = YR == y
        print(f"    {y}  {int((pred[m] == Y[m]).sum()):3d}/{int(m.sum()):3d}"
              f" = {(pred[m] == Y[m]).mean() * 100:5.1f}%")
    return acc, brier


def paired_vs(X_alt, X, absret, years, label):
    pa, Y, _ = walk_forward(X_alt, absret, years)
    pb, _, _ = walk_forward(X, absret, years)
    a, b = ((pa > 0.5).astype(int) == Y), ((pb > 0.5).astype(int) == Y)
    ao, bo = int((a & ~b).sum()), int((b & ~a).sum())
    d = b.astype(int) - a.astype(int)
    rng = random.Random(5)
    blocks = [d[i:i + 21] for i in range(0, len(d), 21)]
    boots = [np.concatenate([blocks[rng.randrange(len(blocks))]
                             for _ in blocks]).mean() for _ in range(2000)]
    lo, hi = np.percentile(boots, [2.5, 97.5]) * 100
    print(f"  vs {label}: {(b.mean() - a.mean()) * 100:+.2f}pp  "
          f"95% CI [{lo:+.2f}, {hi:+.2f}]  "
          f"McNemar p={stats.binom_two_sided(bo, ao + bo):.3f}")


def band_walk_forward(X, absret, years, conf):
    """Out-of-sample coverage and width of the adaptive band.

    The band is q * scale(today), where scale is a linear fit of |ret| on
    the range features and q is the conf-quantile of |ret|/scale measured
    on the TRAINING window only. Both parts are refitted per fold.
    """
    band, act, scale = [], [], []
    for y in range(FIRST_TEST_YEAR, int(years.max()) + 1):
        tr, te = years < y, years == y
        if not te.any() or not tr.any():
            continue
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        reg = LinearRegression().fit((X[tr] - mu) / sd, absret[tr])
        s_tr = np.maximum(reg.predict((X[tr] - mu) / sd), 1e-3)
        s_te = np.maximum(reg.predict((X[te] - mu) / sd), 1e-3)
        q = float(np.quantile(absret[tr] / s_tr, conf))
        band.extend(q * s_te)
        act.extend(absret[te])
        scale.extend(s_te)
    return np.array(band), np.array(act), np.array(scale)


def report_band(X, absret, years):
    """Coverage, width, and the comparison that justifies the whole idea."""
    out = {}
    for conf in CONFIDENCES:
        band, act, scale = band_walk_forward(X, absret, years, conf)
        realised = float((act <= band).mean())
        # a FIXED band tuned on the test set to the same realised
        # coverage — deliberately generous to the alternative
        fixed = float(np.quantile(act, realised))
        print(f"\n  target {conf * 100:.0f}%  ->  realised "
              f"{realised * 100:.2f}%   mean width ±{band.mean():.3f}%")
        print(f"    fixed band at identical coverage: ±{fixed:.3f}%  "
              f"— adaptive is {(1 - band.mean() / fixed) * 100:.1f}% "
              f"narrower")
        t1, t2 = np.quantile(scale, [1 / 3, 2 / 3])
        print("    coverage by regime (this is the real argument):")
        for name, m in (("calm    ", scale <= t1),
                        ("normal  ", (scale > t1) & (scale <= t2)),
                        ("volatile", scale > t2)):
            print(f"      {name} adaptive {(act[m] <= band[m]).mean() * 100:5.1f}%"
                  f" (±{band[m].mean():.2f}%)    "
                  f"fixed {(act[m] <= fixed).mean() * 100:5.1f}% "
                  f"(±{fixed:.2f}%)")
        out[f"{conf:.2f}"] = {
            "target": conf * 100, "realised": realised * 100,
            "mean_width_pct": float(band.mean()),
            "fixed_width_pct": fixed,
        }
    return out


def main():
    print("=" * 68)
    print("VOLATILITY MODEL — walk-forward evaluation")
    print("=" * 68)
    results = {}
    for index in ("nifty", "banknifty"):
        bars, X, absret, years = series(index)
        print(f"\n{index.upper()}  ({len(bars)} bars)")
        P, Y, YR = walk_forward(X, absret, years)
        acc, brier = calibration_report(P, Y, YR)
        results[index] = {"accuracy": acc * 100, "brier": brier,
                          "n": int(len(Y))}

    # sensitivity: the alternatives, all within noise of each other
    bars, X, absret, years = series("nifty")
    print("\nSENSITIVITY (nifty) — feature-set alternatives")
    o = np.array([b["open"] for b in bars])
    ar = absret
    W = volmodel.WINDOWS
    X_ret = np.array([[ar[max(0, i - w):i].mean() if i else 0.0
                       for w in W] for i in range(len(bars))])
    paired_vs(X_ret, X, absret, years, "|ret|-only (the earlier Model A)")
    X_both = np.hstack([X_ret, X])
    paired_vs(X, X_both, absret, years,
              "range-only (i.e. what adding |ret| back buys)")

    print("\n" + "=" * 68)
    print("BAND FORECAST — 'today stays within ±X%'")
    print("=" * 68)
    bars, X, absret, years = series("nifty")
    band_stats = report_band(X, absret, years)

    # ---- final fit on ALL data, exported for the runtime
    med = float(np.median(absret))
    mu, sd = X.mean(0), X.std(0) + 1e-9
    clf = LogisticRegression(C=1.0, max_iter=4000)
    clf.fit((X - mu) / sd, (absret > med).astype(int))
    # a companion regression for the expected range, in percent
    rngs = np.array([volmodel.day_range_pct(bars, i)
                     for i in range(len(bars))])
    reg = LinearRegression().fit((X - mu) / sd, rngs)

    # scale model for the band: |ret| from the same features, plus the
    # quantiles of |ret| / scale that turn a scale into an interval
    scale_reg = LinearRegression().fit((X - mu) / sd, absret)
    s_all = np.maximum(scale_reg.predict((X - mu) / sd), 1e-3)
    ratios = absret / s_all
    ratio_q = {f"{c:.2f}": float(np.quantile(ratios, c))
               for c in CONFIDENCES}

    payload = {
        "version": 1,
        "trained_through": bars[-1]["date"],
        "index": "nifty",
        "windows": list(W),
        "median_abs_ret_pct": med,
        "mu": mu.tolist(), "sd": sd.tolist(),
        "coef": clf.coef_[0].tolist(),
        "intercept": float(clf.intercept_[0]),
        "range_coef": reg.coef_.tolist(),
        "range_intercept": float(reg.intercept_),
        "scale_coef": scale_reg.coef_.tolist(),
        "scale_intercept": float(scale_reg.intercept_),
        "ratio_quantiles": ratio_q,
        "band_oos": band_stats,
        "oos": results,
        "note": ("Predicts whether |close-open| exceeds the historical "
                 "median. Says nothing about DIRECTION. Not a trading "
                 "signal."),
    }
    with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\nwrote {WEIGHTS_PATH}")
    print(f"  trained through {payload['trained_through']}, "
          f"median |ret| = {med:.3f}%")

    # parity check: the stdlib scorer must reproduce sklearn exactly
    ref = clf.predict_proba((X - mu) / sd)[:, 1]
    got = np.array([volmodel.probability_wide(bars, i, payload)
                    for i in range(len(bars))])
    worst = float(np.max(np.abs(ref - got)))
    print(f"  stdlib scorer vs sklearn: max abs diff {worst:.2e}")
    assert worst < 1e-9, "stdlib scorer does not reproduce sklearn"


if __name__ == "__main__":
    main()
