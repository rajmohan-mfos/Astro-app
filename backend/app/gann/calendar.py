"""The cosmogram aspect calendar: every catalogued Gann rule's event
dates over a window, each carrying its measured evidence.

The catalogue deliberately ships the audit with the rule — a rule that
surfaces in the UI without its hit-rate-vs-base-rate attached would
quietly become a belief (gann-engine-CLAUDE.md §3). Verdict scale:

  paper-trade   the two rules whose numbers beat their base rate, still
                unproven (Venus–Jupiter L10, Mercury–Saturn L12)
  lean          directionally consistent across both indices, p ≈ 0.1
  null          measured at the noise floor
  rare          too few independent events to ever test
  calendar-trap the pattern is a season, not a signal

All astronomy is tropical (aspects.py). Weekend events carry a note —
the source's holiday convention maps them to the PREVIOUS session.
"""
import datetime

from . import aspects, natal

# Base rates every rule must beat (Nifty 2007–2026, measured in the
# course backtests; gann-engine-CLAUDE.md §4). The ±2-day flip rate is
# the important one: any "reversal within ±2 days" rule measures the
# calendar, not the sky.
BASE_RATES = {
    "trend_flip_any_day": "49%",
    "trend_flip_within_2_days": "85%",
    "positive_5d": "56%",
    "mean_5d_return": "+0.22%",
}

