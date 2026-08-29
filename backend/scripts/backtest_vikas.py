"""Backtest of Vikas's "important dates" method (backend/app/vikas.py).

Usage (from backend/):
    python scripts/backtest_vikas.py            # uses cached prices/features
    python scripts/backtest_vikas.py --refresh  # refetch prices, recompute

What is tested, and how (details in knowledge/vikas/NOTES.md §F):
  A. nakshatra-lord daily direction: malefic lord → up, benefic → down
  B. the opposite-nature carry-over (with his same-Moon-sign / no-planet-
     moved conditions)
  C. Saturn-star fall → Mercury-star next day retraces ≥ half
  D. the "important date" candle: is a date's high/low a better breakout
     level than any other day's? (first cross within 5 sessions, then
     follow-through at session 5) — for every date family he names
  E. Sun nakshatra ingresses: week holds the low / 5-day return /
     reversal, all 27 stars, his five called out
  F. Mercury→Aries: is the ingress low closed below within 20/40/60 sessions?
  G. metals: Mars in the 12th sign from Saturn / Mars with Saturn /
     Mars in Dhanishta, over the whole transit span; Jupiter+Venus same
     sign for Nifty
  H. Sun–Neptune conjunction forward returns
  I. Monday green → Tuesday red
Nothing here was tuned on prices: the rules and parameters are his.
"""
import argparse
import datetime
import json
import math
import os
import random
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "opt"))

from app import vikas                              # noqa: E402
from app.names import NAKSHATRAS, RASIS            # noqa: E402
import prices                                      # noqa: E402
import stats                                       # noqa: E402

OUT = os.path.join(HERE, "..", "knowledge", "backtest", "vikas")
START = datetime.date(2011, 1, 1)
END = datetime.date(2026, 8, 28)
METAL_START = datetime.date(2015, 12, 22)          # the cached COMEX window
K_FWD = (1, 3, 5, 10)
RNG = random.Random(20260829)


# ----------------------------------------------------------------- features
def build_features(path: str) -> dict:
    feats = {}
    d = START - datetime.timedelta(days=12)
    prev = vikas.snapshot(d - datetime.timedelta(days=1), vikas.CLOSE_H)
    with open(path, "w", encoding="utf-8") as f:
        while d <= END:
            now = vikas.snapshot(d, vikas.CLOSE_H)
            o = vikas.snapshot(d, vikas.OPEN_H)
            star = vikas.session_star(d)
            ev = vikas.events_between(d, prev, now) + vikas.moon_angle_date(d, o=o)
            r = {"date": d.isoformat(), "wd": d.weekday(), "star": star,
                 "events": [{k: e[k] for k in ("family", "key", "label", "instrument")}
                            for e in ev],
                 "sun_venus": round(vikas._sep(o["trop"]["Venus"], o["trop"]["Sun"]), 3)}
            f.write(json.dumps(r) + "\n")
            feats[r["date"]] = r
            prev = now
            d += datetime.timedelta(days=1)
    return feats


def load_features(path: str) -> dict:
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                out[r["date"]] = r
    return out


# ----------------------------------------------------------------- prices
class Series:
    def __init__(self, bars: list[dict]):
        self.bars = [b for b in bars if b["high"] and b["low"]]
        self.idx = {b["date"]: i for i, b in enumerate(self.bars)}
        self.dates = [b["date"] for b in self.bars]
        self.n = len(self.bars)

    def i_on_or_after(self, iso: str) -> int | None:
        """Index of the first bar on/after a calendar date (his after-
        close / holiday shift), or None past the end."""
        import bisect
        i = bisect.bisect_left(self.dates, iso)
        return i if i < self.n else None

    def ret(self, i: int, k: int) -> float | None:
        if i + k >= self.n or i < 0:
            return None
        return self.bars[i + k]["close"] / self.bars[i]["close"] - 1

    def oc(self, i: int) -> float:
        b = self.bars[i]
        return b["close"] / b["open"] - 1

    def cc(self, i: int) -> float | None:
        return None if i == 0 else self.bars[i]["close"] / self.bars[i - 1]["close"] - 1


def load_series(refresh: bool) -> dict:
    out = {}
    for inst, start in (("nifty", START), ("banknifty", START),
                        ("gold", METAL_START), ("silver", METAL_START),
                        ("metal", START)):
        try:
            out[inst] = Series(prices.load(inst, start - datetime.timedelta(days=10),
                                           END, refresh=refresh))
            print(f"{inst}: {out[inst].n} bars {out[inst].dates[0]} → {out[inst].dates[-1]}")
        except Exception as e:                       # noqa: BLE001
            print(f"{inst}: unavailable ({e})")
    return out


# ----------------------------------------------------------------- stats
def binom_p(k: int, n: int, p: float) -> float:
    """Exact two-sided binomial p-value in log space."""
    if n == 0 or p <= 0 or p >= 1:
        return 1.0
    lp, lq = math.log(p), math.log(1 - p)

    def logpmf(i):
        return (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                + i * lp + (n - i) * lq)
    obs = logpmf(k)
    return min(1.0, sum(math.exp(logpmf(i)) for i in range(n + 1)
                        if logpmf(i) <= obs + 1e-9))


