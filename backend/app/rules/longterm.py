"""Long-term investment rules — GRAHA MARKETS Astro Class 11 (+ LT part 2).

Anchor = JUPITER (yearly key planet, [NOTES] + [C11 @ 00:13]). Window = the
Jupiter-nakshatra period ("Jupiter is in [Rahu's star] … in 22nd Mars is
changed" — his July 2021 example is a retrograde ingress into Dhanishta,
stable for ~6 months, [C11 @ 01:28–03:10]). Chain identical to the other
horizons (X = Jupiter's star lord, X1/Y1 overrides), degree-counts from
Jupiter. X-side rules the window's first half, Y-side the second; the
teacher splits the Y half further along the deeper star chain (his Venus →
Moon example, 1.5 months each, [C11 @ 08:53–09:19]).
"""
from .. import transit
from .base import Finding
from .graph import STAR_QUALITY, bias, nak_lord_of, pick_chain

SECTION = "long_term"


def rules(chart: dict) -> list[Finding]:
    inp = chart["input"]
    year, month, day = (int(v) for v in inp["date"].split("-"))
    window = transit.jupiter_nak_window(year, month, day, inp["tz_offset"])

    p = pick_chain(chart, "Jupiter")
    grahas = p["grahas"]
    out = []

    out.append(Finding(
        SECTION,
        f"Window: Jupiter in {window['nak']} ({window['lord']}'s star)",
        f"{window['start']} → {window['end']} (~{window['days']} days). The "
        f"long-term horizon runs until Jupiter's star changes — confirm in "
        f"the panchangam that it holds before predicting; first half to "
        f"{window['mid']}, second half after.",
        "Astro Class 11 @ 01:28–03:10"))

    out.append(Finding(
        SECTION,
        "Chain selection (from Jupiter)",
        f"X={p['x']}, Y={p['y']}, X1={p['x1'] or '—'}, Y1={p['y1'] or '—'} "
        f"→ using {p['first']} (first half) and {p['second']} (second "
        f"half). The teacher splits the second half again along the deeper "
        f"star chain when it continues (his Venus 8 → Moon 3 example).",
        "Astro Class 11 @ 03:14–04:46, 08:53–09:19"))

    for label, span, planet, count in [
            ("First half", f"{window['start']} → {window['mid']}",
             p["first"], p["first_count"]),
            ("Second half", f"{window['mid']} → {window['end']}",
             p["second"], p["second_count"])]:
        g = grahas[planet]
        b, reason = bias(count, planet, g["retro"])
        out.append(Finding(
            SECTION,
            f"{label} ({span}): {b.upper()}",
            f"{planet} at degree-house {count} from Jupiter — {reason}. "
            f"Stocks belonging to {planet} follow this bias in this "
            f"stretch (see the stock findings for the planet's tickers).",
            "Astro Class 11 @ 04:38–05:48 + கிரகங்கள் house table"))

    out.append(Finding(
        SECTION,
        "Prediction-day checklist",
        "Make the long-term prediction on a clean day: transit Moon NOT in "
        "5/8/12 from your rasi, avoid Rahu/Ketu interference, and validate "
        "the entry with a prasanam question (2/6/11 = profit; 5/12 median "
        "loss, 8 heavy loss; 6 median profit, 11 heavy profit).",
        "Astro Class 11 @ 06:00–06:34 + LT part 2 @ 03:32–05:48"))

    return out
