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


def rules(chart: dict) -> list[Finding]:
    from . import graph
    p = graph.pick_chain(graph.cast_chart(chart), "Moon")
    out = []
    for label, planet in (("first half", p["first"]),
                          ("second half", p["second"])):
        pure = stocks_of(planet, pure=True)
        shared = [s for s in stocks_of(planet) if s not in pure]
        if not pure and not shared:
            continue
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
        out.append(Finding(
            SECTION,
            f"Stocks for the {label} planet {planet}",
            detail,
            "GRAPH ASTRO-4.pptx slide 1 + Astro Class 4 @ 15:26"))
    return out