def perm_p_pairs(pairs: list, hits: int, n_perm: int = 2000, block: int = 5) -> float:
    preds = [s for s, _ in pairs]
    rets = [r for _, r in pairs]
    ge = 0
    for _ in range(n_perm):
        sh = stats.block_shuffle(rets, block, RNG)
        h = sum(1 for s, r in zip(preds, sh) if (r > 0) == (s > 0) and r != 0)
        ge += h >= hits
    return (ge + 1) / (n_perm + 1)


def perm_p_mean(obs_mean: float, pool: list, n: int, n_perm: int = 4000) -> float:
    """Two-sided: share of random n-subsets of `pool` whose mean is at
    least as far from the pool mean as the observed mean."""
    if n == 0 or n >= len(pool):
        return 1.0
    base = statistics.mean(pool)
    dev = abs(obs_mean - base)
    ge = 0
    for _ in range(n_perm):
        s = RNG.sample(pool, n)
        ge += abs(statistics.mean(s) - base) >= dev - 1e-15
    return (ge + 1) / (n_perm + 1)


def score_pairs(label: str, pairs: list) -> dict:
    n = len(pairs)
    hits = sum(1 for s, r in pairs if (r > 0) == (s > 0) and r != 0)
    ups = sum(1 for _, r in pairs if r > 0)
    naive = max(ups, n - ups) / n if n else 0.5
    s = stats.summarise(hits, n, naive, label)
    s["naive"] = naive * 100
    s["p_binom"] = binom_p(hits, n, 0.5)
    s["perm_p"] = perm_p_pairs(pairs, hits) if n >= 20 else 1.0
    return s


def rate(label: str, hits: int, n: int, base: float) -> dict:
    s = stats.summarise(hits, n, base, label)
    s["base"] = base * 100
    s["p_binom_vs_base"] = binom_p(hits, n, base)
    return s


# ----------------------------------------------------------------- tests
LORD_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
              "Saturn", "Mercury"]


def test_lord_direction(feats: dict, S: Series) -> dict:
    """A. malefic → up, benefic → down (his reading, opposite to the
    classical one); the Moon's nature follows the tithi."""
    out = {}
    for key in ("oc", "cc"):
        all_pairs, per_lord = [], defaultdict(list)
        for i, b in enumerate(S.bars):
            f = feats.get(b["date"])
            if not f or not f["star"]["clean"]:
                continue
            r = S.oc(i) if key == "oc" else S.cc(i)
            if r is None:
                continue
            pred = 1 if f["star"]["nature"] == "malefic" else -1
            per_lord[f["star"]["lord"]].append((pred, r))
            if f["star"]["lord"] not in ("Sun", "Moon"):   # his own exclusion
                all_pairs.append((pred, r))
        by_lord = []
        for L in LORD_ORDER:
            if not per_lord[L]:
                continue
            sc = score_pairs(f"{L} days ({key})", per_lord[L])
            half = len(per_lord[L]) // 2
            for tag, part in (("h1", per_lord[L][:half]), ("h2", per_lord[L][half:])):
                ups = sum(1 for _, r in part if r > 0)
                sc[f"up_{tag}"] = ups / len(part) * 100 if part else 0
            sc["up_rate"] = sum(1 for _, r in per_lord[L] if r > 0) / len(per_lord[L]) * 100
            by_lord.append(sc)
        out[key] = {"all_ex_sun_moon": score_pairs(f"lord rule ({key}), ex Sun/Moon days",
                                                   all_pairs),
                    "by_lord": by_lord}
    return out


def _consecutive(S: Series, i: int) -> bool:
    if i + 1 >= S.n:
        return False
    a = datetime.date.fromisoformat(S.dates[i])
    b = datetime.date.fromisoformat(S.dates[i + 1])
    return (b - a).days == 1


def test_carry_over(feats: dict, S: Series) -> dict:
    """B. day 1 closes against its lord → day 2 (opposite nature) goes
    the other way. Strict = his full condition set [V5]; loose = only
    same Moon sign [V1]."""
    res = {}
    for variant in ("strict", "loose"):
        pairs_oc, pairs_cc, not_beyond, base_not_beyond = [], [], [0, 0], [0, 0]
        for i in range(S.n - 1):
            if not _consecutive(S, i):
                continue
            f1, f2 = feats.get(S.dates[i]), feats.get(S.dates[i + 1])
            if not (f1 and f2):
                continue
            s1, s2 = f1["star"], f2["star"]
            d1 = 1 if S.oc(i) > 0 else -1
            # baseline: any consecutive pair, "day 2 does not close beyond day 1's extreme"
            b2 = S.bars[i + 1]
            beyond = (b2["close"] > S.bars[i]["high"]) if d1 > 0 else (b2["close"] < S.bars[i]["low"])
            base_not_beyond[0] += not beyond
            base_not_beyond[1] += 1
            if not (s1["clean"] and s2["clean"] and s1["full_session"]):
                continue
            if s1["nature"] == s2["nature"]:
                continue
            if s1["moon_sign"] != s2["moon_sign"]:
                continue
            if variant == "strict" and s1["signs"] != s2["signs"]:
                continue
            against = (s1["nature"] == "malefic" and d1 < 0) or \
                      (s1["nature"] == "benefic" and d1 > 0)
            if not against:
                continue
            pred = -d1
            pairs_oc.append((pred, S.oc(i + 1)))
            pairs_cc.append((pred, S.cc(i + 1)))
            not_beyond[0] += not beyond
            not_beyond[1] += 1
        res[variant] = {
            "oc": score_pairs(f"carry-over {variant} (day-2 close vs open)", pairs_oc),
            "cc": score_pairs(f"carry-over {variant} (day-2 close vs day-1 close)", pairs_cc),
            "not_beyond": rate(f"carry-over {variant}: day 2 does not close beyond day-1 extreme",
                               not_beyond[0], not_beyond[1],
                               base_not_beyond[0] / base_not_beyond[1])}
    return res