# kind: "transit" (both bodies transiting), "natal" (transit body vs
# fixed radix point), "natal-cross" (transit A vs natal B and vice
# versa), "station" (speed sign flip), "pattern" (multi-condition).
RULES = [
    {
        "id": "venus_jupiter_quadrature", "kind": "transit",
        "title": "Venus–Jupiter quadrature", "bodies": ["Venus", "Jupiter"],
        "angle": 90, "retro_excluded": True, "verdict": "paper-trade",
        "direction": "Reversal of the prevailing trend (judged on the "
                     "last 2–3 days); entry at the aspect-date close, "
                     "target 250–300 pts, stop 210–220, trail after target",
        "bias": "reversal",
        "timing": "Entry at the close of the aspect date (previous "
                  "session if closed); move expected within ~10 sessions",
        "evidence": "54% win rate vs 43% base on 26 decided trades "
                    "(14W/12L/10 undecided), +35 pts expectancy — the "
                    "best rule in the catalogue, still not statistically "
                    "significant. Claimed: >80%.",
        "source": "Gann_Trading_Course.md Lesson 10",
    },
    {
        "id": "mercury_saturn_conjunction", "kind": "transit",
        "title": "Mercury–Saturn conjunction", "bodies": ["Mercury", "Saturn"],
        "angle": 0, "retro_excluded": False, "verdict": "paper-trade",
        "direction": "Reversal of the prior 3–5 day trend, 400+ pts claimed",
        "bias": "reversal",
        "timing": "From the aspect date, against the prior 3–5-day trend",
        "evidence": "Trend flipped 16/23 (70%) vs 49% base, p=0.038 — the "
                    "strongest number in the project, but ~25 rules were "
                    "tested so one such false positive is expected, and "
                    "his own forward call (25 Feb 2025) failed.",
        "source": "Gann_Trading_Course.md Lesson 12",
    },
    {
        "id": "mars_jupiter_semisquare", "kind": "transit",
        "title": "Mars–Jupiter semisquare", "bodies": ["Mars", "Jupiter"],
        "angle": 45, "retro_excluded": False, "verdict": "lean",
        "direction": "Bullish (his standing call)",
        "bias": "bullish",
        "timing": "From the aspect date, ~5 trading days",
        "evidence": "+1.4% Nifty / +1.9% BankNifty 5-day forward, p≈0.1 — "
                    "directionally consistent on both indices, unproven.",
        "source": "Bjybnf_Gann_Concepts_Summary.md §7 backtest",
    },
    {
        "id": "mars_neptune_conjunction", "kind": "transit",
        "title": "Mars–Neptune conjunction", "bodies": ["Mars", "Neptune"],
        "angle": 0, "retro_excluded": False, "verdict": "lean",
        "direction": "Bearish (his standing call)",
        "bias": "bearish",
        "timing": "From the aspect date, ~5 trading days",
        "evidence": "−2.45% avg 5-day on Nifty at p=0.023 — but n=9, and "
                    "one of 36 tests where two false positives are "
                    "expected by chance.",
        "source": "Bjybnf_Gann_Concepts_Summary.md §7 backtest",
    },
    {
        "id": "venus_saturn_quadrature", "kind": "transit",
        "title": "Venus–Saturn quadrature", "bodies": ["Venus", "Saturn"],
        "angle": 90, "retro_excluded": False, "verdict": "null",
        "direction": "Reversal, 150–300 pts within 1–2 days claimed",
        "bias": "reversal",
        "timing": "1–2 trading days from the aspect date",
        "evidence": "57% vs a 55% base across all 40 events since 2007, "
                    "identical median excursions — and a ≥150-pt "
                    "counter-move within 2 days happens on 39% of ALL "
                    "days. Performs at the noise floor.",
        "source": "Gann_Trading_Course.md Lesson 7",
    },
    {
        "id": "jupiter_uranus_conjunction", "kind": "transit",
        "title": "Jupiter–Uranus conjunction/opposition",
        "bodies": ["Jupiter", "Uranus"], "angle": 0, "angles": [0, 180],
        "retro_excluded": False, "verdict": "rare",
        "direction": "Major reversal claimed at each rare pass",
        "bias": "reversal",
        "timing": "Weeks-to-months horizon; each event is a triple pass "
                  "over ~9 months",
        "evidence": "7 exact passes since 2007, 1 produced the claimed "
                    "reversal. Retrogradation makes each 'rare event' a "
                    "triple pass over ~9 months — only the pass followed "
                    "by a fall was shown.",
        "source": "Gann_Trading_Course.md Lesson 5",
    },
    {
        "id": "venus_natal_venus", "kind": "natal",
        "title": "Venus–natalVenus", "bodies": ["Venus"],
        "angles": [60, 90, 120], "angle": None,
        "retro_excluded": True, "verdict": "null",
        "direction": "Reversal 1–2 days after the aspect date",
        "bias": "reversal",
        "timing": "Flip expected 1–2 days AFTER the aspect date "
                  "(weekend → the following Monday)",
        "evidence": "The flagship birth-chart rule: sextile scored 10/15 "
                    "(67%) vs a 64% base — not the claimed 85%; "
                    "quadrature and trine averaged −0.1% to +0.9%, all "
                    "p>0.37. No edge at any of the three angles.",
        "source": "Gann_Trading_Course.md Lesson 8 + backtest sheet",
    },
    {
        "id": "mercury_mars_radix", "kind": "natal-cross",
        "title": "Mercury–Mars radix–transit conjunction",
        "bodies": ["Mercury", "Mars"], "angle": 0,
        "retro_excluded": False, "verdict": "null",
        "direction": "Reversal with a '1–2 day deflection' claimed",
        "bias": "reversal",
        "timing": "At the aspect date ±2 days (his 'deflection' window)",
        "evidence": "Reversal at the exact date 5/13 (38%) — below the "
                    "49% random-day rate. With his ±2-day deflection it "
                    "reads 85%… which is exactly the base rate of any "
                    "random day. The window manufactures the accuracy.",
        "source": "Gann_Trading_Course.md Lesson 6",
    },
    {
        "id": "jupiter_natal_jupiter", "kind": "natal",
        "title": "Jupiter–natalJupiter opposition", "bodies": ["Jupiter"],
        "angles": [180], "angle": 180,
        "retro_excluded": False, "verdict": "rare",
        "direction": "Bullish 'always' — his only unidirectional claim",
        "bias": "bullish",
        "timing": "1–6 month horizon from each pass",
        "evidence": "Once per ~11.9-year orbit, as a triple pass. The "
                    "Aug 2025 pass ran +4.4% at three months (his first "
                    "graded forward hit); the Feb 2026 pass of the same "
                    "triple was followed by −5%. Too rare to establish.",
        "source": "Gann_Trading_Course.md Lesson 13",
    },
    {
        "id": "venus_station", "kind": "station",
        "title": "Venus station", "bodies": ["Venus"], "angle": None,
        "retro_excluded": False, "verdict": "null",
        "direction": "Reversal at the station (either direction) claimed "
                     "~90% for Nifty",
        "bias": "reversal",
        "timing": "At the station date (both Rx start and Rx end count)",
        "evidence": "All 22 stations 2007–2026: flip at the date 55% vs "
                    "49% base; within ±2 days 95% vs an 85% base. "
                    "Mercury's 118 stations flip at the same 55% — the "
                    "slow-planet accuracy claim isn't in the data.",
        "source": "Gann_Trading_Course.md Lesson 9",
    },
    {
        "id": "sun_uranus_neptune", "kind": "pattern",
        "title": "Sun–Uranus–Neptune triangle",
        "bodies": ["Sun", "Uranus", "Neptune"], "angle": None,
        "retro_excluded": False, "verdict": "calendar-trap",
        "direction": "Reversal claimed when Sun quincunxes both while "
                     "Uranus sextiles Neptune",
        "bias": "reversal",
        "timing": "During the window (in practice: mid-to-late October)",
        "evidence": "Uranus–Neptune sit within 5° of sextile on 11% of "
                    "all days — the Sun supplies all the timing, so the "
                    "'rare pattern' recurs every mid-to-late October. "
                    "1 of 3 windows produced a flip.",
        "source": "Gann_Trading_Course.md Lesson 11",
    },
]


def _daterange(start: datetime.date, days: int) -> list[datetime.date]:
    return [start + datetime.timedelta(days=i) for i in range(days)]


def _market_note(d: datetime.date) -> str | None:
    # NSE holidays aren't modelled; weekends cover most mapped dates.
    if d.weekday() >= 5:
        prev = d - datetime.timedelta(days=d.weekday() - 4)
        return (f"{d.strftime('%A')} — market closed; his holiday rule "
                f"uses the previous session ({prev.isoformat()})")
    return None


