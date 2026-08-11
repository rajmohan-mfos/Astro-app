"""Horai (planetary hour) golden rules — GRAPH PREDICTION -5.pptx [S5].

Horai timeline: equal one-hour slots from sunrise, Chaldean sequence
starting with the weekday lord (standard Tamil convention — the slide deck
assumes the reader knows it; confirm the convention against Class 7 when
its transcript is reviewed). Findings list each rule-matching horai window
that overlaps the market session 09:15–15:30.
"""
from .. import transit
from .base import Finding

SECTION = "graph"

SESSION_START = 9.25          # 09:15
SESSION_END = 15.5            # 15:30

# [S5] slides 2–6: weekday → {horai lord: (bias, detail)}
# Day-independent horai effects [C8/C9 + guide §7]. Every figure the
# teacher quotes is a MINIMUM ("you will get minimum points for each of
# these rules"), and the move concentrates in ~45 min of the hour —
# position ~5 minutes BEFORE the horai starts, not after it is under way.
HORAI_EFFECT = {
    "Sun": "down",
    # [C9] "That is vice versa — it will be opposite to what happened
    # before"; [C8] on a Tuesday it 'will definitely come down'. Both hold:
    # Saturn turns the prevailing move, which on a rising day means down.
    "Saturn": "REVERSAL — 'vice versa', turns whatever was happening "
              "before (on a rising day that means down)",
    "Mars": "negative bias",
    "Mercury": "up",
    "Jupiter": "amplifies the genuine trend",
    "Venus": "REVERSAL — the unexpected; do not trade through it, act on "
             "the new direction once it shows",
    "Moon": "no specific rule",
}

WINDOW_NOTE = ("Effect concentrates in ~45 minutes of the hour; position "
               "~5 minutes BEFORE the horai starts. Point figures are "
               "minimums, not targets.")

DAY_RULES = {
    "Monday": {
        "Mercury": ("UP", "Mercury horai on Monday — UP UP UP; ~100 points "
                          "Nifty minimum [C8]"),
    },
    "Tuesday": {
        "Saturn": ("DOWN", "Saturn horai on Tuesday — 'will definitely "
                           "come down': ~40–50 points Nifty / ~100 "
                           "BankNifty minimum. Buy puts / sell futures "
                           "before it starts; if it fails to fall, the day "
                           "becomes hard to bring down [C8]"),
    },
    "Wednesday": {
        "Venus": ("UP", "Venus horai on Wednesday — UP UP UP (75% up on a "
                        "normal natchathiram & thithi; 100% when both are "
                        "positive) [C8]"),
    },
    "Thursday": {
        "Sun": ("BANKNIFTY-UP", "Sun horai on Thursday with Karthigai "
                                "natchathiram — BankNifty positive"),
    },
    "Friday": {
        "Mercury": ("UP", "Mercury horai on Friday — UP UP UP; check "
                          "whether it lands around 2 p.m. [C8]"),
    },
}

# [C8] "Saturn horai + Uttaradam natchathiram will down the market" —
# the mega-crash tier, with its own magnitudes
UTHIRADAM_TIER = ("Uttara Ashadha",
                  "Saturn horai on Tuesday WITH Uthiradam natchathiram — "
                  "mega sell-off: ~100 points Nifty / ~300–400 BankNifty "
                  "minimum [C8]")


def _fmt(h: float) -> str:
    return f"{int(h):02d}:{round((h % 1) * 60):02d}"