def test_saturn_mercury(feats: dict, S: Series) -> dict:
    """C. Saturn star falls all session → Mercury star next day retraces
    at least half of the fall (body and range versions)."""
    hits = {"body": [0, 0], "range": [0, 0]}
    base = {"body": [0, 0], "range": [0, 0]}
    examples = []
    for i in range(S.n - 1):
        if not _consecutive(S, i):
            continue
        b1, b2 = S.bars[i], S.bars[i + 1]
        if b1["close"] >= b1["open"]:
            continue
        body_hit = b2["high"] >= b1["close"] + 0.5 * (b1["open"] - b1["close"])
        range_hit = b2["high"] >= b1["low"] + 0.5 * (b1["high"] - b1["low"])
        for k, h in (("body", body_hit), ("range", range_hit)):
            base[k][0] += h
            base[k][1] += 1
        f1, f2 = feats.get(b1["date"]), feats.get(b2["date"])
        if not (f1 and f2):
            continue
        s1, s2 = f1["star"], f2["star"]
        if not (s1["nakshatra"] in vikas.SATURN_STARS and s1["full_session"]):
            continue
        if not (s2["open_nakshatra"] in vikas.MERCURY_STARS and s2["clean"]):
            continue
        for k, h in (("body", body_hit), ("range", range_hit)):
            hits[k][0] += h
            hits[k][1] += 1
        examples.append((b1["date"], round(S.oc(i) * 100, 2), body_hit,
                         round(S.oc(i + 1) * 100, 2)))
    return {k: rate(f"Saturn→Mercury half-retrace ({k})", hits[k][0], hits[k][1],
                    base[k][0] / base[k][1]) for k in hits} | {"examples": examples}


def candle_outcomes(S: Series, i: int, horizon: int = 5) -> dict | None:
    """The date-candle trade: first cross of the date's high/low within
    `horizon` sessions and whether session `horizon` closes beyond it."""
    if i + horizon >= S.n or i < 0:
        return None
    hi, lo = S.bars[i]["high"], S.bars[i]["low"]
    for j in range(i + 1, i + horizon + 1):
        b = S.bars[j]
        up, dn = b["high"] > hi, b["low"] < lo
        if up and dn:
            return {"cross": "both", "ft": None, "same_day": None}
        if up:
            return {"cross": "high", "ft": S.bars[i + horizon]["close"] > hi,
                    "same_day": b["close"] > hi}
        if dn:
            return {"cross": "low", "ft": S.bars[i + horizon]["close"] < lo,
                    "same_day": b["close"] < lo}
    return {"cross": None, "ft": None, "same_day": None}


def family_dates(feats: dict, S: Series, pick) -> list[int]:
    """Bar indexes for events selected by pick(feature_row, event) → bool,
    shifted to the next session (his after-close rule; holidays too)."""
    out = set()
    for iso, f in feats.items():
        for e in f["events"]:
            if pick(f, e):
                i = S.i_on_or_after(iso)
                if i is not None:
                    out.add(i)
    return sorted(out)


def star_dates(feats: dict, S: Series, stars: set, no_friday: bool = True) -> list[int]:
    out = []
    for i, b in enumerate(S.bars):
        f = feats.get(b["date"])
        if not f:
            continue
        s = f["star"]
        if s["nakshatra"] in stars and s["clean"] and (not no_friday or f["wd"] != 4):
            out.append(i)
    return out


def test_candles(label: str, idxs: list[int], S: Series, base: dict) -> dict:
    """D. the candle test for one family vs the all-days baseline."""
    outs = [candle_outcomes(S, i) for i in idxs]
    outs = [o for o in outs if o]
    n = len(outs)
    crossed = [o for o in outs if o["cross"] in ("high", "low")]
    ft = sum(1 for o in crossed if o["ft"])
    sd = sum(1 for o in crossed if o["same_day"])
    held = sum(1 for o in outs if o["cross"] is None)
    fwd = {}
    for k in K_FWD:
        rs = [S.ret(i, k) for i in idxs]
        rs = [r for r in rs if r is not None]
        if not rs:
            continue
        ups = sum(1 for r in rs if r > 0)
        fwd[k] = {"n": len(rs), "mean_bp": statistics.mean(rs) * 1e4,
                  "up": ups / len(rs) * 100,
                  "base_mean_bp": base["fwd"][k]["mean_bp"], "base_up": base["fwd"][k]["up"],
                  "p_mean": perm_p_mean(statistics.mean(rs), base["fwd"][k]["pool"], len(rs)),
                  "p_up": binom_p(ups, len(rs), base["fwd"][k]["up"] / 100)}
    return {"label": label, "n": n,
            "follow_through": rate(f"{label}: follow-through at +5", ft, len(crossed),
                                   base["ft"]),
            "same_day": rate(f"{label}: cross-day closes beyond", sd, len(crossed),
                             base["same_day"]),
            "held": rate(f"{label}: range held 5 sessions", held, n, base["held"]),
            "fwd": fwd}