def _event(rule: dict, d: datetime.date, *, angle: float | None,
           detail: str, retro: list[str], end: datetime.date | None = None
           ) -> dict:
    excluded = rule["retro_excluded"] and bool(retro)
    return {
        "date": d.isoformat(),
        "end_date": end.isoformat() if end else None,
        "rule_id": rule["id"],
        "title": rule["title"],
        "kind": rule["kind"],
        "angle": angle,
        "detail": detail,
        "direction": rule["direction"],
        # bullish/bearish are his fixed-direction calls; "reversal"
        # rules flip whatever the prior trend was, so they carry no
        # fixed color — the UI renders them amber, not green/red
        "bias": rule["bias"],
        "timing": rule["timing"],
        "verdict": rule["verdict"],
        "evidence": rule["evidence"],
        "source": rule["source"],
        "retro": retro,
        "excluded": excluded,
        "market_note": _market_note(d),
    }


ASPECT_NAMES = {0: "conjunction", 30: "semisextile", 45: "semisquare",
                60: "sextile", 90: "quadrature", 120: "trine",
                135: "sesquisquare", 150: "quincunx", 180: "opposition"}


def scan(center: datetime.date, back: int, ahead: int) -> dict:
    """All catalogued rule events in [center-back, center+ahead]."""
    start = center - datetime.timedelta(days=back)
    dates = _daterange(start, back + ahead + 1)
    # one ephemeris pass; every rule reads from it
    daily = [aspects.positions(d) for d in dates]
    lons = {n: [day[n][0] for day in daily] for n in daily[0]}
    speeds = {n: [day[n][1] for day in daily] for n in daily[0]}
    nat = natal.radix()

    def retro_on(d: datetime.date, names: list[str]) -> list[str]:
        i = dates.index(d)
        return [n for n in names if speeds[n][i] < 0]

    events = []
    for rule in RULES:
        angles = rule.get("angles") or [rule["angle"]]
        if rule["kind"] == "transit":
            a, b = rule["bodies"]
            for ang in angles:
                for d in aspects.crossings(dates, lons[a], lons[b], ang):
                    events.append(_event(
                        rule, d, angle=ang,
                        detail=f"transit {a} {ASPECT_NAMES[ang]} transit {b}",
                        retro=retro_on(d, [a, b])))
        elif rule["kind"] == "natal":
            (body,) = rule["bodies"]
            fixed = [nat[body]] * len(dates)
            for ang in angles:
                for d in aspects.crossings(dates, lons[body], fixed, ang):
                    events.append(_event(
                        rule, d, angle=ang,
                        detail=f"transit {body} {ASPECT_NAMES[ang]} natal "
                               f"{body} ({nat[body]:.1f}°)",
                        retro=retro_on(d, [body])))
        elif rule["kind"] == "natal-cross":
            a, b = rule["bodies"]
            for t, n in ((a, b), (b, a)):
                fixed = [nat[n]] * len(dates)
                for d in aspects.crossings(dates, lons[t], fixed,
                                           rule["angle"]):
                    events.append(_event(
                        rule, d, angle=rule["angle"],
                        detail=f"transit {t} conjunct natal {n} "
                               f"({nat[n]:.1f}°)",
                        retro=retro_on(d, [t])))
        elif rule["kind"] == "station":
            (body,) = rule["bodies"]
            for d, label in aspects.stations(dates, speeds[body]):
                events.append(_event(rule, d, angle=None,
                                     detail=f"{body} {label}",
                                     retro=[]))
        elif rule["kind"] == "pattern":
            # Sun quincunx Uranus (orb 3) + Sun quincunx Neptune (orb 3)
            # + Uranus sextile Neptune (orb 5), simultaneously (L11).
            active = []
            for i in range(len(dates)):
                su = aspects.separation(lons["Sun"][i], lons["Uranus"][i])
                sn = aspects.separation(lons["Sun"][i], lons["Neptune"][i])
                un = aspects.separation(lons["Uranus"][i], lons["Neptune"][i])
                active.append(abs(su - 150) <= 3 and abs(sn - 150) <= 3
                              and abs(un - 60) <= 5)
            i = 0
            while i < len(dates):
                if active[i]:
                    j = i
                    while j + 1 < len(dates) and active[j + 1]:
                        j += 1
                    events.append(_event(
                        rule, dates[i], angle=None,
                        detail="Sun quincunx Uranus + Sun quincunx "
                               "Neptune + Uranus sextile Neptune",
                        retro=[], end=dates[j]))
                    i = j + 1
                else:
                    i += 1

    events.sort(key=lambda e: (e["date"], e["rule_id"]))
    return {
        "center": center.isoformat(),
        "start": dates[0].isoformat(),
        "end": dates[-1].isoformat(),
        "radix": {"date": natal.RADIX_DATE,
                  "positions": {k: round(v, 2) for k, v in nat.items()}},
        "base_rates": BASE_RATES,
        "events": events,
        "note": "Every verdict comes from the course backtests (Nifty "
                "2007–2026): no rule cleared a fair statistical bar. "
                "Study aid, not a trading signal.",
    }
