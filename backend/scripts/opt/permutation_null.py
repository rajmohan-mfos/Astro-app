"""How high does the best-of-N variant score when there is NO signal?

This is the step that makes the rest of the study interpretable. The
search reports the maximum over thousands of variants, and a maximum is
biased upward: run enough variants against noise and one of them looks
brilliant. The only way to know how much of an observed 59% is that
effect is to measure it — run the identical search, same variant count,
same folds, against outcomes that have been shuffled so no relationship
with the astro features can survive.

Shuffling is done in contiguous blocks (default 21 bars, about a trading
month) so that volatility clustering and serial correlation are kept. An
i.i.d. shuffle would make the null too easy to beat and would therefore
overstate the significance of the real result.

Usage: python scripts/opt/permutation_null.py [n_permutations] [block]
"""
import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import features as feat                                      # noqa: E402
import stats                                                 # noqa: E402
import walkforward as wf                                     # noqa: E402

OUT_DIR = os.path.join(HERE, "..", "..", "knowledge", "backtest", "opt")
MIN_CALLS = 500      # a variant that trades 12 days a year proves nothing


def best_rate(hits, tot, min_calls=MIN_CALLS) -> float:
    """Best RAW hit rate. Kept for reference — see best_edge for why this
    one is misleading on its own."""
    ok = tot >= min_calls
    if not ok.any():
        return 0.0
    return float(np.max(hits[ok] / tot[ok]))


def best_edge(hits, tot, downs, min_calls=MIN_CALLS) -> float:
    """Best DIRECTIONAL EDGE — the metric that actually decides.

    Raw hit rate rewards a variant for choosing to trade on days that are
    unusually bearish, which is not forecasting. Subtracting always-down
    on each variant's own traded days leaves only the part that is.
    """
    ok = tot >= min_calls
    if not ok.any():
        return 0.0
    return float(np.max(wf.edge(hits, tot, downs)[ok]))


def run(n_perm: int = 200, block: int = 21, seed: int = 20260813) -> dict:
    rows = feat.load()
    oos = [r for r in rows if r["year"] >= wf.FIRST_TEST_YEAR]
    p0 = wf.base_rate(oos)

    t0 = time.perf_counter()
    masks, hits, tot, downs = wf.best_of_search(rows)
    real_rate = best_rate(hits, tot)
    real_edge = best_edge(hits, tot, downs)
    n_variants = len(hits)
    print(f"real search: {n_variants} variants, best raw "
          f"{real_rate * 100:.2f}%, best edge {real_edge * 100:+.2f}pp "
          f"({time.perf_counter() - t0:.1f}s)")

    ups = [r["up"] for r in rows]
    rng = random.Random(seed)
    null_rate, null_edge = [], []
    for i in range(n_perm):
        shuffled = stats.block_shuffle(ups, block, rng)
        _m, h, t, dn = wf.best_of_search(rows, ups=shuffled)
        null_rate.append(best_rate(h, t))
        null_edge.append(best_edge(h, t, dn))
        if (i + 1) % 20 == 0:
            a = np.array(null_edge)
            print(f"  {i + 1}/{n_perm}  null best EDGE: "
                  f"mean {a.mean() * 100:+.2f}pp  "
                  f"p95 {np.percentile(a, 95) * 100:+.2f}pp", flush=True)

    ar, ae = np.array(null_rate), np.array(null_edge)
    result = {
        "n_variants": n_variants, "n_permutations": n_perm,
        "block": block, "min_calls": MIN_CALLS,
        "always_down": p0 * 100,
        # raw hit rate — reported but NOT the decision metric
        "real_best_rate": real_rate * 100,
        "null_rate_p95": float(np.percentile(ar, 95)) * 100,
        "null_rate_max": float(ar.max()) * 100,
        # directional edge — the decision metric
        "real_best_edge": real_edge * 100,
        "null_edge_mean": float(ae.mean()) * 100,
        "null_edge_p50": float(np.percentile(ae, 50)) * 100,
        "null_edge_p95": float(np.percentile(ae, 95)) * 100,
        "null_edge_max": float(ae.max()) * 100,
        "p_value": float((ae >= real_edge).sum() + 1) / (n_perm + 1),
        "survives": bool(real_edge > np.percentile(ae, 95)),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "permutation_null.json"), "w",
              encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 21
    r = run(n, b)
    print()
    for k, v in r.items():
        print(f"  {k}: {v}")
    print("\n" + ("SURVIVES the null" if r["survives"]
                  else "DOES NOT survive the null — the best variant is "
                       "inside the range luck produces"))
