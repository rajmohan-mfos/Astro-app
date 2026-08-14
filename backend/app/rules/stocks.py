"""Nifty-50 stock → planet mapping — GRAPH ASTRO-4.pptx slide 1
("NIFTY 50 STOCKS AND THEIR PLANETS", OPTIONS MERSAL).

Usage per the videos: stocks of the half's chain planet follow that
half's bias [C4 @ 15:04, C6 @ 17:05, C11 @ 05:14]. Prefer stocks owned
PURELY by the signal planet — C4 rejects Cipla (Rahu+Sun) for a Sun
signal and takes Reliance (pure Sun) [C4 @ 15:26–16:32]. Neptune/Uranus
appear in a few rows; they are outside the engine's nine grahas and only
matter for exclusion from "pure" matches.
"""
from .base import Finding

SECTION = "graph"

STOCKS = {
    "ADANIPORTS": ["Saturn", "Mercury"], "ASIANPAINTS": ["Mars", "Neptune"],
    "AXISBANK": ["Jupiter", "Mercury"], "BAJAJ-AUTO": ["Mars", "Venus"],
    "BAJAJFINSERV": ["Jupiter", "Mercury", "Saturn"],
    "BAJFINANCE": ["Jupiter", "Mercury"], "BHARTIARTL": ["Mercury", "Moon"],
    "BPCL": ["Saturn", "Moon"], "CIPLA": ["Rahu", "Sun"],
    "COALINDIA": ["Saturn"], "DRREDDY": ["Rahu", "Sun"],
    "EICHERMOT": ["Mars", "Venus"], "GAIL": ["Ketu"],
    "GRASIM": ["Venus", "Moon"], "HCLTECH": ["Mercury", "Venus"],
    "HDFC": ["Mars", "Saturn"], "HDFCBANK": ["Jupiter", "Mercury"],
    "HEROMOTOCO": ["Mars", "Venus"], "HINDALCO": ["Moon"],
    "HINDPETRO": ["Saturn", "Moon"], "HINDUNILVR": ["Venus", "Moon"],
    "IBULHSGFIN": ["Jupiter", "Mercury", "Saturn"],
    "ICICIBANK": ["Jupiter", "Mercury"], "INDUSINDBK": ["Jupiter", "Mercury"],
    "INFRATEL": ["Mercury", "Moon"], "INFY": ["Mercury", "Moon"],
    "IOC": ["Saturn", "Moon"], "ITC": ["Venus", "Moon"],
    "KOTAKBANK": ["Jupiter", "Moon"], "LT": ["Mars", "Saturn"],
    "LUPIN": ["Rahu", "Sun"], "M&M": ["Mars", "Venus"],
    "MARUTI": ["Mars", "Venus"], "NTPC": ["Saturn", "Moon"],
    "ONGC": ["Ketu"], "POWERGRID": ["Mars", "Mercury"],
    "RELIANCE": ["Sun"], "SBIN": ["Jupiter", "Sun"],
    "SUNPHARMA": ["Rahu", "Sun"], "TATAMOTORS": ["Mars", "Venus"],
    "TATASTEEL": ["Saturn", "Uranus"], "TCS": ["Jupiter", "Venus"],
    "TECHM": ["Jupiter", "Venus"], "TITAN": ["Venus", "Moon"],
    "ULTRACEMCO": ["Moon"], "UPL": ["Mars", "Neptune"],
    "VEDL": ["Saturn"], "WIPRO": ["Jupiter", "Venus"],
    "YESBANK": ["Jupiter", "Mercury"], "ZEEL": ["Mercury", "Moon"],
}


GRAHAS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
          "Rahu", "Ketu"}


def stocks_of(planet: str, pure: bool = False) -> list[str]:
    """`pure` = the only GRAHA on the row. Neptune/Uranus are outside the
    nine and never disqualify a row — otherwise Asian Paints (Mars +
    Neptune), the teacher's own flagship long-term Mars trade, would be
    filtered out of a Mars day."""
    def graha_count(ps):
        return sum(1 for p in ps if p in GRAHAS)
    return sorted(s for s, ps in STOCKS.items()
                  if planet in ps and (not pure or graha_count(ps) == 1))


def stock_finding(planet: str, label: str, section: str = SECTION,
                  source: str = "GRAPH ASTRO-4.pptx slide 1 + Astro Class 4 "
                                "@ 15:26") -> Finding | None:
    """One finding naming the stocks of `planet`, or None if it owns none.

    Shared by every horizon — the rule is the same everywhere: stocks of
    the stretch's chain planet follow that stretch's bias [C4 @ 15:04
    intraday, W weekly "the stocks that are available in Mars", C11 @
    05:14 long-term "let us see what stock is there for Mars"].
    """
    pure = stocks_of(planet, pure=True)
    shared = [s for s in stocks_of(planet) if s not in pure]
    if not pure and not shared:
        return None
    detail = f"Pure {planet} stocks: {', '.join(pure) or '—'}."
    if planet in ("Rahu", "Ketu"):
        detail += (" Rahu/Ketu-combination stocks are corrupted — the "
                   "direction is roughly right but un-positionable "
                   "(whipsaws, false breakouts); the teacher skips "
                   "them.")
    if shared:
        detail += (f" Shared ({', '.join(shared[:6])}"
                   f"{'…' if len(shared) > 6 else ''}) — the teacher "
                   f"avoids mixed-planet stocks for a clean signal.")
    return Finding(section, f"Stocks for the {label}: {planet}", detail,
                   source)


