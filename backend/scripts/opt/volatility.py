"""Volatility instead of direction — does astrology add anything to it?

Direction is close to a fair coin, so the direction study's benchmark was
the base rate. Volatility is different: it is genuinely predictable.
|ret| has autocorrelation +0.215 at lag 1 and is still +0.146 at lag 10 —
the volatility clustering that every GARCH model exploits. A rolling
21-day mean of |ret| already calls the median split correctly 57.8% of the
time.

That completely changes what a result has to show. An astro model that
scores 58% on this target has demonstrated NOTHING, because lagged
volatility alone scores 58%. The only question worth asking is:

    does adding astro features to a lagged-volatility model
    improve it, on data neither model has seen?

So two models are fitted on identical folds and identical rows, differing
only in whether the astro columns are present, and the reported quantity
is the DELTA with a confidence interval on the delta.

TWO GUARDS AGAINST FOOLING OURSELVES:

1. The target's median is computed inside the TRAINING fold. A global
   median leaks the test period's volatility level backwards.

2. NSE expiry is a large, calendar-driven volatility source. It is put in
   the BASELINE (Model A), not left for the astro block to discover. If a
   thithi effect survives with expiry already controlled, it means
   something; if it vanishes, the finding was the calendar, not the sky.

Rather than searching thousands of variants — the procedure the direction
study exists to discredit — this tests a small PRE-REGISTERED list of
claims the course actually makes, with a Bonferroni correction at the
declared count.

Usage: python scripts/opt/volatility.py
"""
import datetime
import os
import random
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import features as feat                                      # noqa: E402
import stats                                                 # noqa: E402
import tier2                                                 # noqa: E402
import walkforward as wf                                     # noqa: E402

# Declared BEFORE running. Five tests => Bonferroni alpha = 0.05/5 = 0.010.
HYPOTHESES = {
    "Amavasai (new moon, thithi 30)":
        lambda r: r["thithi_num"] == 30,
    "Pournami (full moon, thithi 15)":
        lambda r: r["thithi_num"] == 15,
    "New or full moon (either)":
        lambda r: r["thithi_num"] in (15, 30),
    "Extreme yogas (Vyaghata/Vyatipata/Vaidhriti)":
        lambda r: r["yogam"] in ("Vyaghata", "Vyatipata", "Vaidhriti"),
    "Rikta thithis (4/9/14 in paksha)":
        lambda r: r["thithi_in_paksha"] in (4, 9, 14),
}
N_HYP = len(HYPOTHESES)
ALPHA = 0.05 / N_HYP

WINDOWS = (1, 3, 5, 10, 21)


# ------------------------------------------------------ expiry controls
def _last_thursday(d: datetime.date) -> datetime.date:
    nxt = datetime.date(d.year + (d.month == 12),
                        d.month % 12 + 1, 1)
    last = nxt - datetime.timedelta(days=1)
    while last.weekday() != 3:
        last -= datetime.timedelta(days=1)
    return last


def vol_block(rows) -> np.ndarray:
    """Strictly-lagged volatility + expiry features.

    Every window slices r[max(0, i-w):i] — EXCLUSIVE of bar i. An
    off-by-one here would let today's move predict itself and would
    manufacture the entire result.
    """
    r = np.array([abs(x["ret_pct"]) for x in rows])
    signed = np.array([x["ret_pct"] for x in rows])
    out = []
    for i, row in enumerate(rows):
        d = datetime.date.fromisoformat(row["date"])
        lt = _last_thursday(d)
        feats = []
        for w in WINDOWS:
            feats.append(r[max(0, i - w):i].mean() if i else r[:1].mean())
        feats += [
            signed[i - 1] if i else 0.0,
            r[i - 1] if i else r[0],
            r[max(0, i - 21):i].std() if i > 1 else 0.0,
            float(d.weekday() == 3),               # Thursday = weekly expiry
            float(d == lt),                        # monthly expiry
            float(abs((d - lt).days) <= 1),        # expiry neighbourhood
        ]
        out.append(feats)
    return np.array(out, dtype=float)


# ------------------------------------------------------------- modelling
def _design_astro(rows):
    X_cat = [[str(x[c]) for c in tier2.CAT] for x in rows]
    _c, X_num = tier2.design(rows)
    return X_cat, X_num


