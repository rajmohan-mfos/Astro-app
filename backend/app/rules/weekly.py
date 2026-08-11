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
from .base import Finding
from .graph import bias, pick_chain

SECTION = "weekly"


def rules(chart: dict) -> list[Finding]:
    inp = chart["input"]
    year, month, day = (int(v) for v in inp["date"].split("-"))
    window = transit.sun_nak_window(year, month, day, inp["tz_offset"])

    p = pick_chain(chart, "Sun")
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

    halves = []
    for label, span, planet, count in [
            ("First half", f"{window['start']} → {window['mid']}",
             p["first"], p["first_count"]),
            ("Second half", f"{window['mid']} → {window['end']}",
             p["second"], p["second_count"])]:
        g = grahas[planet]
        b, reason = bias(count, planet, g["retro"])
        halves.append(b)
        out.append(Finding(
            SECTION,
            f"{label} ({span}): {b.upper()}",
            f"{planet} at degree-house {count} from the Sun — {reason}.",
            "Weekly & Monthly class @ 04:24–06:40 + கிரகங்கள் house table"))

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
