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
import json
import os

from .base import Finding
from . import graph, panchang_rules

SECTION = "graph"

# ---------------------------------------------------------------------
# TWO SETS OF NUMBERS LIVE HERE.
#
# TAUGHT_*  are the course's own values, exactly as sourced in
#           knowledge/RULES-SOURCES.md. They are the app's provenance and
#           are never edited by a fitting run.
#
# FITTED_*  are learned from 15 years of Nifty by
#           scripts/opt/fit_tables.py, stored in fitted_tables.json.
#
# MODE picks which the score uses. The displayed classifications (Rikta,
# Vyatipata, ...) always stay taught, so the reading you see is still the
# course's — only the arithmetic changes.
#
# HONESTY REQUIREMENT: in fitted mode the tally is tuned ON the same
# history it is scored against. Its in-sample accuracy is flattering and
# is NOT a forecast; out-of-sample the same procedure lands at the
# always-down base rate. Every finding emitted in fitted mode says so, and
# tests enforce that it does.
# ---------------------------------------------------------------------
MODE = os.environ.get("ASTRO_SCORE_MODE", "taught").lower()

# star-lord temperament → tally value (guide §2 / [C3-Buzz])
TAUGHT_STAR_VALUE = {"Mercury": 1.0, "Venus": 0.5, "Moon": 0.5, "Sun": 0.0,
                     "Mars": -0.5, "Saturn": -1.0, "Ketu": -1.0}
AMPLIFIERS = {"Jupiter", "Rahu"}      # amplify the prevailing tally

TAUGHT_CHAIN_WEIGHTS = {"bullish": 1.0, "sideways-bullish": 0.5,
                        "sideways": 0.0, "angle": 0.0,
                        "sideways-bearish": -0.5, "bearish": -1.0}

# Back-compat aliases — the taught tables remain the module's public
# constants, so importers and the scenario tests are unaffected.
STAR_VALUE = TAUGHT_STAR_VALUE
CHAIN_WEIGHTS = TAUGHT_CHAIN_WEIGHTS

_FITTED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "fitted_tables.json")
_fitted = None


def fitted() -> dict | None:
    """The fitted tables, or None if a fitting run has never happened."""
    global _fitted
    if _fitted is None:
        if not os.path.exists(_FITTED_PATH):
            return None
        with open(_FITTED_PATH, encoding="utf-8") as f:
            _fitted = json.load(f)
    return _fitted


def active_mode() -> str:
    """'fitted' only if fitted mode is asked for AND tables exist."""
    return "fitted" if (MODE == "fitted" and fitted()) else "taught"


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


# [C9 @ 03:34–03:55] "so, 9, Saturn 1, so it is like half and half …
# it is like a small wave, wave, wave, wave, wave … all the stars are
# positive plus negative". A chain whose stretches CANCEL is taught as a
# distinct outcome — a choppy, small-range day — not the same thing as a
# chain with no push in it at all. Both land at a mean near zero, so the
# mean alone cannot tell them apart; the discriminator is how much force
# each stretch carries. Energy is the span-weighted mean of |weight|:
# bullish-then-bearish gives mean 0 with energy 1.0, while all-sideways
# gives mean 0 with energy 0.0.
SMALL_WAVE_MEAN_MAX = 0.25     # the flat band, same as _sign_word
SMALL_WAVE_ENERGY_MIN = 0.5    # one sideways-bullish/bearish pair


def chain_profile(chart: dict) -> dict:
    """Span-weighted mean of the chain's segment weights, and its energy."""
    segs = graph.build_segments(graph.cast_chart(chart))
    span = sum(s["end"] - s["start"] for s in segs) if segs else 0.0
    if not segs or not span:
        return {"score": 0.0, "energy": 0.0, "segments": len(segs or [])}
    weights = [(s["end"] - s["start"], CHAIN_WEIGHTS.get(s["bias"], 0.0))
               for s in segs]
    return {
        "score": round(sum(d * w for d, w in weights) / span, 2),
        "energy": round(sum(d * abs(w) for d, w in weights) / span, 2),
        "segments": len(segs),
    }


def chain_score(chart: dict) -> float:
    return chain_profile(chart)["score"]


def is_small_wave(score: float, energy: float) -> bool:
    """The taught 'half and half' day: stretches that cancel each other."""
    return (abs(score) <= SMALL_WAVE_MEAN_MAX
            and energy >= SMALL_WAVE_ENERGY_MIN)