def baseline(S: Series) -> dict:
    outs = [candle_outcomes(S, i) for i in range(S.n)]
    outs = [o for o in outs if o]
    crossed = [o for o in outs if o["cross"] in ("high", "low")]
    b = {"ft": sum(1 for o in crossed if o["ft"]) / len(crossed),
         "same_day": sum(1 for o in crossed if o["same_day"]) / len(crossed),
         "held": sum(1 for o in outs if o["cross"] is None) / len(outs),
         "fwd": {}}
    for k in K_FWD:
        pool = [S.ret(i, k) for i in range(S.n - k)]
        b["fwd"][k] = {"pool": pool, "mean_bp": statistics.mean(pool) * 1e4,
                       "up": sum(1 for r in pool if r > 0) / len(pool) * 100}
    return b


def test_sun_naks(feats: dict, S: Series, base: dict) -> dict:
    """E. every Sun nakshatra ingress: does the week hold the ingress low,
    5-day return, and reversal (5 days before vs 5 after)."""
    rows = []
    all_hold, all_rev = [0, 0], [0, 0]
    # baselines over all days
    bh = sum(1 for i in range(S.n - 5)
             if min(b["low"] for b in S.bars[i + 1:i + 6]) >= S.bars[i]["low"])
    bh_n = S.n - 5
    br = 0
    for i in range(5, S.n - 5):
        pre = S.bars[i]["close"] - S.bars[i - 5]["close"]
        post = S.bars[i + 5]["close"] - S.bars[i]["close"]
        br += (pre > 0) != (post > 0)
    br_n = S.n - 10
    for nak in NAKSHATRAS:
        idxs = family_dates(feats, S, lambda f, e, nak=nak: e["family"] == "sun_nak"
                            and e["key"] == nak)
        idxs = [i for i in idxs if 5 <= i < S.n - 5]
        hold = sum(1 for i in idxs
                   if min(b["low"] for b in S.bars[i + 1:i + 6]) >= S.bars[i]["low"])
        rev = 0
        for i in idxs:
            pre = S.bars[i]["close"] - S.bars[i - 5]["close"]
            post = S.bars[i + 5]["close"] - S.bars[i]["close"]
            rev += (pre > 0) != (post > 0)
        r5 = [S.ret(i, 5) for i in idxs]
        r3 = [S.ret(i, 3) for i in idxs]
        rows.append({"nakshatra": nak, "n": len(idxs), "hold_low": hold,
                     "hold_rate": hold / len(idxs) * 100 if idxs else 0,
                     "rev": rev, "rev_rate": rev / len(idxs) * 100 if idxs else 0,
                     "mean5_bp": statistics.mean(r5) * 1e4 if r5 else 0,
                     "up5": sum(1 for r in r5 if r > 0) / len(r5) * 100 if r5 else 0,
                     "mean3_bp": statistics.mean(r3) * 1e4 if r3 else 0,
                     "p5": perm_p_mean(statistics.mean(r5), base["fwd"][5]["pool"], len(r5))
                     if r5 else 1.0,
                     "note": vikas.SUN_NAK_NOTES.get(nak, ""),
                     "years": [S.dates[i][:4] + (":hold" if min(b["low"] for b in S.bars[i + 1:i + 6]) >= S.bars[i]["low"] else ":broke") for i in idxs]})
        all_hold[0] += hold
        all_hold[1] += len(idxs)
        all_rev[0] += rev
        all_rev[1] += len(idxs)
    return {"rows": rows, "base_hold": bh / bh_n * 100, "base_rev": br / br_n * 100,
            "all_hold": rate("all Sun ingresses: week holds the low", *all_hold, bh / bh_n),
            "all_rev": rate("all Sun ingresses: 5-day reversal", *all_rev, br / br_n)}


def test_mercury_aries(feats: dict, S: Series) -> dict:
    """F. the ingress-day low is 'not closed below for months'."""
    res = {}
    for horizon in (20, 40, 60):
        base = sum(1 for i in range(S.n - horizon)
                   if min(b["close"] for b in S.bars[i + 1:i + horizon + 1]) >= S.bars[i]["low"])
        base_n = S.n - horizon
        for label, pick in (("Mercury→Mesha", lambda f, e: e["family"] == "mercury_sign" and e["key"] == "Mesha"),
                            ("all Mercury sign ingresses", lambda f, e: e["family"] == "mercury_sign")):
            idxs = [i for i in family_dates(feats, S, pick) if i < S.n - horizon]
            held = sum(1 for i in idxs
                       if min(b["close"] for b in S.bars[i + 1:i + horizon + 1]) >= S.bars[i]["low"])
            res[f"{label} / {horizon}"] = rate(f"{label}: low holds {horizon} sessions",
                                               held, len(idxs), base / base_n)
            if label == "Mercury→Mesha":
                res[f"{label} / {horizon}"]["dates"] = [
                    S.dates[i] + (":held" if min(b["close"] for b in S.bars[i + 1:i + horizon + 1]) >= S.bars[i]["low"] else ":broke")
                    for i in idxs]
    return res


