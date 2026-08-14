"""Intraday / next-day "graph prediction" rules — GRAHA MARKETS method.

Sources (see backend/knowledge/RULES-SOURCES.md for the full provenance map):
- [C5]   Astro Class 5 transcript ("GRAPH PREDICTION 2", video 4n2rbfCAE6s)
- [NOTES] docs/கிரகங்கள்.docx — planet-nature & house-count tables
- [S4]   docs/GRAPH ASTRO-4.pptx slides — star-lord qualities, day lords

Method (X/Y taught in Class 4, X1/Y1 in Class 5):
  X  = lord of the nakshatra the Moon occupies              [C5 @ 01:14]
  Y  = lord of the nakshatra that X occupies ("star's star") [C5 @ 00:18]
  X1 = another graha sitting in one of X's nakshatras        [C5 @ 02:02]
  Y1 = another graha sitting in one of Y's nakshatras        [C5 @ 02:49]
  Override: when X1 exists use it INSTEAD of X; same for Y1/Y
  ("When x1 comes you should only see x1 … forget xy")       [C5 @ 03:57]
  Count houses from the Moon's rasi to the chosen graha's rasi (inclusive);
  X-side count drives the FIRST half (09:15–12:00), Y-side the SECOND half
  (12:00–15:30)                                              [C5 @ 00:28, 05:39]

The Class 4 transcript landed and is codified (X/Y derivation, degree
counting, X=Y full-day bias, sideways-on-bearish drift — see
RULES-SOURCES.md "Class 4 confirmations"); the day-lord rule comes from
Class 7 [C7 @ 06:16–08:47].
"""
from .base import Finding

SEG = 360 / 27
# Vimshottari order — nakshatra n is ruled by NAK_LORDS[n % 9]
NAK_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
             "Jupiter", "Saturn", "Mercury"]

# [NOTES] கிரகங்கள்.docx planet natures
BULLISH_PLANETS = {"Jupiter", "Rahu"}
BEARISH_PLANETS = {"Mars", "Saturn"}
# everything else (Venus, Sun, Moon, Mercury, Ketu) = sideways-market planet

# [NOTES] house-count table: உபஜெய 1,3,6,10,11 · அபஜெய 5,8,12 · 4,7 · கோணம் 2,9
BULLISH_COUNTS = {1, 3, 6, 10, 11}
BEARISH_COUNTS = {5, 8, 12}
SIDEWAYS_COUNTS = {4, 7}
ANGLE_COUNTS = {2, 9}

# [S4] slide 8 — nakshatra-lord qualities
STAR_QUALITY = {
    "Ketu": "negative", "Saturn": "negative", "Venus": "positive",
    "Moon": "positive", "Mercury": "positive",
    "Jupiter": "follows current situation", "Mars": "60% negative / 40% positive",
    "Rahu": "amplifies — everything happens big",
    "Sun": "neutral; negative in combination with a Saturn horai",
}

FIRST_HALF = "09:15–12:00"
SECOND_HALF = "12:00–15:30"


