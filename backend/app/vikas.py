"""Vikas — the "important dates" method, as a computable engine.

Provenance: backend/knowledge/vikas/NOTES.md (his classes 1–6, demo
classes). Vikas does not predict direction from astrology; he derives
DATES from planetary events and trades the date's daily candle
(high-cross long / low-cross short) on the chart. What the app can
compute is the date list, the day-lord table and the rule flags; the
candle trade stays with the trader.

Everything here is sidereal Lahiri (drikpanchang's default, which is
what he reads) except where he explicitly uses GannZilla's geocentric
tropical longitudes (the Moon-45° and Venus-45° dates), which are
computed both ways.
"""
import datetime

import swisseph as swe

from . import nse_holidays
from .engine import FLAGS
from .names import NAKSHATRAS, RASIS
from .transit import DASHA_LORDS, SEG, _next_cross

TZ = 5.5
IST = datetime.timezone(datetime.timedelta(hours=TZ))
OPEN_H, CLOSE_H = 9.25, 15.5                    # 09:15, 15:30 IST
SESSION_H = CLOSE_H - OPEN_H

# his benefic / malefic split [V5 @ 28:03–30:40]; the Moon is benefic
# only from Shukla Dashami to Krishna Panchami (tithi 10..20)
MALEFIC = {"Ketu", "Sun", "Mars", "Rahu", "Saturn"}
BENEFIC = {"Venus", "Jupiter", "Mercury"}
MOON_BENEFIC_TITHI = (10, 20)

SATURN_STARS = {"Pushya", "Anuradha", "Uttara Bhadrapada"}
MERCURY_STARS = {"Ashlesha", "Jyeshtha", "Revati"}
# star-lord → what he trades on those Moon days [V3 @ 05:00–12:00; V5 @ 40:40]
STAR_INSTRUMENT = {"Saturn": "Nifty / Reliance / oil & gas / IT",
                   "Jupiter": "Bank Nifty / banking / finance",
                   "Venus": "Bajaj Finance / luxury",
                   "Mars": "Hindalco / metals",
                   "Ketu": "Glenmark (pharma)"}

BIG = ["Jupiter", "Saturn", "Uranus", "Neptune", "Sun"]
SMALL = ["Mars", "Mercury", "Venus"]
BODIES = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
          "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
          "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
          "Rahu": swe.MEAN_NODE}
SIGN_PLANETS = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu"]

# Sun-nakshatra ingresses he singled out [V1 @ 29:02–51:26; VD2]
SUN_NAK_NOTES = {
    "Uttara Ashadha": "market does not fall that week (his '95%'); sell puts",
    "Shravana": "Moon-lorded star → bottom / support, reversal date",
    "Dhanishta": "bearish 2–3 days",
    "Rohini": "Moon-lorded star → minor top, reversal date",
    "Hasta": "Moon-lorded star → top (27 Sep 2024 ATH), reversal date",
}
MOON_SIGN_DATES = {
    "Mesha": "Nifty date, both days of the transit (6–7 Jan 2025 top, 3–4 Mar 2025 bottom) [V2]",
    "Meena": "counts as the Mesha date when Mesha falls on the weekend [V2]",
}
SAME_DEGREE = (("Sun", "Neptune", "bullish; buy above the date's high [V4]"),
               ("Venus", "Ketu", "reversal date [V4]"),
               ("Venus", "Rahu", "reversal date [V4]"),
               ("Mercury", "Ketu", "reversal — 30 Sep 2024 top, 11 Apr 2022 top [V2]"),
               ("Mercury", "Rahu", "reversal — 3 Mar 2025 bottom, 20 Mar 2024 bottom [V2]"))


def _jd(d: datetime.date, hour: float) -> float:
    return swe.julday(d.year, d.month, d.day, hour - TZ)


def _sid() -> None:
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)


def _lon(body: int, jd: float) -> float:
    return swe.calc_ut(jd, body, FLAGS)[0][0] % 360


def _sep(a: float, b: float) -> float:
    """Separation in [0, 360): b measured from a."""
    return (b - a) % 360


def _nature(lord: str, tithi: int) -> str:
    if lord == "Moon":
        lo, hi = MOON_BENEFIC_TITHI
        return "benefic" if lo <= tithi <= hi else "malefic"
    return "malefic" if lord in MALEFIC else "benefic"


