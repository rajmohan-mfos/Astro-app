"""Panchang-element market biases — GRAHA MARKETS course.

Thithi: the five classical families, graded per the course guide §4A
(user-adjudicated 2026-08-10 — the guide's reading is applied in place of
C7-Buzz's tighter "beyond Jaya and Rikta the others are all neutral").
Karanam [C7 @ 11:25]; yogam lists from guide §4B + [EX-Buzz].
"""
from ..names import KARANA_MOVABLE
from . import graph
from .base import Finding

SECTION = "graph"

# (family, thithis within a paksha, bias, description) — course thithi
# sheet (OPTIONS MERSAL "திதிகளின் வகைகள்"), glosses translated verbatim
THITHI_FAMILIES = [
    ("Nanda", {1, 6, 11}, "positive", "gives joy and delight"),
    ("Bhadra", {2, 7, 12}, "positive", "suitable to begin all actions"),
    ("Jaya", {3, 8, 13}, "positive", "to conquer enemies — victory"),
    ("Rikta", {4, 9, 14}, "negative",
     "gives obstacles and sorrow — sharp gap-downs, 1000–2000 point drops"),
    ("Purna", {5, 10, 15}, "neutral", "suitable to complete all matters"),
]

# பகூச்சித்திரை — in BOTH pakshas these five are defective/weak thithis
PAKSHA_CHIDRA = {4, 6, 8, 12, 14}

# தக்க யோகத் திதிகள் — thithi + weekday pairs that form an auspicious
# combination (weekday index: Mon=0 … Sun=6)
THAKKA_YOGA = {(12, 6), (11, 0), (5, 1), (2, 2), (6, 3), (8, 4), (9, 5)}

# Panchami is called positive in a worked example ([EX-Buzz] "Panchami…
# Shashti — both are positive"), overriding its Purna family default.
WORKED_EXAMPLE_POSITIVE = {5}


def thithi_bias(num: int) -> tuple[str, str]:
    """num = 1..30 (1..15 Shukla, 16..30 Krishna)."""
    if num == 15:
        return "positive", "Pournami (full moon) — strong positive"
    if num == 30:
        return "negative", "Amavasai (new moon) — strong negative"
    in_paksha = (num - 1) % 15 + 1
    for family, members, bias, why in THITHI_FAMILIES:
        if in_paksha not in members:
            continue
        if in_paksha in WORKED_EXAMPLE_POSITIVE:
            return "positive", (f"{family} thithi (#{in_paksha}) — stated "
                                f"positive in a worked example")
        return bias, f"{family} thithi (#{in_paksha}) — {why}"
    return "neutral", "not in a flagged thithi group"


def karanam_bias(name: str) -> tuple[str, str]:
    """[C7 @ 11:25] 'the four Karanam at the end are negative, the first
    seven are positive' — movable karanas positive, fixed negative."""
    if name in KARANA_MOVABLE:
        return "positive", "movable karanam"
    return "negative", "fixed karanam (Kimstughna/Shakuni/Chatushpada/Naga)"


# Complete 27-yoga classification from the course yogam sheet (OPTIONS
# MERSAL): சுபம் = auspicious, அசுபம் = inauspicious, அதித அசுபம் =
# extremely inauspicious. Note several classically-benign yogas (Dhriti,
# Dhruva, Siddhi) are marked inauspicious in THIS system — follow the
# sheet, not the classical convention.
VERY_NEGATIVE_YOGAS = {"Vyaghata", "Vyatipata", "Vaidhriti"}
NEGATIVE_YOGAS = {"Vishkambha", "Atiganda", "Dhriti", "Shula", "Ganda",
                  "Dhruva", "Siddhi", "Parigha"} | VERY_NEGATIVE_YOGAS
POSITIVE_YOGAS = {"Priti", "Ayushman", "Saubhagya", "Shobhana", "Sukarman",
                  "Vriddhi", "Harshana", "Vajra", "Variyan", "Shiva",
                  "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra"}


def yogam_bias(name: str) -> tuple[str, str]:
    if name in VERY_NEGATIVE_YOGAS:
        return "very negative", "அதித அசுபம் — extremely inauspicious"
    if name in NEGATIVE_YOGAS:
        return "negative", "அசுபம் — inauspicious"
    if name in POSITIVE_YOGAS:
        return "positive", "சுபம் — auspicious"
    return "neutral", "not classified"


def rules(chart: dict) -> list[Finding]:
    import datetime

    pan = graph.cast_chart(chart)["panchang"]
    thithi, karanam, yogam = pan["thithi"], pan["karanam"], pan["yogam"]
    t_bias, t_reason = thithi_bias(thithi["num"])
    k_bias, k_reason = karanam_bias(karanam["name"])
    y_bias, y_reason = yogam_bias(yogam["name"])

    out = [
        Finding(
            SECTION,
            f"Thithi bias: {thithi['name']} — {t_bias.upper()}",
            f"{t_reason}.",
            "Course thithi sheet + Astro Classes 7/8"),
        Finding(
            SECTION,
            f"Yogam bias: {yogam['name']} — {y_bias.upper()}",
            f"{y_reason}." + (" Heavy downside pressure — a crash-risk day."
                              if y_bias == "very negative" else ""),
            "Course yogam sheet (27-yoga classification)"),
        Finding(
            SECTION,
            f"Karanam bias: {karanam['name']} — {k_bias.upper()}",
            f"{k_reason}.",
            "Astro Class 7 @ 11:25–11:31"),
    ]

    in_paksha = (thithi["num"] - 1) % 15 + 1
    if in_paksha in PAKSHA_CHIDRA:
        out.append(Finding(
            SECTION,
            f"Paksha Chidra day (thithi #{in_paksha})",
            "பகூச்சித்திரை — 4/6/8/12/14 in either paksha are defective "
            "thithis; treat the day's other signals with reduced "
            "conviction.",
            "Course thithi sheet"))

    inp = chart.get("input")
    if inp:
        y_, m_, d_ = (int(v) for v in inp["date"].split("-"))
        weekday = datetime.date(y_, m_, d_).weekday()
        if (in_paksha, weekday) in THAKKA_YOGA:
            out.append(Finding(
                SECTION,
                f"Thakka yogam: thithi #{in_paksha} on this weekday",
                "தக்க யோகத் திதி — an auspicious thithi/weekday pairing.",
                "Course thithi sheet"))
    return out
