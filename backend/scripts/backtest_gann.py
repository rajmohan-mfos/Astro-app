"""Backtest of the Gann cosmogram catalogue (backend/app/gann/calendar.py).

Usage (from backend/):
    python scripts/backtest_gann.py

The catalogue's evidence strings came from the course archive; this is
the repo's own measurement, on the same Nifty / Bank Nifty bars and with
the same scoring as backtest_vikas.py. For every rule, every exact event
in 2011–2026 is mapped to a session (the course convention: the PREVIOUS
session when the aspect day is closed; the next-session mapping is also
scored) and judged on:
  * 5-session forward return and up-rate vs every other day
  * reversal: sign of the 5-session move after the date differs from the
    sign of the 3-session move before it (base = the same over all days)
  * the "flip within ±2 days" claim (base ≈ 85% — a calendar artefact)
  * the date candle: first cross of the event day's high/low within 5
    sessions and follow-through (backtest_vikas.candle_outcomes)
  * a month histogram per rule (calendar-trap check)
Multi-pass rules (Jupiter–Uranus, Jupiter–natal Jupiter) are reported as
they occur; with n < 10 nothing about them can be concluded.
"""
import datetime
import json
import os
import statistics
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "opt"))

from app.gann import calendar as gann_cal                  # noqa: E402
import backtest_vikas as bv                                # noqa: E402

OUT = os.path.join(HERE, "..", "knowledge", "backtest", "gann")
START = datetime.date(2011, 1, 1)
END = datetime.date(2026, 8, 28)