def snapshot(d: datetime.date, hour: float) -> dict:
    """Longitudes and derived labels at one instant."""
    _sid()
    jd = _jd(d, hour)
    sid = {n: _lon(b, jd) for n, b in BODIES.items()}
    sid["Ketu"] = (sid["Rahu"] + 180) % 360
    ayan = swe.get_ayanamsa_ut(jd)
    trop = {n: (v + ayan) % 360 for n, v in sid.items()}
    nak_i = int(sid["Moon"] // SEG)
    tithi = int(_sep(sid["Sun"], sid["Moon"]) // 12) + 1
    return {"jd": jd, "sid": sid, "trop": trop,
            "moon_nak": NAKSHATRAS[nak_i],
            "moon_lord": DASHA_LORDS[nak_i % 9],
            "moon_sign": RASIS[int(sid["Moon"] // 30)],
            "tithi": tithi,
            "signs": {p: int(sid[p] // 30) for p in SIGN_PLANETS},
            "sun_nak": NAKSHATRAS[int(sid["Sun"] // SEG)],
            "mars_nak": NAKSHATRAS[int(sid["Mars"] // SEG)]}


def _clock(jd: float, d: datetime.date) -> str:
    total = round((jd - _jd(d, 0)) * 1440)
    h, m = divmod(total % 1440, 60)
    return f"{h:02d}:{m:02d}"


def session_star(d: datetime.date) -> dict:
    """The Moon nakshatra that owns the trading session [V5 @ 34:49].

    Rules he states: the star must be in force during market hours; if
    it starts after the close the next day is its date; a star that
    covers under ~4–5 h of the session is not a clean date [V3 @ 10:30].
    """
    o = snapshot(d, OPEN_H)
    jd_open, jd_close = o["jd"], _jd(d, CLOSE_H)
    nak_i = NAKSHATRAS.index(o["moon_nak"])
    end = _next_cross(lambda j: _lon(swe.MOON, j), ((nak_i + 1) % 27) * SEG,
                      jd_open, jd_open + 1.3, 0.05)
    covered = (min(end, jd_close) - jd_open) * 24 if end else SESSION_H
    covered = min(covered, SESSION_H)
    if covered >= SESSION_H / 2:
        nak, lord = o["moon_nak"], o["moon_lord"]
        clean = covered >= 4.0
        end_clock = None if not end or end > jd_close else _clock(end, d)
    else:                                   # the next star owns the session
        nak = NAKSHATRAS[(nak_i + 1) % 27]
        lord = DASHA_LORDS[(nak_i + 1) % 9]
        clean = (SESSION_H - covered) >= 4.0
        end_clock = _clock(end, d)
    return {"nakshatra": nak, "lord": lord,
            "nature": _nature(lord, o["tithi"]),
            "full_session": end is None or end > jd_close,
            "hours": round(covered if nak == o["moon_nak"] else SESSION_H - covered, 2),
            "clean": clean,
            "open_nakshatra": o["moon_nak"], "open_ends": end_clock,
            "tithi": o["tithi"], "moon_sign": o["moon_sign"],
            "signs": o["signs"]}


def next_trading_day(d: datetime.date) -> datetime.date:
    while not nse_holidays.is_trading_day(d):
        d += datetime.timedelta(days=1)
    return d


def _crossed(prev: float, now: float, target: float) -> bool:
    """Did an increasing angle pass `target` between two snapshots?
    (steps are < 15°, so the shorter arc is the true one)"""
    a = (target - prev) % 360
    b = (now - prev) % 360
    return 0 < a <= b < 180


def events_between(d: datetime.date, prev: dict | None = None,
                   now: dict | None = None) -> list[dict]:
    """Planetary events in (D-1 15:30, D 15:30] — i.e. the events whose
    'important date' is D by his after-close → next-day rule, before the
    holiday shift. Each: {family, label, note, instrument}."""
    p = prev or snapshot(d - datetime.timedelta(days=1), CLOSE_H)
    n = now or snapshot(d, CLOSE_H)
    out = []
    # 1. Sun nakshatra ingress
    if n["sun_nak"] != p["sun_nak"]:
        out.append({"family": "sun_nak", "label": f"Sun enters {n['sun_nak']}",
                    "note": SUN_NAK_NOTES.get(n["sun_nak"],
                                              "yearly date; trade the candle"),
                    "instrument": "Nifty", "key": n["sun_nak"]})
    # 2. sign ingresses of Mercury, Venus, Mars, Jupiter, Saturn
    for pl in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        if n["signs"][pl] != p["signs"][pl]:
            sign = RASIS[n["signs"][pl]]
            note, key = "sign date", sign
            if pl == "Mercury" and sign == "Mesha":
                note = "BIG date — the low is not closed below for months [V1]"
            if pl == "Mars":
                if n["signs"]["Mars"] == (n["signs"]["Saturn"] - 1) % 12:
                    even = (n["signs"]["Saturn"] + 1) % 2 == 0
                    note = (f"Mars in the 12th sign from Saturn → metals fall "
                            f"(Saturn in {'even' if even else 'odd'} sign: "
                            f"{'big' if even else 'small'} fall) [V4]")
                    key = "12th_from_saturn_even" if even else "12th_from_saturn_odd"
                elif n["signs"]["Mars"] == n["signs"]["Saturn"]:
                    note = "Mars joins Saturn's sign → metals rise [V4]"
                    key = "with_saturn"
            if pl == "Venus" and n["signs"]["Venus"] == n["signs"]["Jupiter"]:
                note = "Venus joins Jupiter's sign → bullish Nifty while together [V4]"
                key = "with_jupiter"
            if pl == "Jupiter" and n["signs"]["Venus"] == n["signs"]["Jupiter"]:
                note = "Jupiter joins Venus's sign → bullish Nifty while together [V4]"
                key = "with_venus"
            out.append({"family": f"{pl.lower()}_sign",
                        "label": f"{pl} enters {sign}", "note": note,
                        "instrument": "metals" if pl == "Mars" else "Nifty",
                        "key": key})
    # 3. Mars nakshatra ingress (Dhanishta = bearish metals)
    if n["mars_nak"] != p["mars_nak"]:
        out.append({"family": "mars_nak", "label": f"Mars enters {n['mars_nak']}",
                    "note": ("bearish for metals (Hindalco) [V1, V4]"
                             if n["mars_nak"] == "Dhanishta" else "metals date"),
                    "instrument": "metals", "key": n["mars_nak"]})
    # 4. big × small planet at 30° / 60° (either side), and conjunction
    for bn in BIG:
        for sn in SMALL:
            if bn == "Sun" and sn in ("Mercury", "Venus"):
                continue                     # never reach 60°; skip the pair
            sp = _sep(p["sid"][bn], p["sid"][sn])
            sn_ = _sep(n["sid"][bn], n["sid"][sn])
            for ang in (30, 60, 300, 330, 0):
                if _crossed(sp, sn_, ang) or _crossed(sn_, sp, ang):
                    a = ang if ang <= 180 else 360 - ang
                    out.append({"family": "big_small", "label": f"{bn} {a}° {sn}",
                                "note": ("bottoms (Jupiter 30° Mercury: 13 May 2024) [V1]"
                                         if a else "conjunction"),
                                "instrument": "Nifty", "key": f"{bn}-{sn}-{a}"})
                    break
    # 5. same-degree pairs he tests
    for a, b, note in SAME_DEGREE:
        sp, sn_ = _sep(p["sid"][a], p["sid"][b]), _sep(n["sid"][a], n["sid"][b])
        if _crossed(sp, sn_, 0) or _crossed(sn_, sp, 0):
            out.append({"family": "same_degree", "label": f"{a} conjunct {b}",
                        "note": note, "instrument": "Nifty", "key": f"{a}-{b}"})
    # 6. Venus within 8° of Uranus in the same sign [V2 @ 01:04:26–01:15:38;
    #    V6 @ 49:42]: the date is the day the orb closes to 8°
    # (GannZilla tropical: his 19 Apr 2021, 6 Jun 2022, 26 Jun 2025 all sit
    #  at an 8° tropical orb inside tropical Taurus)
    sp = _sep(p["trop"]["Uranus"], p["trop"]["Venus"])
    sn_ = _sep(n["trop"]["Uranus"], n["trop"]["Venus"])
    orb_p = min(sp, 360 - sp)
    orb_n = min(sn_, 360 - sn_)
    same_sign = int(n["trop"]["Venus"] // 30) == int(n["trop"]["Uranus"] // 30)
    if orb_p > 8 >= orb_n and same_sign:
        out.append({"family": "venus_uranus", "label": "Venus within 8° of Uranus",
                    "note": "big date; buy above its high — 19 Apr 2021, 26 Jun 2025 [V2]",
                    "instrument": "Nifty", "key": "8deg"})
    # 7. Venus at 45° (GannZilla tropical; sidereal variant flagged)
    for zod in ("trop", "sid"):
        if _crossed(p[zod]["Venus"], n[zod]["Venus"], 45):
            out.append({"family": f"venus45_{zod}", "label": f"Venus at 45° ({zod})",
                        "note": "11 May 2025 → 13 May bottom [V6]",
                        "instrument": "Nifty", "key": zod})
    return out


def moon_angle_date(d: datetime.date, orb: float = 2.5,
                    o: dict | None = None) -> list[dict]:
    """Moon at 45/135/225/315 (and 270) at the 09:15 open [V4 @ 29:12–46:00;
    V6 @ 39:26]. 'It should be nearly 45 — 43, 44, 45' at 9:15."""
    o = o or snapshot(d, OPEN_H)
    out = []
    for zod in ("trop", "sid"):
        lon = o[zod]["Moon"]
        for tgt in (45, 135, 225, 315, 270):
            diff = ((lon - tgt + 180) % 360) - 180
            if abs(diff) <= orb:
                out.append({"family": f"moon{tgt}_{zod}",
                            "label": f"Moon at {tgt}° at open ({zod}, {lon:.1f}°)",
                            "note": "universal date: its high/low matter; not a holiday",
                            "instrument": "Nifty", "key": zod})
    return out


def day(d: datetime.date) -> dict:
    """Everything the app shows for one date."""
    star = session_star(d)
    ev = events_between(d)
    trading = nse_holidays.is_trading_day(d)
    if trading:
        ev += moon_angle_date(d)
    star_date = (trading and star["clean"] and d.weekday() != 4
                 and star["lord"] in STAR_INSTRUMENT)
    # Moon in Mesha (and Meena when the Mesha days fall on a weekend) —
    # both days of the sign transit are Nifty dates [V2 @ 32:29–37:30]
    if trading and star["moon_sign"] in MOON_SIGN_DATES:
        ev.append({"family": "moon_sign", "label": f"Moon in {star['moon_sign']}",
                   "note": MOON_SIGN_DATES[star["moon_sign"]],
                   "instrument": "Nifty", "key": star["moon_sign"]})
    return {"date": d.isoformat(), "weekday": d.strftime("%a"),
            "trading": trading, "closed": nse_holidays.closed_reason(d),
            "star": star,
            "star_date": STAR_INSTRUMENT.get(star["lord"]) if star_date else None,
            "events": ev}


def carry_over(prev: dict, cur: dict) -> dict | None:
    """The opposite-nature carry-over [V1 @ 01:25; V5 @ 49:15–01:13:00]:
    usable only when both are consecutive trading days, the lords are of
    opposite nature, the Moon is in the same sign and no other planet
    changed sign. Direction depends on how the first day actually
    closed, which the app cannot know in advance — it reports the setup."""
    if not (prev["trading"] and cur["trading"]):
        return None
    if datetime.date.fromisoformat(cur["date"]) - \
            datetime.date.fromisoformat(prev["date"]) != datetime.timedelta(days=1):
        return None
    ps, cs = prev["star"], cur["star"]
    if ps["nature"] == cs["nature"]:
        return None
    if ps["moon_sign"] != cs["moon_sign"] or ps["signs"] != cs["signs"]:
        return None
    return {"setup": True,
            "text": (f"{ps['lord']} ({ps['nature']}) → {cs['lord']} ({cs['nature']}): "
                     f"if the first day closes against its lord, the second goes "
                     f"the other way (same Moon sign, no planet moved)")}


def week(start: datetime.date, days: int = 14) -> dict:
    """Upcoming dates with the after-close / holiday shift applied."""
    rows = []
    for i in range(days):
        d = start + datetime.timedelta(days=i)
        r = day(d)
        r["shifted_to"] = None if r["trading"] else next_trading_day(d).isoformat()
        r["carry_over"] = None
        rows.append(r)
    for a, b in zip(rows, rows[1:]):
        b["carry_over"] = carry_over(a, b)
    return {"start": start.isoformat(), "days": rows}
