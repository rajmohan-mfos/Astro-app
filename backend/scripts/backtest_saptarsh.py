"""Backtest of the Saptarsh-style outlook (app/saptarsh.py) against
Nifty, gold and silver.

Two phases, both reproducible:

  1. features — app.saptarsh.day() for every calendar day of the window,
     reduced to a flat record and cached as JSON lines. This is the
     expensive part (~0.2 s/day), run in a process pool.
  2. evaluate — join with prices and score:
       * the final Nifty / gold / silver call (bull / bear) against the
         realised direction, split by source (observed / extrapolated)
       * the Moon-nakshatra base call alone, and the per-star table
       * the Nifty session-window lean and the metals-window lean
       * "volatile" calls against the realised absolute move
       * every named rule as an event study (Amavasya, Vishti, Kshaya,
         Mercury retrograde, ingresses, stations, Kaal Sarp, grand trine,
         stellia, Vaar-Tithi, Vaar-Nakshatra, ...)
       * every observed aspect label with enough exact hits
       * his retrograde-Mercury moratorium: accuracy in retro vs direct
     Each line carries n, hit rate, Wilson 95% CI, the base rate it must
     beat, a z against that base, and an exact binomial p; the headline
     accuracies also get a moving-block permutation p. A Bonferroni line
     says how many of the rule tests survive the sweep.

Outcome definitions. Nifty: the report is a session call, so the
outcome is close vs open of the same day (NSE). Gold / silver: COMEX
front-month futures (GC=F / SI=F), whose New-York-dated bar covers
18:00 ET the previous evening to 17:00 ET — i.e. the 03:30 -> 27:30 IST
Globex day the metals report is written for — so the outcome is close
vs previous close of the bar dated d.

Usage (from backend/):
    python scripts/backtest_saptarsh.py               # both phases
    python scripts/backtest_saptarsh.py --features    # phase 1 only
    python scripts/backtest_saptarsh.py --evaluate    # phase 2 only
Outputs under knowledge/backtest/saptarsh/.
"""
import argparse
import csv
import datetime
import json
import math
import os
import random
import statistics
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "opt"))

from app import saptarsh                      # noqa: E402
from app.transit import DASHA_LORDS, SEG      # noqa: E402
from app.names import NAKSHATRAS              # noqa: E402
import prices                                 # noqa: E402
import stats                                  # noqa: E402

OUT = os.path.join(HERE, "..", "knowledge", "backtest", "saptarsh")
START = datetime.date(2016, 1, 1)
END = datetime.date(2026, 8, 28)
INSTRUMENTS = ("nifty", "gold", "silver")
TONE_SIGN = {"bull": 1, "bear": -1}