def fitted_score(chart: dict) -> dict:
    """The engine's own tally with data-fitted numbers substituted in.

    Same five tables, same additive shape, same segments — only the values
    differ. Reported separately from the taught score so the two can be
    compared rather than conflated.
    """
    f = fitted()
    if not f:
        return {}
    t, w = f["tables"], f["component_weights"]
    cast = graph.cast_chart(chart)
    pan = cast["panchang"]
    moon = next(g for g in cast["grahas"] if g["name"] == "Moon")
    lord = graph.nak_lord_of(moon["lon"])

    segs = graph.build_segments(cast)
    chain = 0.0
    if segs:
        span = sum(s["end"] - s["start"] for s in segs) or 1.0
        for s in segs:
            chain += ((s["end"] - s["start"]) / span) * \
                t["chain_weights"].get(s["bias"], 0.0)

    total = (w["star_value"] * t["star_value"].get(lord, 0.0)
             + w["chain_weights"] * chain
             + w["thithi"] * t["thithi"].get(str(pan["thithi"]["num"]), 0.0)
             + w["yogam"] * t["yogam"].get(pan["yogam"]["name"], 0.0)
             + w["karanam"] * t["karanam"].get(pan["karanam"]["name"], 0.0))
    th = f["threshold"]
    call = "up" if total > th else ("down" if total < -th else "no call")
    return {"total": round(total, 4), "threshold": th, "call": call,
            "in_sample_rate": round(f["in_sample"]["rate"], 2),
            "out_of_sample_rate": round(f["out_of_sample"]["rate"], 2),
            "out_of_sample_edge_pp": round(
                f["out_of_sample"]["edge_pp"], 2)}


def day_score(chart: dict) -> dict:
    pan = panchang_tally(chart)
    prof = chain_profile(chart)
    chain = prof["score"]
    small_wave = is_small_wave(chain, prof["energy"])
    p_sign, c_sign = _sign_word(pan["total"]), _sign_word(chain)

    if c_sign == "flat":
        agreement = ("chain cancels out (small wave)" if small_wave
                     else "chain is directionless")
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

    out = {"panchang_total": pan["total"], "chain_score": chain,
           "chain_energy": prof["energy"], "small_wave": small_wave,
           "segments": prof["segments"],
           "panchang_sign": p_sign, "chain_sign": c_sign,
           "agreement": agreement, "conviction": conviction,
           "parts": pan["parts"], "star_lord": pan["lord"],
           "amplified": pan["amplified"], "chidra": pan["chidra"],
           "mode": active_mode()}
    fs = fitted_score(chart)
    if fs:
        out["fitted"] = fs
        # In fitted mode the fitted tables drive the day's CALL. The
        # taught fields above are deliberately left untouched, so the
        # course reading stays intact and readable next to it rather than
        # being silently overwritten by the fit.
        if active_mode() == "fitted":
            out["call"] = fs["call"]
            out["call_source"] = "fitted tables (15y Nifty)"
    return out


def fitted_finding(s: dict) -> Finding | None:
    """Surface the fitted call WITH the number that matters next to it.

    The in-sample rate is the one a reader will latch onto, so it never
    appears without the out-of-sample rate beside it.
    """
    f = s.get("fitted")
    if not f:
        return None
    return Finding(
        SECTION,
        f"Fitted tables: {f['call'].upper()} "
        f"(score {f['total']:+g}, threshold ±{f['threshold']:g})",
        f"Tables re-fitted to 15 years of Nifty rather than taken from the "
        f"course. In-sample {f['in_sample_rate']:g}% — but that is fitted "
        f"and scored on the same history, so it is not a forecast. "
        f"Out-of-sample the identical procedure gives "
        f"{f['out_of_sample_rate']:g}%, an edge of "
        f"{f['out_of_sample_edge_pp']:+g}pp over always-down. Treat the "
        f"first number as a description of the past and the second as the "
        f"honest expectation.",
        "scripts/opt/fit_tables.py — see knowledge/backtest/opt/"
        "OPTIMISATION.md")


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
    out = [Finding(
        SECTION,
        f"Day score: {s['conviction'].upper()} conviction "
        f"({s['panchang_sign']} panchang / {s['chain_sign']} chain)",
        detail,
        "Astro Class 3 'combine with whole concept' + guide §4 tally")]
    if s["small_wave"]:
        # the taught reading of a cancelling chain is about RANGE, which
        # "low conviction" alone does not say [C9 @ 03:34–03:55]
        out.append(Finding(
            SECTION,
            "Small-wave day — choppy, small range expected",
            f"The chain's stretches push hard in both directions and "
            f"cancel: mean {s['chain_score']:+g} but energy "
            f"{s['chain_energy']:g} across {s['segments']} stretches. The "
            f"teacher reads this as 'half and half … like a small wave, "
            f"wave, wave' — not a flat day, but a day that keeps "
            f"reversing inside a narrow range. That is a statement about "
            f"the SIZE of the swings, not their direction, and it is why "
            f"this differs from a merely directionless chain. Study aid, "
            f"not a signal.",
            "Astro Class 9 @ 03:34–03:55"))
    ff = fitted_finding(s)
    if ff:
        out.insert(0 if active_mode() == "fitted" else 1, ff)
    return out
