"""Volatility context: is today likely to be a wide session or a narrow one?

READ THIS BEFORE USING THE NUMBER.

This model works, which makes it more dangerous to misread than the astro
engine ever was. What it does:

  * It predicts whether |close - open| will land ABOVE or BELOW the
    historical median daily move. That is a two-way split of session
    width, nothing finer.
  * It is right about 60% of the time out-of-sample over 2016-2026.

What it does NOT do, at all:

  * It says NOTHING about direction. A "wide day" is equally likely to be
    wide up or wide down; the direction study found no method of calling
    that better than a coin (OPTIMISATION.md).
  * It is not a trading signal and must never be wired to an order system.
    60% on a binary split of volatility is ordinary — volatility
    clustering is one of the oldest known properties of markets and every
    GARCH textbook exploits it. It is context for reading the day, not an
    edge.
  * It carries no astrology. The panchang and chain features were
    measured to make this model significantly WORSE (-5.05pp on Nifty,
    -4.09pp on BankNifty, both p<0.001), so none of them are in it.

Six features: mean daily high-low range over the previous 1, 3, 5, 10, 21
and 63 sessions. Coefficients are trained offline by
scripts/opt/train_volmodel.py and loaded from volmodel_weights.json, so
this module stays stdlib-only and the deploy zip stays small.
"""
import json
import math
import os

WINDOWS = (1, 3, 5, 10, 21, 63)
MAX_LOOKBACK = max(WINDOWS)
_WEIGHTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "volmodel_weights.json")
_cache = None


def weights() -> dict:
    global _cache
    if _cache is None:
        with open(_WEIGHTS_FILE, encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def day_range_pct(bars: list, i: int) -> float:
    """High-low range of bar i as a percent of its open."""
    b = bars[i]
    if not b.get("high") or not b.get("low") or not b.get("open"):
        return 0.0
    return (b["high"] - b["low"]) / b["open"] * 100


def features(bars: list, i: int) -> list:
    """Mean range over each window, using ONLY bars strictly before i.

    The slice is bars[i-w : i] — bar i is excluded. If it were included,
    today's own range would predict today's own width and the model would
    score near-perfectly while being worthless.
    """
    out = []
    for w in WINDOWS:
        lo = max(0, i - w)
        window = [day_range_pct(bars, j) for j in range(lo, i)]
        out.append(sum(window) / len(window) if window else 0.0)
    return out


def _scale(x: list, w: dict) -> list:
    return [(v - m) / s for v, m, s in zip(x, w["mu"], w["sd"])]


def probability_wide(bars: list, i: int, w: dict | None = None) -> float:
    """P(|close-open| of bar i exceeds the historical median)."""
    w = w or weights()
    z = _scale(features(bars, i), w)
    s = w["intercept"] + sum(c * v for c, v in zip(w["coef"], z))
    return 1.0 / (1.0 + math.exp(-s))


def expected_range_pct(bars: list, i: int, w: dict | None = None) -> float:
    """Expected high-low range for bar i, in percent of open."""
    w = w or weights()
    z = _scale(features(bars, i), w)
    return w["range_intercept"] + sum(
        c * v for c, v in zip(w["range_coef"], z))


def expected_abs_move_pct(bars: list, i: int, w: dict | None = None) -> float:
    """The scale: expected |close-open| for bar i, in percent."""
    w = w or weights()
    z = _scale(features(bars, i), w)
    return max(w["scale_intercept"]
               + sum(c * v for c, v in zip(w["scale_coef"], z)), 1e-3)


def interval(bars: list, i: int, confidence: float = 0.90,
             w: dict | None = None) -> dict:
    """'Today should stay within ±X%' — an adaptive band.

    Width is the scale for today multiplied by a fixed quantile of
    |ret| / scale measured over history. Because the scale moves with
    recent ranges, the band tightens on calm days and widens on volatile
    ones.

    That adaptivity is the whole point. A FIXED band tuned to the same
    average coverage looks equivalent on paper and is not: measured
    out-of-sample it covers 97.7% of calm days and only 82.9% of volatile
    ones, so it is loosest when it costs nothing and wrong exactly when
    it matters. The adaptive band holds ~91% in all three regimes.

    The stated confidence is a target; `realised` reports what that level
    actually achieved out-of-sample, which is the number to trust.
    """
    w = w or weights()
    key = f"{confidence:.2f}"
    if key not in w["ratio_quantiles"]:
        raise ValueError(
            f"confidence must be one of "
            f"{sorted(w['ratio_quantiles'])}, got {confidence}")
    scale = expected_abs_move_pct(bars, i, w)
    half = w["ratio_quantiles"][key] * scale
    last = bars[i - 1]["close"]
    stats = (w.get("band_oos") or {}).get(key, {})
    return {
        "confidence": confidence,
        "half_width_pct": round(half, 3),
        "half_width_points": round(half / 100 * last),
        "low": round(last * (1 - half / 100), 1),
        "high": round(last * (1 + half / 100), 1),
        "reference_close": last,
        "realised_coverage": stats.get("realised"),
        "note": ("Band on the SIZE of the move, not its direction. "
                 "Not a trading signal."),
    }


def band(p: float) -> str:
    """A label, deliberately coarse — the model does not support finer."""
    if p >= 0.65:
        return "wide"
    if p >= 0.55:
        return "leaning wide"
    if p <= 0.35:
        return "narrow"
    if p <= 0.45:
        return "leaning narrow"
    return "typical"


def forecast(bars: list, i: int | None = None,
             date: str | None = None) -> dict:
    """Full reading for bar i (default: the last bar supplied).

    `bars` must be at least MAX_LOOKBACK+1 daily OHLC dicts in ascending
    date order, each with open/high/low/close.

    Pass i == len(bars) to score the NEXT, not-yet-traded session — the
    features only ever look backwards, so this is the same computation
    with nothing withheld. That is the case the daily push needs, since it
    runs before the market opens.
    """
    w = weights()
    if i is None:
        i = len(bars) - 1
    if i < 1:
        raise ValueError("need at least one prior bar")
    if i > len(bars):
        raise ValueError("i is more than one session past the last bar")
    p = probability_wide(bars, i, w)
    rng = expected_range_pct(bars, i, w)
    last = bars[i - 1]["close"]
    return {
        "date": date or (bars[i].get("date") if i < len(bars) else None),
        "p_wide": round(p, 4),
        "band": band(p),
        "expected_range_pct": round(rng, 3),
        "expected_range_points": round(rng / 100 * last),
        "median_abs_ret_pct": w["median_abs_ret_pct"],
        "history_bars": min(i, MAX_LOOKBACK),
        "trained_through": w["trained_through"],
        "oos_accuracy": round(w["oos"]["nifty"]["accuracy"], 1),
        "band90": interval(bars, i, 0.90, w),
        "note": ("Session WIDTH only — this says nothing about direction, "
                 "and is not a trading signal."),
    }