def spans(feats: dict, S: Series, start_pick, end_family: str) -> list[tuple[int, int, str]]:
    """(start bar, end bar, key) from an event to the next event of
    `end_family` (the planet's next ingress)."""
    starts = []
    for iso in sorted(feats):
        for e in feats[iso]["events"]:
            if start_pick(feats[iso], e):
                starts.append((iso, e["key"]))
    ends = sorted(iso for iso in feats for e in feats[iso]["events"]
                  if e["family"] == end_family)
    out = []
    for iso, key in starts:
        nxt = next((x for x in ends if x > iso), None)
        i, j = S.i_on_or_after(iso), S.i_on_or_after(nxt) if nxt else None
        if i is not None and j is not None and j > i:
            out.append((i, j, key))
    return out


def test_spans(feats: dict, series: dict) -> dict:
    """G. transit-span returns for the metal rules and Jupiter+Venus."""
    res = {}
    rules = [
        ("Mars in 12th sign from Saturn", ("gold", "silver", "metal", "nifty"),
         lambda f, e: e["family"] == "mars_sign" and e["key"].startswith("12th_from_saturn"),
         "mars_sign", "fall"),
        ("Mars in Saturn's sign", ("gold", "silver", "metal", "nifty"),
         lambda f, e: e["family"] == "mars_sign" and e["key"] == "with_saturn",
         "mars_sign", "rise"),
        ("Mars in Dhanishta", ("gold", "silver", "metal", "nifty"),
         lambda f, e: e["family"] == "mars_nak" and e["key"] == "Dhanishta",
         "mars_nak", "fall"),
        ("Jupiter & Venus in one sign", ("nifty", "banknifty"),
         lambda f, e: e["family"] in ("venus_sign", "jupiter_sign")
         and e["key"] in ("with_jupiter", "with_venus"),
         "venus_sign", "rise"),
    ]
    for label, insts, pick, end_family, claim in rules:
        for inst in insts:
            S = series.get(inst)
            if not S:
                continue
            sp = spans(feats, S, pick, end_family)
            # baseline: every span of the same planet family
            allsp = spans(feats, S, lambda f, e, ef=end_family: e["family"] == ef, end_family)
            pool = [S.bars[j]["close"] / S.bars[i]["close"] - 1 for i, j, _ in allsp]
            rows = []
            for i, j, key in sp:
                r = S.bars[j]["close"] / S.bars[i]["close"] - 1
                worst = min(b["low"] for b in S.bars[i:j + 1]) / S.bars[i]["close"] - 1
                best = max(b["high"] for b in S.bars[i:j + 1]) / S.bars[i]["close"] - 1
                rows.append({"start": S.dates[i], "end": S.dates[j], "key": key,
                             "ret": r * 100, "max_dd": worst * 100, "max_up": best * 100,
                             "sessions": j - i})
            rets = [r["ret"] / 100 for r in rows]
            hit = (sum(1 for r in rets if r < 0) if claim == "fall"
                   else sum(1 for r in rets if r > 0))
            base_hit = (sum(1 for r in pool if r < 0) if claim == "fall"
                        else sum(1 for r in pool if r > 0)) / len(pool) if pool else 0.5
            ex2020 = [r["ret"] / 100 for r in rows if not r["start"].startswith("2020")]
            half = len(rets) // 2
            res[f"{label} / {inst}"] = {
                "median_ret": statistics.median(rets) * 100 if rets else 0,
                "base_median_ret": statistics.median(pool) * 100 if pool else 0,
                "mean_ex2020": statistics.mean(ex2020) * 100 if ex2020 else 0,
                "mean_h1": statistics.mean(rets[:half]) * 100 if half else 0,
                "mean_h2": statistics.mean(rets[half:]) * 100 if rets[half:] else 0,
                "by_key": {k: statistics.mean([r["ret"] for r in rows if r["key"] == k])
                           for k in sorted({r["key"] for r in rows})},
                "label": label, "instrument": inst, "claim": claim, "rows": rows,
                "n": len(rows), "mean_ret": statistics.mean(rets) * 100 if rets else 0,
                "base_mean_ret": statistics.mean(pool) * 100 if pool else 0,
                "base_n": len(pool),
                "hit": rate(f"{label} / {inst}: span goes the claimed way", hit, len(rets), base_hit),
                "p_mean": perm_p_mean(statistics.mean(rets), pool, len(rets)) if rets and len(pool) > len(rets) else 1.0}
    return res


def test_monday(S: Series) -> dict:
    """I. 'Monday green, Tuesday red' [V5 @ 49:03]."""
    mg_tr, mg, mr_tg, mr, tue_red, tue = 0, 0, 0, 0, 0, 0
    for i in range(S.n - 1):
        if not _consecutive(S, i):
            continue
        if datetime.date.fromisoformat(S.dates[i]).weekday() != 0:
            continue
        m_up, t_up = S.oc(i) > 0, S.oc(i + 1) > 0
        tue += 1
        tue_red += not t_up
        if m_up:
            mg += 1
            mg_tr += not t_up
        else:
            mr += 1
            mr_tg += t_up
    return {"mon_green_tue_red": rate("Monday green → Tuesday red", mg_tr, mg, tue_red / tue),
            "mon_red_tue_green": rate("Monday red → Tuesday green", mr_tg, mr, 1 - tue_red / tue)}