def rules(chart: dict) -> list[Finding]:
    inp = chart["input"]
    year, month, day = (int(v) for v in inp["date"].split("-"))
    slots = transit.horai_timeline(year, month, day, inp["tz_offset"],
                                   inp["lat"], inp["lon"])
    vaara = chart["panchang"]["vaara"]["en"]
    nak = chart["panchang"]["natchathiram"]["name"]
    yogam_name = chart["panchang"]["yogam"]["name"]
    from .panchang_rules import yogam_bias
    yogam_bias_word = yogam_bias(yogam_name)[0]
    bad_yogam = yogam_bias_word in ("negative", "very negative")
    out = []

    day_rules = DAY_RULES.get(vaara, {})
    for slot in slots:
        if slot["end"] <= SESSION_START or slot["start"] >= SESSION_END:
            continue
        rule = day_rules.get(slot["lord"])
        if rule is None:
            continue
        bias, detail = rule
        if vaara == "Thursday" and slot["lord"] == "Sun" and nak != "Krittika":
            continue        # the Thursday Sun rule needs Karthigai
        # [EX] "If you see Budhan Hora on Friday you will doubt — on the
        # day of disease [Vyatipata], if you come on Friday market will
        # down." A negative yogam overrides an UP golden rule; panchang
        # gates the horai, per "first you see Yogo Karanam, second XY".
        if bias == "UP" and bad_yogam:
            bias = "UP — OVERRIDDEN"
            detail = (f"{detail}. BUT the day carries a "
                      f"{yogam_bias_word} yogam ({yogam_name}) — the "
                      f"teacher's own Example Chart shows the Friday "
                      f"Mercury rule failing on such a day and the market "
                      f"going down instead. Panchang gates the horai")
        # the Uthiradam mega-crash tier replaces the plain Tuesday rule
        if (vaara == "Tuesday" and slot["lord"] == "Saturn"
                and nak == UTHIRADAM_TIER[0]):
            bias, detail = "HEAVY DOWN", UTHIRADAM_TIER[1]
        out.append(Finding(
            SECTION,
            f"Horai {_fmt(slot['start'])}–{_fmt(slot['end'])} "
            f"({slot['lord']}): {bias}",
            f"{detail}. {WINDOW_NOTE}",
            "Astro Class 8 + GRAPH PREDICTION -5.pptx"))

    # [S5] slide 5: Thursday + Visagam natchathiram → positive (day-level)
    if vaara == "Thursday" and nak == "Vishakha":
        out.append(Finding(
            SECTION, "Thursday with Visagam natchathiram: POSITIVE",
            "Jupiter day-lord with Visagam natchathiram — positive day.",
            "GRAPH PREDICTION -5.pptx slide 5"))

    # [S5] slide 7 / [C8]: opens inside a Saturn OR Sun horai — down first,
    # then recovery once that horai ends
    opening = next((s for s in slots
                    if s["start"] <= SESSION_START < s["end"]), None)
    if opening and opening["lord"] in ("Saturn", "Sun"):
        out.append(Finding(
            SECTION,
            f"Market opens in {opening['lord']} horai "
            f"(ends {_fmt(opening['end'])})",
            f"Down into the open; after the {opening['lord']} horai ends "
            f"the market recovers — 30 points Nifty / 80+ BankNifty "
            f"minimum.",
            "Astro Class 8 + GRAPH PREDICTION -5.pptx slide 7"))

    # day-independent horai timeline for the session [C8/C9 + guide §7]
    timeline = []
    for slot in slots:
        if slot["end"] <= SESSION_START or slot["start"] >= SESSION_END:
            continue
        effect = HORAI_EFFECT.get(slot["lord"])
        if effect and effect != "no specific rule":
            timeline.append(f"{_fmt(slot['start'])}–{_fmt(slot['end'])} "
                            f"{slot['lord']}: {effect}")
    if timeline:
        out.append(Finding(
            SECTION, "Horai timeline (session overlay)",
            " · ".join(timeline) + f". {WINDOW_NOTE}",
            "Astro Class 8/9 + course guide §7"))

    # [C10] "When Saturn comes and when it matches [the graph], we can do
    # this — minimum 30 points, BN minimum 60 points, upside or downside."
    # Confluence = a golden-rule horai pointing the same way as the chain
    # segment covering that window.
    from . import graph as _graph
    try:
        segs = _graph.build_segments(_graph.cast_chart(chart))
    except Exception:
        segs = []
    UP, DOWN = {"UP", "BANKNIFTY-UP"}, {"DOWN", "HEAVY DOWN"}
    for slot in slots:
        rule = day_rules.get(slot["lord"])
        if rule is None or slot["end"] <= SESSION_START \
                or slot["start"] >= SESSION_END:
            continue
        mid = (max(slot["start"], SESSION_START)
               + min(slot["end"], SESSION_END)) / 2
        seg = next((s for s in segs if s["start"] <= mid < s["end"]), None)
        if seg is None:
            continue
        seg_up = seg["bias"] in ("bullish", "sideways-bullish")
        seg_dn = seg["bias"] in ("bearish", "sideways-bearish")
        if (rule[0] in UP and seg_up) or (rule[0] in DOWN and seg_dn):
            out.append(Finding(
                SECTION,
                f"Confluence {_fmt(slot['start'])}–{_fmt(slot['end'])}: "
                f"{slot['lord']} horai agrees with the chain",
                f"The {slot['lord']} horai and the {seg['planet']}"
                f"({seg['count']}) stretch point the same way — the "
                f"teacher's minimum expectation when graph and horai "
                f"match is 30 points Nifty / 60 points BankNifty, either "
                f"direction.",
                "Astro Class 10"))

    # [C8] index selection — day-independent, not part of any weekday rule
    out.append(Finding(
        SECTION, "Index selection: Nifty is the benchmark",
        "If Nifty and BankNifty diverge (or global cues conflict), trade "
        "NIFTY only — 'Nifty is the first economic trade'. When both move "
        "together either works, and BankNifty gives the larger points.",
        "Astro Class 8 @ divergence rule"))

    return out
