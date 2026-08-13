"""Statistics for the optimisation study — stdlib only.

The repo already had `wilson` and `binom_two_sided` inside
scripts/compare_ayanamsa.py, but nothing importable for a two-proportion
test, and every sigma figure in RESULTS.md was hand-computed prose rather
than produced by code. This module is the one place those live now.
"""
import math
import random


def wilson(hits: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval, in percent."""
    if n == 0:
        return (0.0, 100.0)
    p = hits / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return ((centre - half) * 100, (centre + half) * 100)


def binom_two_sided(k: int, n: int) -> float:
    """Exact two-sided binomial p-value against p=0.5."""
    if n == 0:
        return 1.0
    def pmf(i):
        return math.comb(n, i) * 0.5 ** n
    obs = pmf(k)
    return min(1.0, sum(pmf(i) for i in range(n + 1)
                        if pmf(i) <= obs * (1 + 1e-12)))


def prop_z(hits: int, n: int, p0: float) -> float:
    """z for an observed rate against a FIXED benchmark p0.

    Used to test a strategy against the always-down base rate. p0 is
    treated as known rather than estimated, which is the right call here:
    the base rate comes from the same 3,800 bars and is not the thing
    under test.
    """
    if n == 0:
        return 0.0
    return (hits / n - p0) / math.sqrt(p0 * (1 - p0) / n)


def block_shuffle(values: list, block: int, rng: random.Random) -> list:
    """Shuffle in contiguous blocks, preserving short-range structure.

    A plain i.i.d. shuffle destroys the volatility clustering and serial
    correlation in daily returns, which makes the null too easy to beat
    and so overstates significance. Moving blocks keep it.
    """
    if block <= 1:
        out = list(values)
        rng.shuffle(out)
        return out
    blocks = [values[i:i + block] for i in range(0, len(values), block)]
    rng.shuffle(blocks)
    out = [v for b in blocks for v in b]
    return out[:len(values)]


def summarise(hits: int, n: int, p0: float, label: str = "") -> dict:
    lo, hi = wilson(hits, n)
    return {"label": label, "hits": hits, "n": n,
            "rate": (hits / n * 100) if n else 0.0,
            "ci_lo": lo, "ci_hi": hi, "z_vs_base": prop_z(hits, n, p0)}


def fmt(s: dict) -> str:
    return (f"{s['label']:<38s} {s['hits']:5d}/{s['n']:<5d} "
            f"{s['rate']:5.2f}%  CI [{s['ci_lo']:5.2f}, {s['ci_hi']:5.2f}]  "
            f"z={s['z_vs_base']:+.2f}")