# ----------------------------------------------------------------- report
def pct(x):
    return f"{x:5.1f}%"


def fmt_rate(s: dict) -> str:
    return (f"| {s['label']} | {s['hits']}/{s['n']} | {pct(s['rate'])} | {pct(s['base'])} | "
            f"[{s['ci_lo']:.1f}, {s['ci_hi']:.1f}] | {s['p_binom_vs_base']:.3f} |")


def fmt_pairs(s: dict) -> str:
    return (f"| {s['label']} | {s['hits']}/{s['n']} | {pct(s['rate'])} | {pct(s['naive'])} | "
            f"[{s['ci_lo']:.1f}, {s['ci_hi']:.1f}] | {s['p_binom']:.3f} | {s['perm_p']:.3f} |")


RATE_HDR = "| rule | hits | rate | base | 95% CI | p vs base |\n|---|---|---|---|---|---|"
PAIR_HDR = "| rule | hits | rate | naive | 95% CI | p vs 50% | perm-p |\n|---|---|---|---|---|---|---|"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    fpath = os.path.join(OUT, f"features_{START}_{END}.jsonl")
    feats = load_features(fpath) if os.path.exists(fpath) and not args.refresh \
        else build_features(fpath)
    print(f"features: {len(feats)} days")
    series = load_series(args.refresh)
    N = series["nifty"]
    base = baseline(N)
    R = {"window": [START.isoformat(), END.isoformat()], "nifty_days": N.n}

    R["A_lord"] = test_lord_direction(feats, N)
    R["B_carry"] = test_carry_over(feats, N)
    R["C_sat_merc"] = test_saturn_mercury(feats, N)

    fams = [
        ("Moon in a Saturn star (Nifty date)", star_dates(feats, N, vikas.SATURN_STARS), N),
        ("Moon in Pushya", star_dates(feats, N, {"Pushya"}), N),
        ("Moon in Anuradha", star_dates(feats, N, {"Anuradha"}), N),
        ("Moon in Uttara Bhadrapada", star_dates(feats, N, {"Uttara Bhadrapada"}), N),
        ("Moon in Mesha (both days)", [i for i, b in enumerate(N.bars) if feats.get(b["date"], {}).get("star", {}).get("moon_sign") == "Mesha"], N),
        ("Moon in Meena (both days)", [i for i, b in enumerate(N.bars) if feats.get(b["date"], {}).get("star", {}).get("moon_sign") == "Meena"], N),
        ("Sun nakshatra ingress (any)", family_dates(feats, N, lambda f, e: e["family"] == "sun_nak"), N),
        ("Mercury sign ingress (any)", family_dates(feats, N, lambda f, e: e["family"] == "mercury_sign"), N),
        ("Mercury enters Mesha", family_dates(feats, N, lambda f, e: e["family"] == "mercury_sign" and e["key"] == "Mesha"), N),
        ("Venus sign ingress", family_dates(feats, N, lambda f, e: e["family"] == "venus_sign"), N),
        ("Mars sign ingress", family_dates(feats, N, lambda f, e: e["family"] == "mars_sign"), N),
        ("Jupiter sign ingress", family_dates(feats, N, lambda f, e: e["family"] == "jupiter_sign"), N),
        ("Saturn sign ingress", family_dates(feats, N, lambda f, e: e["family"] == "saturn_sign"), N),
        ("Mars nakshatra ingress", family_dates(feats, N, lambda f, e: e["family"] == "mars_nak"), N),
        ("big×small 30°/60° (any)", family_dates(feats, N, lambda f, e: e["family"] == "big_small" and not e["key"].endswith("-0")), N),
        ("big×small conjunction", family_dates(feats, N, lambda f, e: e["family"] == "big_small" and e["key"].endswith("-0")), N),
        ("Jupiter 30° Mercury", family_dates(feats, N, lambda f, e: e["key"] == "Jupiter-Mercury-30"), N),
        ("Sun conjunct Neptune", family_dates(feats, N, lambda f, e: e["key"] == "Sun-Neptune"), N),
        ("Venus conjunct Ketu/Rahu", family_dates(feats, N, lambda f, e: e["key"] in ("Venus-Ketu", "Venus-Rahu")), N),
        ("Mercury conjunct Ketu/Rahu", family_dates(feats, N, lambda f, e: e["key"] in ("Mercury-Ketu", "Mercury-Rahu")), N),
        ("Moon 45/135/225/315° at open (tropical)", family_dates(feats, N, lambda f, e: e["family"] in ("moon45_trop", "moon135_trop", "moon225_trop", "moon315_trop")), N),
        ("Moon 45/135/225/315° at open (sidereal)", family_dates(feats, N, lambda f, e: e["family"] in ("moon45_sid", "moon135_sid", "moon225_sid", "moon315_sid")), N),
        ("Moon 270° at open (tropical)", family_dates(feats, N, lambda f, e: e["family"] == "moon270_trop"), N),
        ("Venus within 8° of Uranus (same sign)", family_dates(feats, N, lambda f, e: e["family"] == "venus_uranus"), N),
        ("Venus at 45° longitude (tropical)", family_dates(feats, N, lambda f, e: e["family"] == "venus45_trop"), N),
        ("Sun–Venus 45° (semi-square)", sun_venus_dates(feats, N), N),
    ]
    R["D_candles"] = [test_candles(lbl, idx, S, base) for lbl, idx, S in fams]
    if "banknifty" in series:
        B = series["banknifty"]
        bb = baseline(B)
        R["D_candles_banknifty"] = [
            test_candles("Moon in a Jupiter star (Bank Nifty date)",
                         star_dates(feats, B, {"Punarvasu", "Vishakha", "Purva Bhadrapada"}), B, bb),
            test_candles("Moon in a Saturn star (Bank Nifty)", star_dates(feats, B, vikas.SATURN_STARS), B, bb)]
        R["banknifty_base"] = {k: v for k, v in bb.items() if k != "fwd"}
    R["base"] = {"ft": base["ft"] * 100, "same_day": base["same_day"] * 100,
                 "held": base["held"] * 100,
                 "fwd": {k: {"mean_bp": v["mean_bp"], "up": v["up"]} for k, v in base["fwd"].items()}}
    R["E_sun"] = test_sun_naks(feats, N, base)
    R["F_mercury"] = test_mercury_aries(feats, N)
    R["G_spans"] = test_spans(feats, series)
    R["I_monday"] = test_monday(N)
    write_report(R)
    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)
    print("written", OUT)