def all_events() -> list[dict]:
    span = (END - START).days
    center = START + datetime.timedelta(days=span // 2)
    res = gann_cal.scan(center, span // 2 + 5, span - span // 2 + 5)
    return [e for e in res["events"] if START.isoformat() <= e["date"] <= END.isoformat()]


def map_session(S: bv.Series, iso: str, convention: str) -> int | None:
    import bisect
    i = bisect.bisect_left(S.dates, iso)
    if i < S.n and S.dates[i] == iso:
        return i
    if convention == "next":
        return i if i < S.n else None
    return i - 1 if i > 0 else None


def reversal_stats(S: bv.Series, idxs: list[int]) -> dict:
    """Reversal = sign(5d after) != sign(3d before); flip2 = any of the
    sessions D-2..D+2 is a local turning point of the 3-day trend."""
    rev = n = flip2 = 0
    for i in idxs:
        if i < 5 or i + 5 >= S.n:
            continue
        n += 1
        before = S.bars[i]["close"] - S.bars[i - 3]["close"]
        after = S.bars[i + 5]["close"] - S.bars[i]["close"]
        rev += (before > 0) != (after > 0)
        # ±2-day version: a 3-day trend flip anchored on any of D-2..D+2
        hit = False
        for j in range(i - 2, i + 3):
            b = S.bars[j]["close"] - S.bars[j - 3]["close"]
            a = S.bars[j + 3]["close"] - S.bars[j]["close"]
            if (b > 0) != (a > 0):
                hit = True
                break
        flip2 += hit
    return {"n": n, "rev": rev, "flip2": flip2}


def base_reversal(S: bv.Series) -> dict:
    r = reversal_stats(S, list(range(S.n)))
    return {"rev": r["rev"] / r["n"], "flip2": r["flip2"] / r["n"]}


def score_rule(rule: dict, evs: list[dict], S: bv.Series, base: dict,
               brev: dict, convention: str) -> dict:
    idxs = sorted({map_session(S, e["date"], convention) for e in evs})
    idxs = [i for i in idxs if i is not None]
    cand = bv.test_candles(rule["title"], idxs, S, base)
    rv = reversal_stats(S, idxs)
    out = {"id": rule["id"], "title": rule["title"], "verdict_catalogue": rule["verdict"],
           "bias": rule["bias"], "evidence_catalogue": rule["evidence"],
           "n_events": len(evs), "n_sessions": len(idxs),
           "excluded_retro": sum(1 for e in evs if e["excluded"]),
           "months": dict(sorted(Counter(int(e["date"][5:7]) for e in evs).items())),
           "dates": [e["date"] for e in evs],
           "fwd": cand["fwd"], "candle": {k: cand[k] for k in ("follow_through", "same_day", "held")},
           "reversal": bv.rate(f"{rule['title']}: 5d reverses 3d trend", rv["rev"], rv["n"], brev["rev"]),
           "flip2": bv.rate(f"{rule['title']}: trend flip within ±2 days", rv["flip2"], rv["n"], brev["flip2"])}
    if rule["bias"] in ("bullish", "bearish") and 5 in cand["fwd"]:
        f = cand["fwd"][5]
        rs = [S.ret(i, 5) for i in idxs]
        rs = [r for r in rs if r is not None]
        hit = sum(1 for r in rs if (r > 0) == (rule["bias"] == "bullish"))
        b = base["fwd"][5]["up"] / 100 if rule["bias"] == "bullish" else 1 - base["fwd"][5]["up"] / 100
        out["direction"] = bv.rate(f"{rule['title']}: 5d goes the called way", hit, len(rs), b)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    events = all_events()
    series = bv.load_series(False)
    R = {"window": [START.isoformat(), END.isoformat()], "instruments": {}}
    by_rule = {}
    for e in events:
        by_rule.setdefault(e["rule_id"], []).append(e)
    for inst in ("nifty", "banknifty"):
        S = series[inst]
        base = bv.baseline(S)
        brev = base_reversal(S)
        R["instruments"][inst] = {
            "days": S.n, "base": {"ft": base["ft"] * 100, "held": base["held"] * 100,
                                  "rev": brev["rev"] * 100, "flip2": brev["flip2"] * 100,
                                  "mean5_bp": base["fwd"][5]["mean_bp"], "up5": base["fwd"][5]["up"]},
            "rules": {}}
        for rule in gann_cal.RULES:
            evs = by_rule.get(rule["id"], [])
            R["instruments"][inst]["rules"][rule["id"]] = {
                conv: score_rule(rule, evs, S, base, brev, conv) for conv in ("prev", "next")}
    write_report(R)
    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)
    print("written", OUT)


def write_report(R: dict) -> None:
    L = [f"# Gann cosmogram catalogue — backtest {R['window'][0]} → {R['window'][1]}", "",
         "Method: every exact event of every rule in `app/gann/calendar.py`",
         "(tropical, `aspects.crossings`), mapped to the previous session when",
         "the aspect day is closed (the course convention; the next-session",
         "mapping is in results.json). Scored against the same statistic on",
         "every other day. p = exact binomial vs base, or a random-subset",
         "permutation for mean returns. Nothing was fitted.", ""]
    for inst, I in R["instruments"].items():
        b = I["base"]
        L += [f"## {inst.upper()} — {I['days']} sessions; base: 5d mean {b['mean5_bp']:+.0f} bp, "
              f"5d up {b['up5']:.1f}%, 5d reverses 3d trend {b['rev']:.1f}%, "
              f"flip within ±2 days {b['flip2']:.1f}%, candle follow-through {b['ft']:.1f}%", "",
              "| rule (catalogue verdict) | events | +5d bp (p) | 5d up | reversal | flip ±2d | called direction | candle follow-through | months |",
              "|---|---|---|---|---|---|---|---|---|"]
        for rid, both in I["rules"].items():
            r = both["prev"]
            f5 = r["fwd"].get(5)
            d = r.get("direction")
            months = " ".join(f"{m}:{c}" for m, c in r["months"].items())
            ft = r["candle"]["follow_through"]
            L.append(
                f"| {r['title']} ({r['verdict_catalogue']}, {r['bias']}) | {r['n_events']}"
                f"{' (' + str(r['excluded_retro']) + ' retro-excluded)' if r['excluded_retro'] else ''} | "
                + (f"{f5['mean_bp']:+.0f} ({f5['p_mean']:.2f})" if f5 else "—") + " | "
                + (f"{f5['up']:.0f}%" if f5 else "—") + " | "
                f"{r['reversal']['hits']}/{r['reversal']['n']} = {r['reversal']['rate']:.0f}% (p {r['reversal']['p_binom_vs_base']:.2f}) | "
                f"{r['flip2']['rate']:.0f}% | "
                + (f"{d['hits']}/{d['n']} = {d['rate']:.0f}% vs {d['base']:.0f}% (p {d['p_binom_vs_base']:.2f})" if d else "— (reversal rule)")
                + f" | {ft['hits']}/{ft['n']} = {ft['rate']:.0f}% (p {ft['p_binom_vs_base']:.2f}) | {months} |")
        L.append("")
        L.append("Catalogue evidence strings, for comparison:")
        L.append("")
        for rid, both in I["rules"].items():
            r = both["prev"]
            L.append(f"- **{r['title']}** — {r['evidence_catalogue']}")
            L.append(f"  dates: {', '.join(r['dates'][:40])}{' …' if len(r['dates']) > 40 else ''}")
        L.append("")
    with open(os.path.join(OUT, "RESULTS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
