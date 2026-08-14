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

# bias → the direction the half runs, for resolving an angle half against
# its neighbour ([W @ 06:36–06:40] "it should run opposite")
_DIRECTION = {"bullish": "up", "sideways-bullish": "up",
              "bearish": "down", "sideways-bearish": "down"}
_OPPOSITE = {"up": "down", "down": "up"}


def _half_bias(biases: list[str]) -> str:
    """One label for a half that may be split among several occupants.

    A half is only an angle when EVERY occupant is one — otherwise the
    occupants that carry a direction give the half its direction. The
    previous code took occupant 1 and ignored the rest, so a two-occupant
    half was represented by half its evidence.
    """
    directed = [b for b in biases if b in _DIRECTION]
    if not directed:
        return "angle" if "angle" in biases else (biases[0] if biases
                                                  else "sideways")
    return directed[0]


def _next_window_chain(chart: dict, window: dict) -> tuple[dict, dict] | None:
    """The chain of the FOLLOWING Sun-star window, computed inline.

    [W @ 06:10–06:22] the monthly picture is successive Sun-star windows
    chained together. Telling the reader to "recompute this chart dated
    X" left the app one step short of the taught method for no reason —
    the next window's start date is already known.

    Deliberately one window ahead and computed here rather than by
    re-entering rules(): the next window would name the one after it, and
    so on without end.
    """
    inp = dict(chart["input"])
    inp["date"] = window["end"]
    try:
        y2, m2, d2 = (int(v) for v in window["end"].split("-"))
        nxt = transit.sun_nak_window(y2, m2, d2, inp["tz_offset"])
        cast = cast_chart({"input": inp})
        return nxt, pick_chain(cast, "Sun")
    except (ValueError, KeyError):
        return None


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
    half_biases: list[list[str]] = []
    for label, a, b_, planets, occ in [
            ("First half", window["start"], window["mid"],
             p["x_occupants"] or [p["x"]], bool(p["x_occupants"])),
            ("Second half", window["mid"], window["end"],
             p["y_occupants"] or [p["y"]], bool(p["y_occupants"]))]:
        half_biases.append([])
        for i, planet in enumerate(planets):
            span_from, span_to = date_slice(a, b_, i, len(planets))
            count = (degree_house(grahas[planet]["lon"], sun) if occ
                     else degree_house(sun, grahas[planet]["lon"]))
            b, reason = bias(count, planet, grahas[planet]["retro"])
            half_biases[-1].append(b)
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

    # the half's label now reflects EVERY occupant, not just the first
    labels = [_half_bias(b) for b in half_biases] or halves
    if "angle" in labels:
        i = labels.index("angle")
        which, other = ("first", "second") if i == 0 else ("second", "first")
        neighbour = labels[1 - i] if len(labels) > 1 else None
        d = _DIRECTION.get(neighbour or "")
        resolved = _OPPOSITE.get(d or "")
        if resolved:
            title = (f"Angle in the {which} half — resolves {resolved.upper()}"
                     f" (opposite the {other} half)")
            detail = (f"The {which} half carries an angle count, so it runs "
                      f"opposite its neighbour. The {other} half is "
                      f"{neighbour} ({d}), so the angle half reads "
                      f"{resolved}. Same resolution the intraday chain "
                      f"uses — an angle takes the opposite of the nearest "
                      f"stretch that has a direction, rather than being "
                      f"left unresolved.")
        else:
            title = "Angle in the window — direction unresolved"
            detail = (f"The {which} half carries an angle count and should "
                      f"run opposite the {other} half, but that half is "
                      f"{neighbour or 'absent'} and carries no direction of "
                      f"its own, so there is nothing to invert. The "
                      f"teacher's Feb example resolves because his other "
                      f"half was directional; this window does not.")
        out.append(Finding(SECTION, title, detail,
                           "Weekly & Monthly class @ 06:36–06:40"))

    nxt = _next_window_chain(chart, window)
    if nxt:
        w2, p2 = nxt
        out.append(Finding(
            "monthly",
            f"Next window {w2['start']} → {w2['end']}: Sun in {w2['nak']} "
            f"({w2['lord']}'s star)",
            f"X={p2['x']}, Y={p2['y']}, X1={p2['x1'] or '—'}, "
            f"Y1={p2['y1'] or '—'} → {p2['first']} rules to {w2['mid']}, "
            f"then {p2['second']}. The monthly picture is successive "
            f"Sun-star windows chained together, and this is the next "
            f"link, cast on its own start date. Only one window ahead — "
            f"each window's chain must be read off a chart cast inside it.",
            "Weekly & Monthly class @ 06:10–06:22"))
    else:
        out.append(Finding(
            "monthly",
            f"Next window from {window['end']}: {window['next_lord']}'s star",
            f"The next window's chain could not be computed here; recompute "
            f"this chart dated {window['end']} for the next stretch.",
            "Weekly & Monthly class @ 06:10–06:22"))

    out.append(Finding(
        SECTION,
        "Confirm with prasanam before acting",
        "The teacher repeatedly warns not to take positions from the "
        "weekly/monthly chart alone without a prasanam confirmation.",
        "Weekly & Monthly class @ 06:44–07:04"))

    return out