def sun_venus_dates(feats: dict, S: Series) -> list[int]:
    """'Venus 45°' read as the Sun–Venus separation crossing 45° (his
    11 May / 23 Jun 2025 dates sit at 43.9° / 44.4°)."""
    out, prev = set(), None
    for iso in sorted(feats):
        sv = feats[iso]["sun_venus"]
        if prev is not None:
            for tgt in (45, 315):
                if vikas._crossed(prev, sv, tgt) or vikas._crossed(sv, prev, tgt):
                    i = S.i_on_or_after(iso)
                    if i is not None:
                        out.add(i)
        prev = sv
    return sorted(out)


def write_report(R: dict) -> None:
    L = [f"# Vikas — backtest {R['window'][0]} → {R['window'][1]}", "",
         "Method: `app/vikas.py` computes his dates and day-lords from the",
         "ephemeris (sidereal Lahiri; GannZilla-style tropical where he uses",
         "it) for every day of the window; nothing was fitted to prices.",
         "Nifty = ^NSEI daily bars. `base` is the same statistic over all",
         "trading days; p is an exact binomial against that base (or a",
         "random-subset permutation for mean returns). Where he gives a",
         "number ('90%', '100%') it is quoted next to the result.", ""]
    A = R["A_lord"]
    L += ["## A. Nakshatra-lord daily rule — malefic lord → up, benefic → down", "",
          "His claim [V5]: the lord's nature sets the day's direction; he",
          "excludes Sun and Moon days himself. Only sessions where one star",
          "covers ≥ 4 h are used.", "", PAIR_HDR]
    for key in ("oc", "cc"):
        L.append(fmt_pairs(A[key]["all_ex_sun_moon"]))
    L += ["", "By lord (close vs open). `up` = share of those days that closed",
          "up, then the same for the first / second half of the window — the",
          "classical reading (benefic up, malefic down) is `100 − rate` where",
          "the lord is malefic:", "",
          "| lord | hits | rate (his reading) | up | up h1 | up h2 | p vs 50% |",
          "|---|---|---|---|---|---|---|"]
    for s in A["oc"]["by_lord"]:
        L.append(f"| {s['label']} | {s['hits']}/{s['n']} | {pct(s['rate'])} | {pct(s['up_rate'])} | "
                 f"{pct(s['up_h1'])} | {pct(s['up_h2'])} | {s['p_binom']:.3f} |")
    L += ["", "## B. The carry-over (day 1 closes against its lord → day 2 goes the other way)", "",
          "Strict = his full condition set [V5]: consecutive trading days, opposite",
          "natures, same Moon sign, no other planet changed sign. Loose = same Moon",
          "sign only [V1]. His claim: 'this works 100%'.", "", PAIR_HDR]
    for v in ("strict", "loose"):
        L += [fmt_pairs(R["B_carry"][v]["oc"]), fmt_pairs(R["B_carry"][v]["cc"])]
    L += ["", RATE_HDR]
    L += [fmt_rate(R["B_carry"][v]["not_beyond"]) for v in ("strict", "loose")]
    C = R["C_sat_merc"]
    L += ["", "## C. Saturn star falls → Mercury star retraces at least half next day", "",
          "His claim: '90–100%', 'once in 2–3 months'. Hit = next day's high",
          "reaches the 50% retracement of the fall (body: open→close; range:",
          "high→low). Base = any down day followed by the next calendar day.", "",
          RATE_HDR, fmt_rate(C["body"]), fmt_rate(C["range"]), "",
          f"Instances ({len(C['examples'])}): " +
          ", ".join(f"{d} ({r1:+.1f}% → {'hit' if h else 'miss'}, next {r2:+.1f}%)"
                    for d, r1, h, r2 in C["examples"][-12:]) + (" …" if len(C["examples"]) > 12 else "")]
    b = R["base"]
    L += ["", "## D. The date candle — is his date's high/low a better breakout level?", "",
          "For each date: first cross of the date candle's high or low within",
          "5 sessions; follow-through = session 5 closes beyond the crossed",
          "level; cross-day = the crossing session itself closes beyond;",
          "held = neither side crossed in 5 sessions. Base over all Nifty days:",
          f"follow-through {b['ft']:.1f}%, cross-day {b['same_day']:.1f}%, held {b['held']:.1f}%.",
          "Forward returns: mean k-session return on the dates vs all days",
          "(p = random-subset permutation).", "",
          "| date family | n | follow-through | cross-day close | held | +1d bp (p) | +5d bp (p) | +10d bp (p) |",
          "|---|---|---|---|---|---|---|---|"]
    for row in R["D_candles"] + R.get("D_candles_banknifty", []):
        ft, sd, hd = row["follow_through"], row["same_day"], row["held"]
        f = row["fwd"]

        def cell(k):
            if k not in f:
                return "—"
            return f"{f[k]['mean_bp']:+.0f} vs {f[k]['base_mean_bp']:+.0f} ({f[k]['p_mean']:.2f})"
        L.append(f"| {row['label']} | {row['n']} | {ft['hits']}/{ft['n']} = {ft['rate']:.0f}% "
                 f"(p {ft['p_binom_vs_base']:.2f}) | {sd['rate']:.0f}% | {hd['rate']:.0f}% "
                 f"(p {hd['p_binom_vs_base']:.2f}) | {cell(1)} | {cell(5)} | {cell(10)} |")
    E = R["E_sun"]
    L += ["", "## E. Sun nakshatra ingresses (his yearly dates)", "",
          f"Base over all days: week holds the day's low {E['base_hold']:.1f}%, "
          f"5-day reversal {E['base_rev']:.1f}%, mean 5-day return "
          f"{b['fwd'][5]['mean_bp']:+.0f} bp.", "",
          "| Sun enters | n | week holds low | reversal | +3d bp | +5d bp (p) | his note | years |",
          "|---|---|---|---|---|---|---|---|"]
    for r in E["rows"]:
        L.append(f"| {r['nakshatra']} | {r['n']} | {r['hold_low']}/{r['n']} = {r['hold_rate']:.0f}% | "
                 f"{r['rev_rate']:.0f}% | {r['mean3_bp']:+.0f} | {r['mean5_bp']:+.0f} ({r['p5']:.2f}) | "
                 f"{r['note']} | {' '.join(r['years'])} |")
    L += ["", RATE_HDR, fmt_rate(E["all_hold"]), fmt_rate(E["all_rev"])]
    L += ["", "## F. Mercury enters Aries — 'the low is not closed below for months'", "", RATE_HDR]
    for k, s in R["F_mercury"].items():
        L.append(fmt_rate(s))
    for k, s in R["F_mercury"].items():
        if "dates" in s:
            L.append(f"\n{k}: " + ", ".join(s["dates"]))
    L += ["", "## G. Transit spans — metals and Jupiter+Venus", "",
          "Return from the ingress session to the planet's next ingress; base",
          "= every span of that planet (all its sign / nakshatra transits) on",
          "the same instrument. `metal` = Nifty Metal index if Yahoo served it.", "",
          "| rule / instrument | n | mean span return | base mean (n) | goes the claimed way | p (mean) |",
          "|---|---|---|---|---|---|"]
    for k, s in R["G_spans"].items():
        h = s["hit"]
        L.append(f"| {k} ({s['claim']}) | {s['n']} | {s['mean_ret']:+.1f}% | {s['base_mean_ret']:+.1f}% "
                 f"({s['base_n']}) | {h['hits']}/{h['n']} vs base {h['base']:.0f}% (p {h['p_binom_vs_base']:.2f}) "
                 f"| {s['p_mean']:.2f} |")
    L += ["", "Robustness (mean is dominated by the 2020 span):", "",
          "| rule / instrument | median | base median | mean ex-2020 | mean 1st half | mean 2nd half | by key |",
          "|---|---|---|---|---|---|---|"]
    for k, s in R["G_spans"].items():
        if s["instrument"] in ("nifty", "metal", "gold"):
            L.append(f"| {k} | {s['median_ret']:+.1f}% | {s['base_median_ret']:+.1f}% | "
                     f"{s['mean_ex2020']:+.1f}% | {s['mean_h1']:+.1f}% | {s['mean_h2']:+.1f}% | "
                     + ", ".join(f"{kk} {v:+.1f}%" for kk, v in s["by_key"].items()) + " |")
    for k, s in R["G_spans"].items():
        if s["rows"] and s["instrument"] in ("gold", "nifty"):
            L.append(f"\n{k}: " + "; ".join(
                f"{r['start']}→{r['end']} {r['ret']:+.1f}% (dd {r['max_dd']:+.1f}%, {r['key']})"
                for r in s["rows"]))
    M = R["I_monday"]
    L += ["", "## I. Monday green → Tuesday red", "", RATE_HDR,
          fmt_rate(M["mon_green_tue_red"]), fmt_rate(M["mon_red_tue_green"])]
    L += ["", "## Not testable without intraday data", "",
          "- the high-cross / low-cross entries with the candle's other side as stop",
          "- the first-1–2-hour rule, gap / order-block retests, flag targets",
          "- the RBI-policy-day fade of the 10:00 candle (needs 5-minute bars)",
          "- stock radix dates (needs incorporation / listing dates per stock)", ""]
    with open(os.path.join(OUT, "RESULTS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
