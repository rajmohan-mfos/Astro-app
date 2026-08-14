"""Weekly / monthly prediction rules — GRAHA MARKETS method.

Source [W]: WEEKLY AND MONTHLY PREDICTION transcript (video RlwVKdrwlAw).
Same chain logic as the intraday method, but:
- anchored on the SUN (key planet for the month, [NOTES] + [W @ 00:42])
- the window is the Sun-nakshatra period, not the calendar month
  ("take the month when the stars change", [W @ 00:28])
- house counts are DEGREE-based: 30° spans measured from the Sun's own
  degree ("from this 24th to this 24th is the first", [W @ 02:38–03:23];
  "you need to maintain 30 degrees", [W @ 07:41])
- X rules the first half of the window, Y the second [W @ 05:44–06:04]
"""
from .. import transit
from .base import Finding, date_slice
from .graph import bias, cast_chart, degree_house, pick_chain
from .stocks import stock_finding

SECTION = "weekly"


def rules(chart: dict) -> list[Finding]:
    inp = chart["input"]
    year, month, day = (int(v) for v in inp["date"].split("-"))
    window = transit.sun_nak_window(year, month, day, inp["tz_offset"])

    # The chain must be read off the SAME chart the window came from:
    # sun_nak_window is KP, so the chain is too (cast_chart = KP at
    # sunrise). Reading the chain off the raw display chart left one
    # prediction straddling two zodiacs AND two cast moments.
    p = pick_chain(cast_chart(chart), "Sun")
    grahas = p["grahas"]
    out = []

    out.append(Finding(
        SECTION,
        f"Window: Sun in {window['nak']} ({window['lord']}'s star)",
        f"{window['start']} → {window['end']}. The prediction month runs "
        f"star-change to star-change, not calendar dates; first half to "
        f"{window['mid']}, second half after.",
        "Weekly & Monthly class @ 00:28–01:26"))

    out.append(Finding(
        SECTION,
        "Chain selection (from Sun)",
        f"X={p['x']}, Y={p['y']}, X1={p['x1'] or '—'}, Y1={p['y1'] or '—'} "
        f"→ using {p['first']} (first half) and {p['second']} (second half).",
        "Weekly & Monthly class @ 01:41–03:54"))

    # each half is shared EQUALLY among the occupants of its star — the
    # same rule Class 11 states for the Jupiter window and Class 10 for
    # the intraday x1/x2 split
    sun = grahas["Sun"]["lon"]
    halves = []
    for label, a, b_, planets, occ in [
            ("First half", window["start"], window["mid"],
             p["x_occupants"] or [p["x"]], bool(p["x_occupants"])),
            ("Second half", window["mid"], window["end"],
             p["y_occupants"] or [p["y"]], bool(p["y_occupants"]))]:
        for i, planet in enumerate(planets):
            span_from, span_to = date_slice(a, b_, i, len(planets))
            count = (degree_house(grahas[planet]["lon"], sun) if occ
                     else degree_house(sun, grahas[planet]["lon"]))
            b, reason = bias(count, planet, grahas[planet]["retro"])
            if i == 0:
                halves.append(b)
            part = (f"{label} part {i + 1}/{len(planets)}"
                    if len(planets) > 1 else label)
            out.append(Finding(
                SECTION,
                f"{part} ({span_from} → {span_to}): {b.upper()}",
                f"{planet} at degree-house {count} from the Sun — {reason}.",
                "Weekly & Monthly class @ 04:24–06:40 + கிரகங்கள் house table"))
            # [W] "the stocks that are available in Mars — 7 to 14 Feb;
            # the stocks in Venus — 14 to 19 Feb": the window stretch's
            # planet names the stocks to trade in that stretch
            sf = stock_finding(
                planet, f"{part.lower()} ({span_from} → {span_to})",
                section=SECTION,
                source="Weekly & Monthly class (stocks of the half's "
                       "planet) + GRAPH ASTRO-4.pptx slide 1")
            if sf:
                out.append(sf)

    if "angle" in halves:
        which = "first" if halves[0] == "angle" else "second"
        other = "second" if which == "first" else "first"
        out.append(Finding(
            SECTION,
            "Angle in the window — expect a reversal",
            f"The {which} half carries an angle count, so it should run "
            f"opposite to the {other} half (the teacher's Feb example: "
            f"first half down, second half recovering up).",
            "Weekly & Monthly class @ 06:36–06:40"))

    out.append(Finding(
        "monthly",
        f"Next window from {window['end']}: {window['next_lord']}'s star",
        f"The monthly picture chains successive Sun-star windows; recompute "
        f"this chart dated {window['end']} for the next stretch.",
        "Weekly & Monthly class @ 06:10–06:22"))

    out.append(Finding(
        SECTION,
        "Confirm with prasanam before acting",
        "The teacher repeatedly warns not to take positions from the "
        "weekly/monthly chart alone without a prasanam confirmation.",
        "Weekly & Monthly class @ 06:44–07:04"))

    return out
