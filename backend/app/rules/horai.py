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
DAY_RULES = {
    "Monday": {
        "Mercury": ("UP", "Mercury horai on Monday — UP UP UP; expect "
                          "~100 points on Nifty, prefer Nifty over "
                          "BankNifty unless they diverge [C8 @ 05:20]"),
        "Venus": ("CAUTION", "Venus horai on Monday — unexpected reversal "
                             "window; don't trade during it, act on the "
                             "new direction after it ends [C8 @ 06:25]"),
    },
    "Tuesday": {
        "Saturn": ("DOWN", "Saturn horai on Tuesday — market down, ~40–50 "
                           "points Nifty / 70–80 BankNifty (put options "
                           "once the fall starts; if it fails to fall the "
                           "day becomes hard to bring down). Stronger when "
                           "the day's natchathiram is Uthiradam "
                           "[C8 @ 07:01–08:37]"),
    },
    "Wednesday": {
        "Venus": ("UP", "Venus horai on Wednesday — UP UP UP (75% up on a "
                        "normal natchathiram & thithi; 100% when both are "
                        "positive)"),
    },
    "Thursday": {
        "Sun": ("BANKNIFTY-UP", "Sun horai on Thursday with Karthigai "
                                "natchathiram — BankNifty positive"),
    },
    "Friday": {
        "Mercury": ("UP", "Mercury horai on Friday — UP UP UP"),
    },
}


def _fmt(h: float) -> str:
    return f"{int(h):02d}:{round((h % 1) * 60):02d}"


def rules(chart: dict) -> list[Finding]:
    inp = chart["input"]
    year, month, day = (int(v) for v in inp["date"].split("-"))
    slots = transit.horai_timeline(year, month, day, inp["tz_offset"],
                                   inp["lat"], inp["lon"])
    vaara = chart["panchang"]["vaara"]["en"]
    nak = chart["panchang"]["natchathiram"]["name"]
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
        out.append(Finding(
            SECTION,
            f"Horai {_fmt(slot['start'])}–{_fmt(slot['end'])} "
            f"({slot['lord']}): {bias}",
            detail + ".",
            "GRAPH PREDICTION -5.pptx"))

    # [S5] slide 5: Thursday + Visagam natchathiram → positive (day-level)
    if vaara == "Thursday" and nak == "Vishakha":
        out.append(Finding(
            SECTION, "Thursday with Visagam natchathiram: POSITIVE",
            "Jupiter day-lord with Visagam natchathiram — positive day.",
            "GRAPH PREDICTION -5.pptx slide 5"))

    # [S5] slide 7: general rule — market opens inside a Saturn horai
    opening = next((s for s in slots
                    if s["start"] <= SESSION_START < s["end"]), None)
    if opening and opening["lord"] == "Saturn":
        out.append(Finding(
            SECTION,
            f"Market opens in Saturn horai (ends {_fmt(opening['end'])})",
            "After the Saturn horai ends the market recovers — roughly 30 "
            "points on Nifty, 80+ on BankNifty.",
            "GRAPH PREDICTION -5.pptx slide 7"))

    return out