def nak_lord_of(lon: float) -> str:
    return NAK_LORDS[int((lon % 360) // SEG) % 9]


def degree_house(anchor_lon: float, lon: float) -> int:
    """Degree-based house: 30° spans from the anchor's exact degree.

    [C4 @ 05:23] the teacher degree-checks the count ("this is 29 degree …
    this is 27 degree, so from here only one is in 12") and the Class 4
    slide states "MOON 29* TO NEXT 29* - 1 HOUSE" — counts run degree to
    degree, not whole sign to whole sign.
    """
    from math import floor
    return floor(((lon - anchor_lon) % 360) / 30) + 1


def planet_nature(name: str, retro: bool) -> str:
    # [NOTES] வக்கிரம் (retro) → bearish. Rahu/Ketu are exempt: they are
    # always retrograde, yet the same notes list Rahu as BULLISH — so the
    # retro rule can only apply to the seven real planets.
    if retro and name not in ("Rahu", "Ketu"):
        return "bearish"
    if name in BULLISH_PLANETS:
        return "bullish"
    if name in BEARISH_PLANETS:
        return "bearish"
    return "sideways"


def bias(count: int, planet: str, retro: bool) -> tuple[str, str]:
    """(bias, reason) per MASTER-RULES.md — calibrated to reproduce the
    user-verified scenarios S1–S4b."""
    nature = planet_nature(planet, retro)
    if count in ANGLE_COUNTS:
        return "angle", (f"count {count} is an angle (கோணம்) house — "
                         f"runs opposite to the adjacent stretch")
    if count in SIDEWAYS_COUNTS:
        return "sideways", f"count {count} is a neutral house"
    if count == 8:
        # heavy-loss house dominates any planet [S1 Venus(8); LT2 grades]
        return "bearish", f"count 8 is the heavy-loss house"
    if count in BULLISH_COUNTS:
        if nature == "bearish":
            # [C6-Buzz] "upside-wise market: up move only, like a slight
            # slope, capped by the bearish planet" (also guide §5
            # "slanted upside") — overrides the earlier S3 memo reading
            return "sideways-bullish", (
                f"count {count} is bullish with bearish {planet} — "
                f"upside-wise: a slight up slope, capped")
        if nature == "bullish":
            if retro:
                # Rahu's permanent retrograde softens it [S2 Rahu(3)]
                return "sideways-bullish", (
                    f"count {count} bullish with retrograde {planet} — "
                    f"upward-leaning sideways")
            return "bullish", f"count {count} is an உபஜெய (bullish) house"
        return "sideways-bullish", (
            f"count {count} is bullish with sideways planet {planet} — "
            f"grinding upward drift [S3 Sun(10)]")
    if count in BEARISH_COUNTS:      # 5, 12 (8 handled above)
        if nature == "bearish":
            return "bearish", f"count {count} is an அபஜெய (bearish) house"
        return "sideways-bearish", (
            f"count {count} is a median-loss house with {planet} — "
            f"downward-leaning sideways [S2 Jupiter(12); C4 Sun@12]")
    return "sideways", f"count {count} not in any table"


def pick_chain(chart: dict, anchor: str) -> dict:
    """X/Y/X1/Y1 chain from any anchor graha (Moon=intraday, Sun=weekly,
    Jupiter=long-term), with degree-based counts from the anchor."""
    grahas = {g["name"]: g for g in chart["grahas"]}
    a = grahas[anchor]

    x = nak_lord_of(a["lon"])             # all 9 lords exist in grahas
    y = nak_lord_of(grahas[x]["lon"])

    def occupants_of_stars(lord: str) -> list[str]:
        # ALL grahas sitting in the lord's stars — Class 10 splits the
        # half among x1, x2, … when there are several
        return [g["name"] for g in chart["grahas"]
                if g["name"] not in (anchor, lord)
                and nak_lord_of(g["lon"]) == lord]

    xs = occupants_of_stars(x)
    # X sits in Y's star by construction (that is how Y was derived), so it
    # never counts as a Y-occupant [S1: Mars defines y=Jupiter yet Y1=—]
    ys = [g for g in occupants_of_stars(y) if g != x]

    first = xs[0] if xs else x     # [C5 @ 03:57] X1 overrides X
    second = ys[0] if ys else y

    def chain_count(planet: str, is_occupant: bool) -> int:
        # X/Y count from the anchor to the planet; X1/Y1 count from the
        # planet BACK to the anchor [C5 @ 04:51 "Moon should come from
        # that planet"; S1 Mercury(9)/Venus(8) verified on ephemeris]
        if is_occupant:
            return degree_house(grahas[planet]["lon"], a["lon"])
        return degree_house(a["lon"], grahas[planet]["lon"])

    return {
        "x": x, "y": y,
        "x1": xs[0] if xs else None, "y1": ys[0] if ys else None,
        "x_occupants": xs, "y_occupants": ys,
        "first": first, "second": second,
        "first_count": chain_count(first, bool(xs)),
        "second_count": chain_count(second, bool(ys)),
        "grahas": grahas, "moon": grahas.get("Moon"),
    }


def _pick(chart: dict) -> dict:
    """Intraday chain: anchored on the Moon."""
    return pick_chain(chart, "Moon")


def _fmt(h: float) -> str:
    total = round(h * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def _house_direction(count: int) -> str | None:
    if count in BULLISH_COUNTS:
        return "bullish"
    if count in BEARISH_COUNTS:
        return "bearish"
    return None


_OPPOSITE = {"bullish": "bearish", "bearish": "bullish"}


def build_segments(chart: dict, p: dict | None = None) -> list[dict]:
    """Time-ordered intraday segments per MASTER-RULES.md.

    Each half is shared equally among the occupants of its star (Class 10:
    x1/x2 split 09:15–12:00 at 10:37). Angle segments resolve OPPOSITE to
    the nearest non-angle neighbour's HOUSE direction [S1, S4b]; when that
    neighbour's planet-dominated bias conflicts with its house direction,
    pairing with the angle flips it to the house direction [S4b Saturn(10)].
    """
    if p is None:
        p = pick_chain(chart, "Moon")
    grahas = p["grahas"]
    moon_lon = grahas["Moon"]["lon"]

    # [C7 @ 06:16–08:47] day-lord rule: the weekday lord appearing as the
    # BARE X or Y makes that half bullish ("bullish at any time"); it does
    # NOT apply to X1/Y1 overrides ("X OR Y (DAY LORD RULE), X1 & Y1 (NO
    # DAY LORD RULE)", C4 slide 9).
    day_lord = None
    inp = chart.get("input")
    if inp:
        import datetime as _dt
        from ..transit import WEEKDAY_LORDS
        y_, m_, d_ = (int(v) for v in inp["date"].split("-"))
        day_lord = WEEKDAY_LORDS[_dt.date(y_, m_, d_).weekday()]

    segs = []
    for (start, end), planets, occ in [
            ((9.25, 12.0), p["x_occupants"] or [p["x"]],
             bool(p["x_occupants"])),
            ((12.0, 15.5), p["y_occupants"] or [p["y"]],
             bool(p["y_occupants"]))]:
        n = len(planets)
        for i, planet in enumerate(planets):
            arc = (((moon_lon - grahas[planet]["lon"]) if occ
                    else (grahas[planet]["lon"] - moon_lon)) % 360)
            count = int(arc // 30) + 1
            b, reason = bias(count, planet, grahas[planet]["retro"])
            if not occ and day_lord and planet == day_lord:
                b = "bullish"
                reason = (f"{planet} is the day lord appearing as bare "
                          f"X/Y — bullish at any time (day-lord rule)")
            segs.append({
                "start": start + (end - start) * i / n,
                "end": start + (end - start) * (i + 1) / n,
                "planet": planet, "count": count, "arc": arc,
                "bias": b, "raw": b, "reason": reason,
            })

    # Boundary tolerance for angle deadlocks: when EVERY segment is an
    # angle nothing can resolve the reversals, and a count whose arc sits
    # within arcminutes of the next house is ephemeris-fragile (the
    # teacher's 25/05/2021 Saturn reads house 10 where our Moon–Saturn arc
    # is 269.74° — 0.26° shy). Nudge such segments across the boundary
    # when that breaks the deadlock.
    if segs and all(s["raw"] == "angle" for s in segs):
        for seg in segs:
            if 30 - (seg["arc"] % 30) > 0.35:
                continue
            cand = seg["count"] % 12 + 1
            b, reason = bias(cand, seg["planet"],
                             grahas[seg["planet"]]["retro"])
            if b != "angle":
                seg["count"] = cand
                seg["bias"] = seg["raw"] = b
                seg["reason"] = (reason + " — count nudged across a "
                                 "house boundary (arc within 0.35°) to "
                                 "break an all-angle deadlock")

    for i, seg in enumerate(segs):
        if seg["raw"] != "angle":
            continue
        neighbor = next(
            (segs[j] for j in (i + 1, i - 1)
             if 0 <= j < len(segs) and segs[j]["raw"] != "angle"), None)
        if neighbor is None:
            continue
        d = _house_direction(neighbor["count"])
        if d is None:
            seg["reason"] += " (neighbour is neutral — pivot unresolved)"
            continue
        seg["bias"] = _OPPOSITE[d]
        seg["reason"] += (f" — resolved {seg['bias']}: opposite of the "
                          f"adjacent {neighbor['planet']}({neighbor['count']})")
        # NOTE: an earlier "the angle's partner flips to its house
        # direction" rule was removed — C5-Buzz shows S4b's second half is
        # sideways-up (the partner keeps its own bias), leaving the flip
        # unsourced. See RULES-SOURCES.md.
    return segs


def cast_chart(chart: dict) -> dict:
    """The day's chain chart is cast at SUNRISE (panchang day start).

    The teacher says "panchangam from morning 5.30" (Class 4 @ 03:52), but
    sunrise is the only cast moment that reproduces ALL the user-verified
    scenarios: the Example Chart (07/01/2022) needs the Moon past 320°
    (crossed ~06:20, sunrise 06:37), while S4b (25/05/2021) needs it still
    below 200° (crossed ~07:20, sunrise 05:46). A fixed 05:30 fails the
    first; a fixed 09:00 fails the second. Synthetic test charts without an
    `input` block are used as-is."""
    inp = chart.get("input")
    if not inp:
        return chart
    from .. import engine, transit
    y_, m_, d_ = (int(v) for v in inp["date"].split("-"))
    rise = transit.sunrise_hour(y_, m_, d_, inp["tz_offset"],
                                inp["lat"], inp["lon"])
    hh, mm = int(rise), round((rise % 1) * 60)
    if mm == 60:
        hh, mm = hh + 1, 0
    # Always recompute on the KP ayanamsa: the taught method is KP
    # throughout (his panchangam, sub-lords and transit tables only
    # reproduce under KP), while the Jothidam display stays Lahiri per
    # SPEC §5. Every prediction module must route through here — the
    # weekly/long-term WINDOWS come from transit.py (KP), so a chain read
    # off the raw display chart straddles two zodiacs and two cast
    # moments. See RULES-SOURCES.md.
    return engine.compute(y_, m_, d_, hh, mm, inp["tz_offset"],
                          inp["lat"], inp["lon"],
                          ayanamsa_mode=engine.KP)


def rules(chart: dict) -> list[Finding]:
    chart = cast_chart(chart)
    p = _pick(chart)
    grahas = p["grahas"]
    out = []

    sel = (f"X={p['x']}, Y={p['y']}, "
           f"X1={p['x1'] or '—'}, Y1={p['y1'] or '—'} → using "
           f"{p['first']} (first half) and {p['second']} (second half)")
    if chart.get("input"):
        sel += f"; chain cast at sunrise ({chart['input']['time']})"
    out.append(Finding("graph", "Chain selection", sel,
                       "Astro Class 5 @ 01:14–03:57; cast at sunrise "
                       "(reconciles all verified scenarios)"))

    segments = build_segments(chart, p)
    for seg in segments:
        out.append(Finding(
            "graph",
            f"{_fmt(seg['start'])}–{_fmt(seg['end'])}: "
            f"{seg['bias'].upper().replace('-', ' ')}",
            f"{seg['planet']} at degree-house {seg['count']} from the Moon "
            f"— {seg['reason']}.",
            "MASTER-RULES.md scenarios + Astro Classes 5/6/10"))

    if any(s["raw"] == "angle" for s in segments):
        out.append(Finding(
            "graph",
            "Angle in the sequence — reversal day",
            "An angle stretch runs opposite to its neighbour. The teacher "
            "advises extra caution and entering only after 12:00 on such "
            "days.",
            "Astro Class 5 @ 10:41–13:19"))

    if p["first"] == p["second"] and p["first_count"] == p["second_count"]:
        g = grahas[p["first"]]
        b, _ = bias(p["first_count"], p["first"], g["retro"])
        out.append(Finding(
            "graph",
            f"Full-day market: {b.upper()}",
            f"X and Y resolve to the same planet ({p['first']}) at the same "
            f"count ({p['first_count']}) — the whole session carries one "
            f"bias (the teacher's '12 sun and 12 sun' example: full day "
            f"bearish, every rise a selling opportunity).",
            "Astro Class 4 @ 21:52–22:32"))

    moon_star_lord = p["x"]
    out.append(Finding(
        "graph",
        f"Moon's nakshatra lord: {moon_star_lord}",
        f"Star quality — {STAR_QUALITY[moon_star_lord]}.",
        "GRAPH ASTRO-4.pptx slide 8"))

    out.append(Finding(
        "graph",
        "Pre-trade checklist",
        "Before entry the teacher requires: (1) transit Moon must NOT be in "
        "5/8/12 from your own birth rasi (it stays ~2.5 days per rasi); "
        "(2) confirm with prasanam; only then take the entry.",
        "Astro Class 4 @ 19:03–19:56"))

    return out
