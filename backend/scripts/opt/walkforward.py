"""Walk-forward evaluation. The only numbers that count are out-of-sample.

The rule this module exists to enforce: a model may never see a bar from
its own test fold, directly or indirectly. Folds expand forward — fit on
2011..Y, test on Y+1 — and every table a variant uses is fitted inside the
training window only. test_walkforward.py asserts the no-leakage property
directly, because a leak here would silently invalidate every result in
the study and would look like success while doing it.

Two protocols are run, and they answer different questions:

  NESTED   The honest single number. Inside each training window an inner
           validation split picks one variant; that variant alone predicts
           the test fold. This is what you would actually have traded,
           knowing only the past.

  BEST-OF  The optimistic number. Every variant is scored out-of-sample
           and the best is reported. This is NOT a performance estimate —
           picking the max over N variants inflates it. It is only
           interpretable against the permutation null in
           permutation_null.py, which measures how high that maximum goes
           on data with no signal in it at all.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import features as feat                                      # noqa: E402
import stats                                                 # noqa: E402

FIRST_TEST_YEAR = 2016          # 2011-2015 is the initial training window


# ---------------------------------------------------------------- groups
# A "group" is one categorical view of a day. Each contributes an additive
# log-odds term fitted on the training window only.

def _chain_bucket(r):
    c = r["chain_score"]
    if c > 0.25:
        return "chain+"
    if c < -0.25:
        return "chain-"
    return "chain0"


def _pan_bucket(r):
    p = r["panchang_total"]
    if p >= 2:
        return "pan++"
    if p > 0.25:
        return "pan+"
    if p < -0.25:
        return "pan-"
    return "pan0"


def _seg_first(r):
    segs = r["segments"]
    return f"seg1:{segs[0]['bias']}" if segs else "seg1:none"


GROUPS = {
    "thithi": lambda r: f"t{r['thithi_num']}",
    "thithi_paksha": lambda r: f"tp{r['thithi_in_paksha']}",
    "thithi_family": lambda r: r["thithi_family"],
    "karanam": lambda r: r["karanam"],
    "yogam": lambda r: r["yogam"],
    "nakshatra": lambda r: r["nakshatra"],
    "nak_lord": lambda r: r["nak_lord"],
    "weekday": lambda r: f"wd{r['weekday']}",
    "paksha": lambda r: r["paksha"],
    "chain": _chain_bucket,
    "panchang": _pan_bucket,
    "x_planet": lambda r: f"x:{r['x_planet']}",
    "x_count": lambda r: f"xc:{r['x_count']}",
    "y_planet": lambda r: f"y:{r['y_planet']}",
    "first_seg": _seg_first,
}
GROUP_NAMES = list(GROUPS)


# ------------------------------------------------------------- log-odds
def fit_group(train_rows, keyfn, smoothing: float) -> dict:
    """level -> log-odds of 'up', shrunk toward the training base rate.

    Shrinkage is what stops a level seen 4 times in training from
    dominating. m=0 would be raw empirical rates, i.e. maximum overfit.
    """
    n_up = sum(r["up"] for r in train_rows)
    n = len(train_rows)
    base = n_up / n if n else 0.5
    buckets = {}
    for r in train_rows:
        k = keyfn(r)
        b = buckets.setdefault(k, [0, 0])
        b[0] += r["up"]
        b[1] += 1
    out = {}
    for k, (up, tot) in buckets.items():
        p = (up + smoothing * base) / (tot + smoothing)
        p = min(max(p, 1e-6), 1 - 1e-6)
        out[k] = math.log(p / (1 - p)) - math.log(base / (1 - base))
    return out


def folds(rows, first_test_year: int = FIRST_TEST_YEAR):
    """Expanding-window (train, test) splits, one test fold per year."""
    years = sorted({r["year"] for r in rows})
    for y in years:
        if y < first_test_year:
            continue
        train = [r for r in rows if r["year"] < y]
        test = [r for r in rows if r["year"] == y]
        if train and test:
            yield y, train, test


# ------------------------------------------------------------- baselines
def baseline_preds(rows, kind: str, train=None):
    if kind == "always_down":
        return np.full(len(rows), -1)
    if kind == "always_up":
        return np.full(len(rows), 1)
    if kind == "momentum":
        return np.array([1 if r["prev_ret"] > 0 else -1 for r in rows])
    if kind == "contrarian":
        return np.array([-1 if r["prev_ret"] > 0 else 1 for r in rows])
    if kind == "current_engine":
        # sign(chain_score), exactly what the app ships today
        return np.array([1 if r["chain_score"] > 0
                         else (-1 if r["chain_score"] < 0 else 0)
                         for r in rows])
    if kind == "current_dayscore":
        # the panchang/chain combination, direction from the panchang sign
        out = []
        for r in rows:
            c, p = r["chain_score"], r["panchang_total"]
            if abs(c) <= 0.25 or abs(p) <= 0.25:
                out.append(0)
            elif (c > 0) == (p > 0):
                out.append(1 if p > 0 else -1)
            else:
                out.append(0)
        return np.array(out)
    raise ValueError(kind)


def score(preds, rows) -> tuple[int, int]:
    """(hits, n) over directional calls only."""
    actual = np.array([1 if r["up"] else -1 for r in rows])
    mask = preds != 0
    return int((preds[mask] == actual[mask]).sum()), int(mask.sum())


# ------------------------------------------------- variant score matrix
def contribution_matrix(train, test, smoothing: float) -> np.ndarray:
    """(len(test), n_groups) log-odds contributions, fitted on train only."""
    M = np.zeros((len(test), len(GROUP_NAMES)))
    for gi, name in enumerate(GROUP_NAMES):
        keyfn = GROUPS[name]
        table = fit_group(train, keyfn, smoothing)
        M[:, gi] = [table.get(keyfn(r), 0.0) for r in test]
    return M


def variant_masks(max_groups: int = 3) -> list[tuple[int, ...]]:
    """All group subsets up to max_groups, plus the all-groups model."""
    import itertools
    out = []
    idx = range(len(GROUP_NAMES))
    for k in range(1, max_groups + 1):
        out.extend(itertools.combinations(idx, k))
    out.append(tuple(idx))
    return out


SMOOTHINGS = (1.0, 5.0, 20.0, 50.0)
THRESHOLDS = (0.0, 0.05, 0.15)


def variant_label(mask, sm, th) -> str:
    return f"[{'+'.join(GROUP_NAMES[i] for i in mask)}] m={sm:g} t={th:g}"


def _apply(scores: np.ndarray, th: float) -> np.ndarray:
    p = np.zeros(len(scores), dtype=int)
    p[scores > th] = 1
    p[scores < -th] = -1
    return p


def best_of_search(rows, max_groups=3, smoothings=SMOOTHINGS,
                   thresholds=THRESHOLDS, ups=None):
    """Score EVERY variant out-of-sample; return per-variant (hits, n).

    `ups` overrides the labels (used by the permutation null to re-run the
    identical search against shuffled outcomes).
    """
    masks = variant_masks(max_groups)
    nv = len(masks) * len(smoothings) * len(thresholds)
    hits = np.zeros(nv, dtype=int)
    tot = np.zeros(nv, dtype=int)
    downs = np.zeros(nv, dtype=int)

    if ups is not None:
        rows = [dict(r, up=u) for r, u in zip(rows, ups)]

    for _y, train, test in folds(rows):
        actual = np.array([1 if r["up"] else -1 for r in test])
        vi = 0
        for sm in smoothings:
            M = contribution_matrix(train, test, sm)
            for mask in masks:
                s = M[:, list(mask)].sum(axis=1)
                for th in thresholds:
                    p = _apply(s, th)
                    m = p != 0
                    hits[vi] += int((p[m] == actual[m]).sum())
                    tot[vi] += int(m.sum())
                    # actual down days among the ones this variant trades:
                    # the always-down score on its OWN sample
                    downs[vi] += int((actual[m] == -1).sum())
                    vi += 1
    return masks, hits, tot, downs


def edge(hits, tot, downs):
    """Hit rate MINUS always-down on the variant's own traded days.

    A variant that trades only days that happen to fall 58% of the time
    scores 58% by predicting 'down' every time, with no directional skill
    whatsoever. Comparing its raw rate against the all-days benchmark
    (53%) credits it with 5 points it did not earn. This is the metric
    that removes day-selection and leaves only skill.
    """
    t = np.maximum(tot, 1)
    return hits / t - downs / t


def nested_walkforward(rows, max_groups=3, smoothings=SMOOTHINGS,
                       thresholds=THRESHOLDS):
    """The honest protocol: variant chosen inside the training window only.

    Inner split = the last training year is held out for selection. The
    winning variant is then refitted on the full training window and used
    once, on the untouched test fold.
    """
    masks = variant_masks(max_groups)
    all_hits = all_n = 0
    picks, per_year = [], []

    for y, train, test in folds(rows):
        inner_years = sorted({r["year"] for r in train})
        cut = inner_years[-1]
        inner_train = [r for r in train if r["year"] < cut]
        inner_val = [r for r in train if r["year"] == cut]
        if not inner_train or not inner_val:
            continue

        val_actual = np.array([1 if r["up"] else -1 for r in inner_val])
        best = (-1.0, None)
        for sm in smoothings:
            M = contribution_matrix(inner_train, inner_val, sm)
            for mask in masks:
                s = M[:, list(mask)].sum(axis=1)
                for th in thresholds:
                    p = _apply(s, th)
                    m = p != 0
                    n = int(m.sum())
                    if n < 40:            # too few calls to select on
                        continue
                    rate = float((p[m] == val_actual[m]).sum()) / n
                    if rate > best[0]:
                        best = (rate, (mask, sm, th))
        if best[1] is None:
            continue

        mask, sm, th = best[1]
        M = contribution_matrix(train, test, sm)
        p = _apply(M[:, list(mask)].sum(axis=1), th)
        actual = np.array([1 if r["up"] else -1 for r in test])
        m = p != 0
        h, n = int((p[m] == actual[m]).sum()), int(m.sum())
        all_hits += h
        all_n += n
        picks.append((y, variant_label(mask, sm, th), best[0]))
        per_year.append((y, h, n))

    return all_hits, all_n, picks, per_year


def base_rate(rows) -> float:
    """P(down) — the always-down benchmark every model must beat."""
    return 1 - sum(r["up"] for r in rows) / len(rows)


if __name__ == "__main__":
    rows = feat.load()
    oos = [r for r in rows if r["year"] >= FIRST_TEST_YEAR]
    p0 = base_rate(oos)
    print(f"{len(rows)} bars, {len(oos)} out-of-sample "
          f"({FIRST_TEST_YEAR}-)   always-down = {p0 * 100:.2f}%\n")

    print("BASELINES (out-of-sample window)")
    for kind in ("always_down", "always_up", "momentum", "contrarian",
                 "current_engine", "current_dayscore"):
        h, n = score(baseline_preds(oos, kind), oos)
        print("  " + stats.fmt(stats.summarise(h, n, p0, kind)))

