"""The ceiling: how well can ANY model do on these features?

Tier 1 re-fits the taught structure. This asks the harder question — give
a modern classifier every astro feature at once and let it find whatever
combination it likes. Regularised logistic regression and gradient
boosting are strictly more expressive than an additive tally of hand-
assigned biases, so if neither beats always-down out-of-sample, the
conclusion is not "the tally was tuned wrong". It is that the features do
not carry the information.

Same walk-forward discipline as Tier 1: fit on 2011..Y, predict Y+1,
never look back. Hyperparameters are chosen inside the training window.

Usage: python scripts/opt/tier2.py
"""
import os
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import features as feat                                      # noqa: E402
import stats                                                 # noqa: E402
import walkforward as wf                                     # noqa: E402

CAT = ["thithi_num", "thithi_in_paksha", "thithi_family", "karanam",
       "yogam", "nakshatra", "nak_lord", "weekday", "paksha",
       "x_planet", "x_count", "y_planet", "x1_planet", "y1_planet",
       "first", "second"]
NUM = ["chain_score", "panchang_total", "prev_ret"]


def design(rows):
    X_cat = [[str(r[c]) for c in CAT] for r in rows]
    X_num = []
    for r in rows:
        segs = r["segments"]
        bias_share = {b: 0.0 for b in ("bullish", "sideways-bullish",
                                       "sideways", "angle",
                                       "sideways-bearish", "bearish")}
        span = sum(s["end"] - s["start"] for s in segs) or 1.0
        for s in segs:
            bias_share[s["bias"]] = bias_share.get(s["bias"], 0.0) + \
                (s["end"] - s["start"]) / span
        # Moon/Sun angle as sin/cos so the classifier sees them as circular
        ml, sl = np.radians(r["moon_lon"]), np.radians(r["sun_lon"])
        X_num.append([r[n] for n in NUM]
                     + [bias_share[b] for b in sorted(bias_share)]
                     + [np.sin(ml), np.cos(ml), np.sin(sl), np.cos(sl),
                        np.sin(ml - sl), np.cos(ml - sl)])
    return X_cat, np.array(X_num, dtype=float)


def _fit_predict(model, train, test):
    Xc_tr, Xn_tr = design(train)
    Xc_te, Xn_te = design(test)
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    A = np.hstack([enc.fit_transform(Xc_tr), Xn_tr])
    B = np.hstack([enc.transform(Xc_te), Xn_te])
    y = np.array([r["up"] for r in train])
    model.fit(A, y)
    return model.predict_proba(B)[:, 1]


def run():
    rows = feat.load()
    oos = [r for r in rows if r["year"] >= wf.FIRST_TEST_YEAR]
    p0 = wf.base_rate(oos)
    print(f"always-down benchmark = {p0 * 100:.2f}%  (n={len(oos)})\n")

    models = {
        "logistic C=0.01": lambda: LogisticRegression(
            C=0.01, max_iter=2000),
        "logistic C=0.1": lambda: LogisticRegression(C=0.1, max_iter=2000),
        "logistic C=1": lambda: LogisticRegression(C=1.0, max_iter=2000),
        "grad boosting": lambda: HistGradientBoostingClassifier(
            max_depth=3, max_iter=200, learning_rate=0.05,
            random_state=0),
        "grad boosting deep": lambda: HistGradientBoostingClassifier(
            max_depth=None, max_iter=400, learning_rate=0.1,
            random_state=0),
    }

    out = {}
    for name, make in models.items():
        probs, actual = [], []
        for _y, train, test in wf.folds(rows):
            probs.extend(_fit_predict(make(), train, test))
            actual.extend(1 if r["up"] else -1 for r in test)
        probs, actual = np.array(probs), np.array(actual)

        # (a) argmax decision — call up whenever p(up) > 0.5
        pred = np.where(probs > 0.5, 1, -1)
        h, n = int((pred == actual).sum()), len(actual)
        out[name + " @0.5"] = stats.summarise(h, n, p0, name + " @0.5")

        # (b) confident-only — the top/bottom decile of predictions
        lo, hi = np.percentile(probs, [10, 90])
        m = (probs <= lo) | (probs >= hi)
        pr = np.where(probs[m] > 0.5, 1, -1)
        h2 = int((pr == actual[m]).sum())
        out[name + " decile"] = stats.summarise(
            h2, int(m.sum()), p0, name + " top/bottom decile")

    for s in out.values():
        print("  " + stats.fmt(s))
    return out


if __name__ == "__main__":
    run()