def conjunctions(cast: dict) -> dict[str, list[str]]:
    """Grahas grouped by the rasi they occupy, for rasis holding 2+.

    Union = same rasi. That is the engine's idiom everywhere else (the
    house counts, the x/y occupancy split), and the teacher gives no orb;
    a degree-based orb would be an invention.
    """
    by_rasi: dict[str, list[str]] = {}
    for g in cast["grahas"]:
        if g["name"] in GRAHAS:
            by_rasi.setdefault(g["rasi"], []).append(g["name"])
    return {r: ps for r, ps in by_rasi.items() if len(ps) > 1}


def united_stocks(cast: dict) -> list[tuple[str, str, str]]:
    """(stock, "A+B", rasi) for every stock whose owners are united.

    [C2 @ 02:22–02:44] "Venus plus Moon — if there is a UNION between
    Venus and Moon, only then these things will happen … Adhani Pots,
    Saturn plus Mercury … then Adhani Pots will be good on that day."
    The stock's own two planets meeting is what is taught to move it —
    which is a different claim from either planet ruling a stretch of the
    day, the rule `stock_finding` already covers.
    """
    joined = conjunctions(cast)
    out = []
    for stock, owners in sorted(STOCKS.items()):
        grahas = [p for p in owners if p in GRAHAS]
        if len(grahas) < 2:
            continue
        for rasi, present in joined.items():
            pair = [p for p in grahas if p in present]
            if len(pair) >= 2:
                out.append((stock, " + ".join(pair), rasi))
                break
    return out


# A stellium makes the rule useless rather than powerful: six grahas in
# one rasi united the owners of 26 of the 50 stocks on 2021-02-10. The
# teacher's examples are always a single pair (Venus+Moon, Saturn+
# Mercury), so a day that "selects" half the index has not selected
# anything. Above this many the finding reports the degeneracy instead of
# presenting the list as picks.
SELECTIVITY_LIMIT = 6


def conjunction_rules(cast: dict, section: str = SECTION) -> list[Finding]:
    united = united_stocks(cast)
    if not united:
        return []
    if len(united) > SELECTIVITY_LIMIT:
        rasis = sorted({r for _, _, r in united})
        biggest = max(conjunctions(cast).items(), key=lambda kv: len(kv[1]))
        return [Finding(
            section,
            f"Conjunction rule not selective today "
            f"({len(united)} of {len(STOCKS)} stocks)",
            f"{len(biggest[1])} grahas sit together in {biggest[0]} "
            f"({', '.join(biggest[1])}), which unites the owning pairs of "
            f"{len(united)} stocks across {', '.join(rasis)}. The taught "
            f"rule keys on a stock's own two planets meeting, and the "
            f"teacher's examples are single pairs — Venus+Moon for ITC, "
            f"Saturn+Mercury for Adani Ports. A stellium satisfies it for "
            f"half the index at once, so it distinguishes nothing today "
            f"and no list is given. Reported rather than hidden, because "
            f"the list would otherwise read as 26 picks.",
            "Astro Class 2 @ 02:22–03:22 + GRAPH ASTRO-4.pptx slide 1")]
    lines = "; ".join(f"{s} ({pair} in {rasi})" for s, pair, rasi in united)
    return [Finding(
        section,
        f"Owning planets united — {len(united)} stock"
        f"{'s' if len(united) != 1 else ''} in play",
        f"{lines}. The teacher's rule is that a stock moves when its own "
        f"planets meet: 'if there is a union between Venus and Moon, only "
        f"then these things will happen' — his ITC example — and the same "
        f"for Saturn+Mercury and Adani Ports. Union is read here as "
        f"sharing a rasi; he states no orb. This is separate from the "
        f"chain rule above: that one asks which planet rules a stretch of "
        f"the day, this one asks which stocks have both their owners in "
        f"one place. Untested — the backtest covered indices, not single "
        f"stocks. Study aid, not a signal.",
        "Astro Class 2 @ 02:22–03:22 + GRAPH ASTRO-4.pptx slide 1")]


def rules(chart: dict) -> list[Finding]:
    from . import graph
    cast = graph.cast_chart(chart)
    p = graph.pick_chain(cast, "Moon")
    out = []
    # every occupant gets its slice of the half [C10 x1/x2 split], so
    # every occupant's stocks are listed — not just the first
    for half, planets in (("first half", p["x_occupants"] or [p["x"]]),
                          ("second half", p["y_occupants"] or [p["y"]])):
        for i, planet in enumerate(planets):
            label = (f"{half} part {i + 1}/{len(planets)}"
                     if len(planets) > 1 else f"{half} planet")
            f = stock_finding(planet, label)
            if f:
                out.append(f)
    out.extend(conjunction_rules(cast))
    return out
