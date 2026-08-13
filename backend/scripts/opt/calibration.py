"""Does recentring the panchang tally fix anything?

Not part of the variant search. This one experiment has a reason that is
independent of the target, so running it is not fitting: the panchang
tally is structurally biased bullish. In a recent 80-day scan 64 of 80
tallies were positive, and 138 of 152 HIGH-conviction days in the 5-year
study were bullish calls — against a market that closes below its open
53% of the time. The course's bias tables simply classify far more days
auspicious than inauspicious, so the engine can barely emit a strong
bearish call.

The question this separates: is the engine wrong because its THRESHOLD is
misplaced (fixable) or because its SIGNAL is empty (not fixable)? If
recentring moves the call distribution to roughly 50/50 without moving
accuracy, it is the second.

Usage: python scripts/opt/calibration.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import features as feat                                      # noqa: E402
import stats                                                 # noqa: E402
import walkforward as wf                                     # noqa: E402


def run():
    rows = feat.load()
    oos = [r for r in rows if r["year"] >= wf.FIRST_TEST_YEAR]
    p0 = wf.base_rate(oos)
    print(f"always-down benchmark = {p0 * 100:.2f}%\n")

    variants = {}

    # (a) as shipped
    raw_pred, raw_act = [], []
    # (b) recentred on the TRAINING window's own mean (no leakage)
    cen_pred = []
    # (c) recentred to match the training window's down-rate by quantile
    qnt_pred = []

    for _y, train, test in wf.folds(rows):
        tr = np.array([r["panchang_total"] for r in train])
        te = np.array([r["panchang_total"] for r in test])
        mu = tr.mean()
        # quantile shift: put the cut where the training up-rate says it
        # belongs, so the call mix matches the market's actual mix
        up_rate = sum(r["up"] for r in train) / len(train)
        cut = float(np.quantile(tr, 1 - up_rate))

        raw_pred.extend(np.where(te > 0.25, 1, np.where(te < -0.25, -1, 0)))
        cen_pred.extend(np.where(te - mu > 0, 1, -1))
        qnt_pred.extend(np.where(te > cut, 1, -1))
        raw_act.extend(1 if r["up"] else -1 for r in test)

    act = np.array(raw_act)
    for name, pred in (("panchang as shipped", np.array(raw_pred)),
                       ("recentred on train mean", np.array(cen_pred)),
                       ("quantile-matched cut", np.array(qnt_pred))):
        m = pred != 0
        h, n = int((pred[m] == act[m]).sum()), int(m.sum())
        bull = int((pred == 1).sum())
        s = stats.summarise(h, n, p0, name)
        variants[name] = s
        print("  " + stats.fmt(s)
              + f"   bullish calls {bull / len(pred) * 100:5.1f}%")

    print(f"\n  (market itself is bullish on "
          f"{sum(r['up'] for r in oos) / len(oos) * 100:.1f}% of days)")
    return variants


if __name__ == "__main__":
    run()