# regime pieces that are cheap (positions only) — computed here rather
# than through saptarsh.regime(), whose sign-span scans cost seconds
TRINE = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def _sep(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def cheap_regime(d: datetime.date) -> dict:
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = saptarsh._jd_local(d, saptarsh.OPEN_H)
    pos = {n: saptarsh._lon(b, jd) for n, b in saptarsh.BODIES if n != "Moon"}
    pos["Ketu"] = (pos["Rahu"] + 180) % 360
    side = [((pos[n] - pos["Rahu"]) % 360) < 180 for n in TRINE]
    kaal = all(side) or not any(side)
    trine = False
    for i, a in enumerate(TRINE):
        for j, b in enumerate(TRINE[i + 1:], i + 1):
            for c in TRINE[j + 1:]:
                if all(abs(_sep(pos[x], pos[y]) - 120) <= 6
                       for x, y in ((a, b), (b, c), (a, c))):
                    trine = True
    naks = defaultdict(int)
    for n, l in pos.items():
        if n not in ("Rahu", "Ketu"):
            naks[int(l // SEG)] += 1
    signs = defaultdict(int)
    for n, l in pos.items():
        signs[int(l // 30)] += 1
    early = sum(1 for l in pos.values() if l % 30 < 10)
    mars_retro = swe.calc_ut(jd, swe.MARS, saptarsh.FLAGS)[0][3] < 0
    return {"kaal_sarp": kaal, "grand_trine": trine,
            "nak_stellium": max(naks.values()) >= 3,
            "sign_stellium": max(signs.values()) >= 4,
            "early_degree": early >= 6, "mars_retro": mars_retro}


def window_lean(windows: list, key_start="start", key_end="end") -> float:
    """Duration-weighted lean of a window list, bull=+1 bear=-1."""
    def mins(s):
        h, m = s.split(":")
        return int(h) * 60 + int(m)
    total, acc = 0, 0.0
    for w in windows:
        dur = max(0, mins(w[key_end]) - mins(w[key_start]))
        total += dur
        acc += dur * TONE_SIGN.get(w["tone"], 0)
    return acc / total if total else 0.0


def features_for(iso: str) -> dict:
    d = datetime.date.fromisoformat(iso)
    x = saptarsh.day(d)
    nak = x["moon"]["nakshatra"]
    rec = {"date": iso, "weekday": d.weekday(), "nak": nak,
           "sign": x["moon"]["sign"],
           "nak_lord": DASHA_LORDS[NAKSHATRAS.index(nak) % 9],
           "nak_change": x["moon"]["nakshatra_change"] is not None,
           "sign_change": x["moon"]["sign_change"] is not None,
           "tithi": x["panchang"]["tithi_num"],
           "amavasya": 30 in x["panchang"]["tithis_in_session"],
           "purnima": 15 in x["panchang"]["tithis_in_session"],
           "kshaya": x["panchang"]["kshaya_tithi"] is not None,
           "yoga": x["panchang"]["yoga"],
           "vishti": any(k["name"] == "Vishti" for k in x["panchang"]["karanas"]),
           "vt_tone": (x["panchang"]["vaar_tithi"] or {}).get("tone"),
           "vt_source": (x["panchang"]["vaar_tithi"] or {}).get("source"),
           "vn_tone": (x["panchang"]["vaar_nakshatra"] or {}).get("tone"),
           "retro": x["mercury"]["retrograde"],
           "combust": x["mercury"]["combust"],
           "retro_mid": x["mercury_retro_midpoint"],
           "eclipse": x["eclipse"] is not None,
           "slow_ingress": any(i["kind"] == "sign" and i["planet"] in
                               ("Mars", "Jupiter", "Saturn", "Uranus")
                               for i in x["ingresses"]),
           "station": any(i["kind"] == "station" for i in x["ingresses"]),
           "sun_moon_session": any(a["in_session"] and {a["a"], a["b"]} ==
                                   {"Sun", "Moon"} for a in x["aspects"]),
           "n_session_aspects": sum(1 for a in x["aspects"] if a["in_session"]),
           "nifty_lean": window_lean(x["windows"]),
           "metal_lean": window_lean(x["metal_windows"]),
           "session_aspects": [(a["a"], a["angle"], a["b"], a["tone"], a["source"])
                               for a in x["aspects"] if a["in_session"]],
           "day_aspects": [(a["a"], a["angle"], a["b"], a["tone"], a["source"])
                           for a in x["aspects"] if "(+1)" not in a["time"]],
           }
    for inst in INSTRUMENTS:
        rec[f"{inst}_tone"] = x["calls"][inst]["tone"]
        rec[f"{inst}_source"] = x["calls"][inst]["source"]
        rec[f"{inst}_base"], _ = saptarsh.nak_tone(nak, x["moon"]["sign"], inst)
    rec.update(cheap_regime(d))
    return rec


def phase_features(workers: int) -> str:
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"features_{START}_{END}.jsonl")
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            done = {json.loads(line)["date"] for line in f if line.strip()}
    days = [(START + datetime.timedelta(days=i)).isoformat()
            for i in range((END - START).days + 1)]
    todo = [d for d in days if d not in done]
    print(f"features: {len(done)} cached, {len(todo)} to compute")
    if todo:
        with open(path, "a", encoding="utf-8") as f, \
                ProcessPoolExecutor(max_workers=workers) as ex:
            for i, rec in enumerate(ex.map(features_for, todo, chunksize=20)):
                f.write(json.dumps(rec) + "\n")
                if i % 200 == 0:
                    print(f"  {i}/{len(todo)} {rec['date']}", flush=True)
    return path


# ------------------------------------------------------------ evaluate

def load_features(path: str) -> dict:
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                out[r["date"]] = r
    return out


def returns(index: str) -> dict:
    bars = prices.load(index, START - datetime.timedelta(days=10), END)
    out = {}
    prev = None
    for b in bars:
        if prev:
            out[b["date"]] = {"oc": b["close"] / b["open"] - 1,
                              "cc": b["close"] / prev["close"] - 1}
        prev = b
    return out


def score(label: str, pairs: list, base_up: float) -> dict:
    """pairs: [(predicted sign +1/-1, realised return)]."""
    n = len(pairs)
    hits = sum(1 for s, r in pairs if (r > 0) == (s > 0) and r != 0)
    # what "always call the majority side" would score on these days
    ups = sum(1 for _, r in pairs if r > 0)
    naive = max(ups, n - ups) / n if n else 0
    # a mixed bull/bear call gets credit on down days too, so the fair
    # benchmark is the majority side on these very days, not the up-rate
    s = stats.summarise(hits, n, naive if n else base_up, label)
    s["naive"] = naive * 100
    s["p_binom"] = _binom_p(hits, n, 0.5)
    return s


def event(label: str, rets: list, all_rets: list) -> dict:
    """An event study: up-rate and mean return on event days vs all."""
    n = len(rets)
    ups = sum(1 for r in rets if r > 0)
    base_up = sum(1 for r in all_rets if r > 0) / len(all_rets)
    med_abs = statistics.median(abs(r) for r in all_rets)
    wide = sum(1 for r in rets if abs(r) > med_abs)
    s = stats.summarise(ups, n, base_up, label)
    s["mean_bp"] = statistics.mean(rets) * 1e4 if n else 0.0
    s["all_mean_bp"] = statistics.mean(all_rets) * 1e4
    s["wide_rate"] = wide / n * 100 if n else 0.0
    s["p_binom_vs_base"] = _binom_p(ups, n, base_up)
    return s


def _binom_p(k: int, n: int, p: float) -> float:
    """Exact two-sided binomial p-value, in log space so n in the
    thousands does not overflow (stats.binom_two_sided uses math.comb
    times a float and dies around n = 1,100)."""
    if n == 0 or p <= 0 or p >= 1:
        return 1.0
    lp, lq = math.log(p), math.log(1 - p)

    def logpmf(i):
        return (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                + i * lp + (n - i) * lq)
    obs = logpmf(k)
    total = 0.0
    for i in range(n + 1):
        li = logpmf(i)
        if li <= obs + 1e-9:
            total += math.exp(li)
    return min(1.0, total)


def permutation_p(pairs: list, hits: int, rng: random.Random,
                  n_perm: int = 2000, block: int = 5) -> float:
    """Moving-block shuffle of the realised returns under the fixed
    prediction sequence; p = share of shuffles scoring >= observed."""
    preds = [s for s, _ in pairs]
    rets = [r for _, r in pairs]
    ge = 0
    for _ in range(n_perm):
        sh = stats.block_shuffle(rets, block, rng)
        h = sum(1 for s, r in zip(preds, sh) if (r > 0) == (s > 0) and r != 0)
        ge += h >= hits
    return (ge + 1) / (n_perm + 1)


def phase_evaluate(path: str) -> dict:
    feats = load_features(path)
    rng = random.Random(20260828)
    results = {"window": [START.isoformat(), END.isoformat()], "instruments": {}}
    md = [f"# Saptarsh-style outlook — backtest {START} → {END}", "",
          "Method: `app/saptarsh.py` is run for every day of the window and",
          "its calls are scored against the realised move. Nifty = close vs",
          "open of the session (the call is a session call); gold / silver =",
          "COMEX front-month close vs previous close on the New-York-dated bar,",
          "which is the 03:30 → 27:30 IST Globex day the metals report covers.",
          "`base` is the up-rate over the same days; `naive` is what always",
          "calling the majority side would have scored on exactly those days;",
          "z is against base; p is the exact two-sided binomial against 50%;",
          "perm-p is a 2,000-draw moving-block permutation of the returns.",
          "Nothing here was tuned on these prices — the rules come from his",
          "posts, the base tables from classical texts.", ""]

    for inst in INSTRUMENTS:
        rets = returns(inst)
        key = "oc" if inst == "nifty" else "cc"
        days = [d for d in sorted(feats) if d in rets]
        all_r = [rets[d][key] for d in days]
        base_up = sum(1 for r in all_r if r > 0) / len(all_r)
        R = {"days": len(days), "base_up": base_up * 100, "headline": [],
             "by_year": [], "nakshatra": [], "rules": [], "aspects": []}
        md += [f"## {inst.upper()} — {len(days)} trading days, base up-rate "
               f"{base_up * 100:.1f}%", ""]

        # 1. final call
        def dir_pairs(filt):
            return [(TONE_SIGN[feats[d][f"{inst}_tone"]], rets[d][key])
                    for d in days if feats[d][f"{inst}_tone"] in TONE_SIGN and filt(feats[d])]
        head = []
        for label, filt in [("Final call, all directional days", lambda f: True),
                            ("  source = observed", lambda f: f[f"{inst}_source"] == "observed"),
                            ("  source = extrapolated", lambda f: f[f"{inst}_source"] == "extrapolated"),
                            ("  Mercury direct", lambda f: not f["retro"]),
                            ("  Mercury retrograde (his moratorium)", lambda f: f["retro"]),
                            ("Nakshatra base call alone",
                             None)]:
            if filt is None:
                pairs = [(TONE_SIGN[feats[d][f"{inst}_base"]], rets[d][key])
                         for d in days if feats[d][f"{inst}_base"] in TONE_SIGN]
            else:
                pairs = dir_pairs(filt)
            s = score(label, pairs, base_up)
            if label.startswith(("Final call", "Nakshatra")) and pairs:
                s["perm_p"] = permutation_p(pairs, s["hits"], rng)
            head.append(s)
        lean_key = "nifty_lean" if inst == "nifty" else "metal_lean"
        pairs = [(1 if feats[d][lean_key] > 0 else -1, rets[d][key])
                 for d in days if abs(feats[d][lean_key]) > 0.2]
        s = score("Window lean (duration-weighted, |lean| > 0.2)", pairs, base_up)
        if pairs:
            s["perm_p"] = permutation_p(pairs, s["hits"], rng)
        head.append(s)
        # volatile calls
        med_abs = statistics.median(abs(r) for r in all_r)
        vol_days = [d for d in days if feats[d][f"{inst}_tone"] == "vol"]
        wide = sum(1 for d in vol_days if abs(rets[d][key]) > med_abs)
        sv = stats.summarise(wide, len(vol_days), 0.5,
                             "'Volatile' call → |move| above median")
        sv["p_binom"] = _binom_p(wide, len(vol_days), 0.5)
        head.append(sv)
        R["headline"] = head
        md += ["| Test | n | hit | 95% CI | naive | z vs base | p | perm-p |",
               "|---|---|---|---|---|---|---|---|"]
        for s in head:
            md.append(f"| {s['label']} | {s['n']} | {s['rate']:.1f}% | "
                      f"[{s['ci_lo']:.1f}, {s['ci_hi']:.1f}] | "
                      f"{s.get('naive', 0):.1f}% | {s['z_vs_base']:+.2f} | "
                      f"{s['p_binom']:.3f} | {s.get('perm_p', float('nan')):.3f} |")
        md.append("")

        # 2. by year
        by_year = defaultdict(list)
        for d in days:
            t = feats[d][f"{inst}_tone"]
            if t in TONE_SIGN:
                by_year[d[:4]].append((TONE_SIGN[t], rets[d][key]))
        md += ["Per year (final call): " + " · ".join(
            f"{y} {score(y, p, base_up)['rate']:.1f}% (n={len(p)})"
            for y, p in sorted(by_year.items())), ""]
        R["by_year"] = [{"year": y, **score(y, p, base_up)} for y, p in sorted(by_year.items())]

        # 3. nakshatra table
        rows = []
        for nak in NAKSHATRAS:
            rs = [rets[d][key] for d in days if feats[d]["nak"] == nak]
            if not rs:
                continue
            call, src = saptarsh.nak_tone(nak, "", inst) if inst == "nifty" \
                else saptarsh.nak_tone(nak, "", inst)
            e = event(nak, rs, all_r)
            e["call"] = call
            e["source"] = src
            rows.append(e)
        R["nakshatra"] = rows
        md += ["### Moon nakshatra at the open", "",
               "| Nakshatra | his call | n | up-rate | mean (bp) | z | p vs base |",
               "|---|---|---|---|---|---|---|"]
        for e in rows:
            md.append(f"| {e['label']} | {e['call']} ({e['source'][:3]}) | {e['n']} | "
                      f"{e['rate']:.1f}% | {e['mean_bp']:+.1f} | {e['z_vs_base']:+.2f} | "
                      f"{e['p_binom_vs_base']:.3f} |")
        md.append("")

        # 4. rules as event studies
        RULES = [
            ("Amavasya in session", lambda f: f["amavasya"]),
            ("Purnima in session", lambda f: f["purnima"]),
            ("Kshaya tithi", lambda f: f["kshaya"]),
            ("Vishti karana in session", lambda f: f["vishti"]),
            ("Vaidhriti yoga", lambda f: f["yoga"] == "Vaidhriti"),
            ("Vyatipata yoga", lambda f: f["yoga"] == "Vyatipata"),
            ("Mercury retrograde", lambda f: f["retro"]),
            ("Mercury retro midpoint", lambda f: f["retro_mid"]),
            ("Mercury combust", lambda f: f["combust"]),
            ("Eclipse day", lambda f: f["eclipse"]),
            ("Sun–Moon aspect in session", lambda f: f["sun_moon_session"]),
            ("Slow-planet sign ingress (Mars..Uranus)", lambda f: f["slow_ingress"]),
            ("Planetary station", lambda f: f["station"]),
            ("Kaal Sarp yog", lambda f: f["kaal_sarp"]),
            ("Mars retrograde", lambda f: f.get("mars_retro", False)),
            ("Grand trine", lambda f: f["grand_trine"]),
            ("Nakshatra stellium (≥3)", lambda f: f["nak_stellium"]),
            ("Sign stellium (≥4)", lambda f: f["sign_stellium"]),
            ("Early-degree cluster (≥6 under 10°)", lambda f: f["early_degree"]),
            ("Moon in Scorpio (debilitated)", lambda f: f["sign"] == "Vrischika"),
            ("Moon in Taurus (exalted)", lambda f: f["sign"] == "Vrishabha"),
            ("Moon in a Rahu-ruled star", lambda f: f["nak_lord"] == "Rahu"),
            ("Moon in a Saturn-ruled star", lambda f: f["nak_lord"] == "Saturn"),
            ("Moon in a Venus/Jupiter-ruled star", lambda f: f["nak_lord"] in ("Venus", "Jupiter")),
            ("Vaar-Tithi observed bullish", lambda f: f["vt_tone"] == "bull" and f["vt_source"] == "observed"),
            ("Vaar-Tithi observed bearish", lambda f: f["vt_tone"] == "bear" and f["vt_source"] == "observed"),
            ("Vaar-Tithi classical bullish", lambda f: f["vt_tone"] == "bull" and f["vt_source"] == "classical"),
            ("Vaar-Tithi classical bearish", lambda f: f["vt_tone"] == "bear" and f["vt_source"] == "classical"),
            ("Vaar-Nakshatra bullish", lambda f: f["vn_tone"] == "bull"),
            ("Vaar-Nakshatra bearish", lambda f: f["vn_tone"] == "bear"),
            ("Nakshatra changes in session", lambda f: f["nak_change"]),
            ("Moon changes sign in session", lambda f: f["sign_change"]),
        ]
        rules = []
        for label, filt in RULES:
            rs = [rets[d][key] for d in days if filt(feats[d])]
            if len(rs) < 8:
                continue
            rules.append(event(label, rs, all_r))
        R["rules"] = rules
        survivors = sum(1 for e in rules if e["p_binom_vs_base"] < 0.05 / len(rules))
        R["bonferroni"] = {"tests": len(rules), "alpha": 0.05 / len(rules),
                           "survivors": survivors}
        md += ["### Rules as event studies (direction; 'wide' = |move| above the median)", "",
               "| Rule | n | up-rate | base | mean (bp) | all (bp) | wide | z | p vs base |",
               "|---|---|---|---|---|---|---|---|---|"]
        for e in rules:
            md.append(f"| {e['label']} | {e['n']} | {e['rate']:.1f}% | {base_up * 100:.1f}% | "
                      f"{e['mean_bp']:+.1f} | {e['all_mean_bp']:+.1f} | {e['wide_rate']:.0f}% | "
                      f"{e['z_vs_base']:+.2f} | {e['p_binom_vs_base']:.3f} |")
        md += ["", f"{len(rules)} rule tests; Bonferroni α = {0.05 / len(rules):.4f}; "
                   f"**{survivors} survive**.", ""]

        # 5. observed aspects
        asp_key = "session_aspects" if inst == "nifty" else "day_aspects"
        hits_by = defaultdict(list)
        for d in days:
            for a, ang, b, tone, src in feats[d][asp_key]:
                if src == "observed" and tone in TONE_SIGN:
                    hits_by[(a, ang, b, tone)].append(rets[d][key])
        arows = []
        for (a, ang, b, tone), rs in sorted(hits_by.items(), key=lambda kv: -len(kv[1])):
            if len(rs) < 15:
                continue
            e = event(f"{a} {ang} {b} → {tone}", rs, all_r)
            hit = sum(1 for r in rs if (r > 0) == (TONE_SIGN[tone] > 0) and r != 0)
            e["hit_rate"] = hit / len(rs) * 100
            e["p_hit"] = _binom_p(hit, len(rs), 0.5)
            arows.append(e)
        R["aspects"] = arows
        md += ["### Observed aspect labels (exact hit on the day; n ≥ 15)", "",
               "| Aspect → his label | n | label hit | up-rate | mean (bp) | p (hit vs 50%) |",
               "|---|---|---|---|---|---|"]
        for e in arows:
            md.append(f"| {e['label']} | {e['n']} | {e['hit_rate']:.1f}% | {e['rate']:.1f}% | "
                      f"{e['mean_bp']:+.1f} | {e['p_hit']:.3f} |")
        md.append("")
        results["instruments"][inst] = R

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "RESULTS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    print("\n".join(md[:60]))
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", action="store_true")
    ap.add_argument("--evaluate", action="store_true")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()
    both = not a.features and not a.evaluate
    path = os.path.join(OUT, f"features_{START}_{END}.jsonl")
    if a.features or both:
        path = phase_features(a.workers)
    if a.evaluate or both:
        phase_evaluate(path)