def run_models(index="nifty"):
    rows = feat.load(index)
    V = vol_block(rows)
    idx = {r["date"]: i for i, r in enumerate(rows)}

    accs = {"A": [0, 0], "B": [0, 0]}
    paired = []          # (A correct?, B correct?) per out-of-sample bar

    for _y, train, test in wf.folds(rows):
        # target median from the TRAINING window only
        tr_abs = np.array([abs(r["ret_pct"]) for r in train])
        med = float(np.median(tr_abs))
        y_tr = np.array([int(abs(r["ret_pct"]) > med) for r in train])
        y_te = np.array([int(abs(r["ret_pct"]) > med) for r in test])

        Vtr = V[[idx[r["date"]] for r in train]]
        Vte = V[[idx[r["date"]] for r in test]]

        # Model A — lagged volatility + expiry only
        mA = LogisticRegression(C=1.0, max_iter=3000)
        mu, sd = Vtr.mean(0), Vtr.std(0) + 1e-9
        mA.fit((Vtr - mu) / sd, y_tr)
        pA = mA.predict((Vte - mu) / sd)

        # Model B — the same block PLUS every astro feature
        Xc_tr, Xn_tr = _design_astro(train)
        Xc_te, Xn_te = _design_astro(test)
        enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        A_tr = np.hstack([enc.fit_transform(Xc_tr), Xn_tr, Vtr])
        A_te = np.hstack([enc.transform(Xc_te), Xn_te, Vte])
        mu2, sd2 = A_tr.mean(0), A_tr.std(0) + 1e-9
        mB = LogisticRegression(C=0.1, max_iter=3000)
        mB.fit((A_tr - mu2) / sd2, y_tr)
        pB = mB.predict((A_te - mu2) / sd2)

        accs["A"][0] += int((pA == y_te).sum())
        accs["A"][1] += len(y_te)
        accs["B"][0] += int((pB == y_te).sum())
        accs["B"][1] += len(y_te)
        paired.extend(zip(pA == y_te, pB == y_te))

    return accs, paired


def delta_report(accs, paired, label=""):
    hA, n = accs["A"]
    hB, _ = accs["B"]
    a_only = sum(1 for a, b in paired if a and not b)
    b_only = sum(1 for a, b in paired if b and not a)
    p = stats.binom_two_sided(b_only, a_only + b_only)

    # block bootstrap CI on the delta, respecting autocorrelation
    diff = np.array([int(b) - int(a) for a, b in paired])
    rng = random.Random(7)
    boots = []
    blocks = [diff[i:i + 21] for i in range(0, len(diff), 21)]
    for _ in range(2000):
        pick = [blocks[rng.randrange(len(blocks))] for _ in blocks]
        boots.append(np.concatenate(pick).mean())
    lo, hi = np.percentile(boots, [2.5, 97.5]) * 100

    print(f"  {label}")
    print(f"    Model A  lagged volatility + expiry only : "
          f"{hA}/{n} = {hA / n * 100:.2f}%")
    print(f"    Model B  A + every astro feature         : "
          f"{hB}/{n} = {hB / n * 100:.2f}%")
    print(f"    DELTA (astro's contribution)             : "
          f"{(hB - hA) / n * 100:+.2f}pp   95% CI "
          f"[{lo:+.2f}, {hi:+.2f}]")
    print(f"    discordant bars: A-only {a_only}, B-only {b_only}, "
          f"exact McNemar p = {p:.3f}")
    return (hB - hA) / n * 100, lo, hi, p


# ---------------------------------------------- pre-registered hypotheses
def hypothesis_tests(index="nifty"):
    rows = feat.load(index)
    r = np.array([abs(x["ret_pct"]) for x in rows])
    # excess over the lagged 21-day level, so "these days are volatile"
    # cannot be satisfied merely by landing in a volatile stretch
    base = np.array([r[max(0, i - 21):i].mean() if i else r[0]
                     for i in range(len(r))])
    excess = r - base

    rng = random.Random(11)
    print(f"  {N_HYP} pre-registered tests, Bonferroni alpha = {ALPHA:.3f}")
    print(f"  (excess = |ret| minus its own trailing 21-day mean)\n")
    results = []
    for name, fn in HYPOTHESES.items():
        m = np.array([fn(x) for x in rows])
        if m.sum() < 20:
            print(f"    {name}: only {m.sum()} days, skipped")
            continue
        obs = excess[m].mean() - excess[~m].mean()
        # block permutation: shuffle the labels in 21-day blocks
        null = []
        idxs = list(range(len(rows)))
        for _ in range(2000):
            sh = stats.block_shuffle(idxs, 21, rng)
            mm = m[sh]
            null.append(excess[mm].mean() - excess[~mm].mean())
        null = np.array(null)
        p = float((np.abs(null) >= abs(obs)).sum() + 1) / (len(null) + 1)
        flag = "SURVIVES" if p < ALPHA else "no"
        print(f"    {name}")
        print(f"      n={int(m.sum()):4d}  mean |ret| {r[m].mean():.3f}% vs "
              f"{r[~m].mean():.3f}%   excess diff {obs:+.4f}pp  "
              f"p={p:.4f}  {flag}")
        results.append((name, obs, p))
    return results


def main():
    print("=" * 72)
    print("VOLATILITY — does astrology add anything to lagged volatility?")
    print("=" * 72)
    for index in ("nifty", "banknifty"):
        print(f"\n{index.upper()}")
        accs, paired = run_models(index)
        delta_report(accs, paired, f"walk-forward, median split")

    print("\n" + "=" * 72)
    print("PRE-REGISTERED HYPOTHESES (nifty)")
    print("=" * 72)
    hypothesis_tests("nifty")
    print("\n" + "=" * 72)
    print("PRE-REGISTERED HYPOTHESES (banknifty)")
    print("=" * 72)
    hypothesis_tests("banknifty")


if __name__ == "__main__":
    main()
