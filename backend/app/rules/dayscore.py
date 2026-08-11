"""Aggregate day score — the "combine, don't decide from one" rule.

[C3-Buzz] "we should not decide with one, we should combine with whole
concept" and "half effect of dhithi will be in yoga"; guide §4 "tally each
as +/- to score the day's bias, yogam carries roughly half-weight
alongside Tithi"; [EX-Buzz] precedence "First you see Yogo Karanam,
second you see XY" — panchang gates the chain, not the reverse.

Weights follow the sources:
- thithi and karanam: full ±1
- yogam: ±0.5 (±1 for the "அதித அசுபம்" extreme grades)
- nakshatra lord: graded ±1 / ±0.5 per the star-quality table
- Jupiter and Rahu star lords AMPLIFY rather than add — Jupiter
  "amplifies the prevailing condition", Rahu "everything happens big"
- Paksha Chidra (defective thithi) downgrades conviction one level

IMPORTANT: this reproduces the taught combination faithfully; it is NOT a
validated signal. The 5-year backtest found confluence days to be the
*least* reliable cell in the whole study (45.5%). See
knowledge/backtest/RESULTS.md.
"""
from .base import Finding
from . import graph, panchang_rules

SECTION = "graph"

# star-lord temperament → tally value (guide §2 / [C3-Buzz])
STAR_VALUE = {"Mercury": 1.0, "Venus": 0.5, "Moon": 0.5, "Sun": 0.0,
              "Mars": -0.5, "Saturn": -1.0, "Ketu": -1.0}
AMPLIFIERS = {"Jupiter", "Rahu"}      # amplify the prevailing tally

CHAIN_WEIGHTS = {"bullish": 1.0, "sideways-bullish": 0.5, "sideways": 0.0,
                 "angle": 0.0, "sideways-bearish": -0.5, "bearish": -1.0}


def _sign_word(v: float) -> str:
    if v > 0.25:
        return "positive"
    if v < -0.25:
        return "negative"
    return "flat"


def panchang_tally(chart: dict) -> dict:
    pan = graph.cast_chart(chart)["panchang"]
    parts = {}

    t_bias = panchang_rules.thithi_bias(pan["thithi"]["num"])[0]
    parts["thithi"] = {"positive": 1.0, "negative": -1.0}.get(t_bias, 0.0)

    k_bias = panchang_rules.karanam_bias(pan["karanam"]["name"])[0]
    parts["karanam"] = {"positive": 1.0, "negative": -1.0}.get(k_bias, 0.0)

    y_bias = panchang_rules.yogam_bias(pan["yogam"]["name"])[0]
    parts["yogam"] = {"positive": 0.5, "negative": -0.5,
                      "very negative": -1.0}.get(y_bias, 0.0)

    # nakshatra lord of the Moon, from the sunrise-cast chart
    cast = graph.cast_chart(chart)
    moon = next(g for g in cast["grahas"] if g["name"] == "Moon")
    lord = graph.nak_lord_of(moon["lon"])
    parts["nakshatra"] = STAR_VALUE.get(lord, 0.0)

    total = sum(parts.values())
    amplified = lord in AMPLIFIERS
    if amplified:
        total *= 1.5

    in_paksha = (pan["thithi"]["num"] - 1) % 15 + 1
    chidra = in_paksha in panchang_rules.PAKSHA_CHIDRA
    return {"parts": parts, "total": round(total, 2), "lord": lord,
            "amplified": amplified, "chidra": chidra,
            "biases": {"thithi": t_bias, "karanam": k_bias,
                       "yogam": y_bias}}


def chain_score(chart: dict) -> float:
    segs = graph.build_segments(graph.cast_chart(chart))
    if not segs:
        return 0.0
    span = sum(s["end"] - s["start"] for s in segs)
    total = sum((s["end"] - s["start"]) * CHAIN_WEIGHTS.get(s["bias"], 0.0)
                for s in segs)
    return round(total / span, 2) if span else 0.0


def day_score(chart: dict) -> dict:
    pan = panchang_tally(chart)
    chain = chain_score(chart)
    p_sign, c_sign = _sign_word(pan["total"]), _sign_word(chain)

    if c_sign == "flat":
        agreement = "chain is directionless"
    elif p_sign == "flat":
        agreement = "panchang neutral"
    elif p_sign == c_sign:
        agreement = "agree"
    else:
        agreement = "conflict"

    # conviction: panchang gates the chain [EX-Buzz precedence]
    if agreement == "conflict":
        conviction = "low"
    elif agreement == "agree" and abs(pan["total"]) >= 2:
        conviction = "high"
    elif agreement == "agree":
        conviction = "medium"
    else:
        conviction = "low"
    if pan["chidra"] and conviction in ("high", "medium"):
        conviction = "medium" if conviction == "high" else "low"

    return {"panchang_total": pan["total"], "chain_score": chain,
            "panchang_sign": p_sign, "chain_sign": c_sign,
            "agreement": agreement, "conviction": conviction,
            "parts": pan["parts"], "star_lord": pan["lord"],
            "amplified": pan["amplified"], "chidra": pan["chidra"]}


def rules(chart: dict) -> list[Finding]:
    s = day_score(chart)
    parts = ", ".join(f"{k} {v:+g}" for k, v in s["parts"].items() if v)
    detail = (f"Panchang tally {s['panchang_total']:+g} "
              f"({parts or 'all neutral'})"
              + (f", amplified by the {s['star_lord']} star lord"
                 if s["amplified"] else "")
              + (" — Paksha Chidra day, conviction reduced"
                 if s["chidra"] else "")
              + f". Chain {s['chain_score']:+g} ({s['chain_sign']}); "
              f"panchang {s['panchang_sign']} — {s['agreement']}. "
              f"Backtested confluence was the least reliable cell in the "
              f"5-year study; treat as study material, not a signal.")
    return [Finding(
        SECTION,
        f"Day score: {s['conviction'].upper()} conviction "
        f"({s['panchang_sign']} panchang / {s['chain_sign']} chain)",
        detail,
        "Astro Class 3 'combine with whole concept' + guide §4 tally")]
