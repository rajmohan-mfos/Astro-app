"""KP-style day-chart helpers (Layer A extension, SPEC Appendix C.3).

Reproduces the author's printed panchang chart (see panchang.png reference):
- Moon transit table: every Vimshottari sub-lord period END during the day,
  with the boundary degree, rasi/nakshatra/sub lords and local clock time.
- Same for the other grahas (only a few cross a boundary on a given day).
- End times for the running thithi / natchathiram / yogam / karanam.

All longitudes sidereal Lahiri, matching engine.py. Boundary degrees are
pure Vimshottari arithmetic; only the crossing *times* need the ephemeris.
"""
import bisect
import datetime

import swisseph as swe

from .engine import FLAGS
from .names import (RASIS, NAKSHATRAS, THITHIS, YOGAS, GRAHA_TA,
                    NAKSHATRAS_TA, WEEKDAYS)
from .panchang import karana_name

SEG = 360 / 27

DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
               "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

RASI_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

WEEKDAY_LORDS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus",
                 "Saturn", "Sun"]                      # Mon..Sun

# 27 nakshatras x 9 subs = 243 segments spanning [0, 360).
# Sub order inside a nakshatra starts with the nakshatra's own lord.
_SUB_STARTS: list[float] = []
_SUBS: list[tuple[float, float, int, str]] = []   # (start, end, nak_idx, sub_lord)
for _n in range(27):
    _pos = _n * SEG
    for _k in range(9):
        _lord = DASHA_LORDS[(_n + _k) % 9]
        _span = SEG * DASHA_YEARS[_lord] / 120
        _SUB_STARTS.append(_pos)
        _SUBS.append((_pos, _pos + _span, _n, _lord))
        _pos += _span


def _segment_at(lon: float) -> tuple[float, float, int, str]:
    return _SUBS[bisect.bisect_right(_SUB_STARTS, lon % 360) - 1]


def _dms(deg: float) -> str:
    total = round(deg * 3600) % (360 * 3600)
    d, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{d:03d}.{m:02d}.{s:02d}"


def _clock(jd: float, jd0: float) -> str:
    """Local clock time as HH:MM:SS; hours run past 24 after midnight."""
    total = round((jd - jd0) * 86400)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _lon_fn(body: int):
    def fn(jd: float) -> float:
        return swe.calc_ut(jd, body, FLAGS)[0][0] % 360
    return fn


def _bisect_cross(f, lo: float, hi: float) -> float:
    for _ in range(40):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _next_cross(value_fn, target: float, jd: float, jd_end: float,
                step: float, decreasing: bool = False):
    """First time in (jd, jd_end] the value passes `target`, or None.

    The value is treated as increasing through the target (decreasing=True
    negates the test for retrograde motion).
    """
    def f(j: float) -> float:
        d = ((value_fn(j) - target + 180) % 360) - 180
        return -d if decreasing else d

    a, fa = jd, f(jd)
    while a < jd_end:
        b = min(a + step, jd_end)
        fb = f(b)
        if fa < 0 <= fb:
            return _bisect_cross(f, a, b)
        a, fa = b, fb
    return None


def _lord_row(boundary: float, sub_lord: str, jd_cross: float, jd0: float) -> dict:
    inside = (boundary - 1e-6) % 360        # the segment that ends here
    rasi_lord = RASI_LORDS[int(inside // 30)]
    nak_lord = DASHA_LORDS[int(inside // SEG) % 9]
    return {
        "deg": _dms(boundary),
        "rasi_lord": rasi_lord, "rasi_lord_ta": GRAHA_TA[rasi_lord],
        "nak_lord": nak_lord, "nak_lord_ta": GRAHA_TA[nak_lord],
        "sub_lord": sub_lord, "sub_lord_ta": GRAHA_TA[sub_lord],
        "time": _clock(jd_cross, jd0),
    }


def _transits(body: int, jd0: float, jd_end: float, step: float) -> list[dict]:
    fn = _lon_fn(body)
    rows = []
    jd = jd0
    while True:
        lon = fn(jd + 1e-6)
        speed = swe.calc_ut(jd + 1e-6, body, FLAGS)[0][3]
        seg = _segment_at(lon)
        if speed >= 0:
            target, decreasing = seg[1] % 360, False
        else:
            target, decreasing = seg[0] % 360, True
        cross = _next_cross(fn, target, jd, jd_end, step, decreasing)
        if cross is None:
            return rows
        rows.append(_lord_row(target if not decreasing else seg[0],
                              seg[3], cross, jd0))
        jd = cross + 30 / 86400


def _panchang_ends(jd_ref: float, jd0: float) -> dict:
    """Name + end time of the thithi/nak/yogam/karanam running at jd_ref."""
    sun, moon = _lon_fn(swe.SUN), _lon_fn(swe.MOON)
    search_end = jd0 + 2.0
    step = 1 / 24

    def elong(j):
        return (moon(j) - sun(j)) % 360

    def ysum(j):
        return (sun(j) + moon(j)) % 360

    out = {}

    e = elong(jd_ref)
    t_idx = int(e // 12)
    cross = _next_cross(elong, ((t_idx + 1) * 12) % 360, jd_ref, search_end, step)
    out["thithi"] = {"num": t_idx + 1, "name": THITHIS[t_idx % 15],
                     "ends": _clock(cross, jd0) if cross else None}

    ml = moon(jd_ref)
    n_idx = int(ml // SEG)
    cross = _next_cross(moon, ((n_idx + 1) * SEG) % 360, jd_ref, search_end, step)
    out["natchathiram"] = {"num": n_idx + 1, "name": NAKSHATRAS[n_idx],
                           "name_ta": NAKSHATRAS_TA[n_idx],
                           "ends": _clock(cross, jd0) if cross else None}

    y = ysum(jd_ref)
    y_idx = int(y // SEG)
    cross = _next_cross(ysum, ((y_idx + 1) * SEG) % 360, jd_ref, search_end, step)
    out["yogam"] = {"num": y_idx + 1, "name": YOGAS[y_idx],
                    "ends": _clock(cross, jd0) if cross else None}

    k = int(e // 6)
    cross = _next_cross(elong, ((k + 1) * 6) % 360, jd_ref, search_end, step)
    out["karanam"] = {"num": k + 1, "name": karana_name(k),
                      "ends": _clock(cross, jd0) if cross else None}
    return out


def sun_nak_window(year: int, month: int, day: int, tz_offset: float) -> dict:
    """The Sun-nakshatra period containing the given local date (KP ayanamsa).

    This is the "weekly" prediction window of the WEEKLY AND MONTHLY class:
    not the calendar month, but the ~13.5 days the Sun spends in one
    nakshatra ("take the month when the stars change").
    """
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    jd_ref = swe.julday(year, month, day, 12 - tz_offset)      # local noon
    sun = _lon_fn(swe.SUN)
    n = int(sun(jd_ref) // SEG)

    jd_start = _next_cross(sun, (n * SEG) % 360, jd_ref - 16, jd_ref, step=0.25)
    jd_end = _next_cross(sun, ((n + 1) * SEG) % 360, jd_ref, jd_ref + 16,
                         step=0.25)

    def local_date(jd: float) -> str:
        y, m, d, _ = swe.revjul(jd + tz_offset / 24)
        return f"{y:04d}-{m:02d}-{d:02d}"

    lord = DASHA_LORDS[n % 9]
    next_lord = DASHA_LORDS[(n + 1) % 9]
    return {
        "nak_num": n + 1,
        "nak": NAKSHATRAS[n],
        "nak_ta": NAKSHATRAS_TA[n],
        "lord": lord,
        "next_lord": next_lord,
        "start": local_date(jd_start) if jd_start else None,
        "mid": local_date((jd_start + jd_end) / 2)
               if jd_start and jd_end else None,
        "end": local_date(jd_end) if jd_end else None,
    }


def moon_rasi_exit(year: int, month: int, day: int, tz_offset: float) -> str:
    """Local datetime when the transit Moon leaves its current rasi.

    KP, matching the /api/can-trade charts this feeds. The two MUST agree:
    `rasi_until` answers "when does the Moon leave THIS rasi", where "this"
    is the `transit_rasi` computed in `can_trade`. Under a different
    ayanamsa the two name different rasis on boundary days and the exit
    time is wrong by up to ~2.5 days. The Moon spends ~2.5 days per rasi,
    so the search window is 3 days from 09:15 local."""
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    jd_ref = swe.julday(year, month, day, 9.25 - tz_offset)
    moon = _lon_fn(swe.MOON)
    target = (int(moon(jd_ref) // 30) + 1) * 30 % 360
    cross = _next_cross(moon, target, jd_ref, jd_ref + 3, step=2 / 24)
    if cross is None:
        return "—"
    y, m, d, h = swe.revjul(cross + tz_offset / 24)
    return f"{y:04d}-{m:02d}-{d:02d} {int(h):02d}:{round((h % 1) * 60):02d}"


HORAI_SEQ = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]


def sunrise_hour(year: int, month: int, day: int, tz_offset: float,
                 lat: float, lon: float) -> float:
    """Local sunrise hour for the civil date (Moshier ephemeris)."""
    jd_prev_evening = swe.julday(year, month, day, -tz_offset - 2)
    res, tret = swe.rise_trans(jd_prev_evening, swe.SUN, swe.CALC_RISE,
                               (lon, lat, 0), 0, 0, swe.FLG_MOSEPH)
    if res != 0:
        raise ValueError("sunrise not found (polar latitude?)")
    jd_local = tret[0] + tz_offset / 24
    _, _, _, hour = swe.revjul(jd_local)
    return hour


def horai_timeline(year: int, month: int, day: int, tz_offset: float,
                   lat: float, lon: float) -> list[dict]:
    """24 PROPORTIONAL horai: daylight (sunrise→sunset) split into 12, and
    night (sunset→next sunrise) into 12, lords in Chaldean sequence from
    the weekday lord. Confirmed by the Example Chart video: the teacher's
    Friday Saturn horai runs 09:24–10:29 (~65 min) on 07/01/2022 —
    proportional gives 09:29–10:26 there, equal hours 09:37–10:37."""
    geopos = (lon, lat, 0)
    jd0 = swe.julday(year, month, day, -tz_offset - 2)
    _, tret = swe.rise_trans(jd0, swe.SUN, swe.CALC_RISE, geopos, 0, 0,
                             swe.FLG_MOSEPH)
    jd_rise = tret[0]
    _, tret = swe.rise_trans(jd_rise, swe.SUN, swe.CALC_SET, geopos, 0, 0,
                             swe.FLG_MOSEPH)
    jd_set = tret[0]
    _, tret = swe.rise_trans(jd_set, swe.SUN, swe.CALC_RISE, geopos, 0, 0,
                             swe.FLG_MOSEPH)
    jd_rise2 = tret[0]

    jd_midnight = swe.julday(year, month, day, -tz_offset)

    def loc(jd: float) -> float:
        return (jd - jd_midnight) * 24

    rise, sett, rise2 = loc(jd_rise), loc(jd_set), loc(jd_rise2)
    day_lord = WEEKDAY_LORDS[datetime.date(year, month, day).weekday()]
    start_idx = HORAI_SEQ.index(day_lord)
    slots = []
    for i in range(24):
        if i < 12:
            s = rise + (sett - rise) * i / 12
            e = rise + (sett - rise) * (i + 1) / 12
        else:
            s = sett + (rise2 - sett) * (i - 12) / 12
            e = sett + (rise2 - sett) * (i - 11) / 12
        lord = HORAI_SEQ[(start_idx + i) % 7]
        slots.append({"lord": lord, "lord_ta": GRAHA_TA[lord],
                      "start": s, "end": e})
    return slots


def lords_of(lon: float) -> dict:
    """Rasi / nakshatra / sub lords of a sidereal longitude (KP tables)."""
    seg = _segment_at(lon)
    return {
        "rasi_lord": RASI_LORDS[int((lon % 360) // 30)],
        "nak_lord": DASHA_LORDS[seg[2] % 9],
        "sub_lord": seg[3],
    }


def prasanam_chain(year: int, month: int, day: int, hour: int, minute: int,
                   tz_offset: float, lat: float, lon: float) -> dict:
    """KP horary chain for a chart cast at the question moment.

    Question planet = the Moon's star lord; answer planet = that planet's
    own star lord. Houses are PLACIDUS cusps — KP is a cusp-based system
    and the teacher's "KP Murai" setting is Placidus, so this now matches
    the planet-position sheet exactly (it previously used whole-sign,
    which could put a planet in a different house from the one displayed).
    All positions use the KP ayanamsa.
    """
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    jd = swe.julday(year, month, day, hour + minute / 60 - tz_offset)
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    if len(cusps) == 13:            # some builds return a leading dummy
        cusps = cusps[1:]
    asc = ascmc[0] % 360

    bodies = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
              "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
              "Venus": swe.VENUS, "Saturn": swe.SATURN}
    lons = {n: swe.calc_ut(jd, b, FLAGS)[0][0] % 360
            for n, b in bodies.items()}
    lons["Rahu"] = swe.calc_ut(jd, swe.MEAN_NODE, FLAGS)[0][0] % 360
    lons["Ketu"] = (lons["Rahu"] + 180) % 360

    def house_of(planet: str) -> int:
        pl = lons[planet]
        for i in range(12):
            c1, c2 = cusps[i] % 360, cusps[(i + 1) % 12] % 360
            if (c1 <= pl < c2) if c1 <= c2 else (pl >= c1 or pl < c2):
                return i + 1
        return 1

    # [LT2] "The moon is the question. You should take the moon… the star
    # in the moon is the question." The question planet is the Moon's
    # nakshatra lord; the answer is that planet's own star lord (user
    # adjudication 2026-08-11, over P1's lagna-sub-lord phrasing — the two
    # transcripts genuinely disagree; see RULES-SOURCES.md).
    question = lords_of(lons["Moon"])["nak_lord"]
    answer = lords_of(lons[question])["nak_lord"]

    # KP significators: a planet signifies the houses it OCCUPIES and
    # OWNS, plus those its STAR LORD occupies and owns [P1: "the star is
    # the question - 4, 9, 10, 11 are there; Rahu is here - 4, 10, 12"].
    # Rahu/Ketu own no rasi, so they act through their sign lord.
    # KP ownership is cusp-based: a planet owns the house whose CUSP falls
    # in a rasi it rules. With Placidus a sign can hold two cusps (or
    # none), which is normal — interception, not a bug.
    def owned_houses(pl: str) -> set:
        return {i + 1 for i, c in enumerate(cusps)
                if RASI_LORDS[int((c % 360) // 30)] == pl}

    def significators(pl: str) -> set:
        out = {house_of(pl)} | owned_houses(pl)
        if pl in ("Rahu", "Ketu"):
            out |= owned_houses(RASI_LORDS[int(lons[pl] // 30)])
        star = lords_of(lons[pl])["nak_lord"]
        if star != pl:
            out |= {house_of(star)} | owned_houses(star)
            if star in ("Rahu", "Ketu"):
                out |= owned_houses(RASI_LORDS[int(lons[star] // 30)])
        return out

    return {
        "question_houses": sorted(significators(question)),
        "answer_houses": sorted(significators(answer)),
        "moon_houses": sorted(significators("Moon")),
        "asc": round(asc, 4),
        "question": question,
        "question_house": house_of(question),
        "answer": answer,
        "answer_house": house_of(answer),
        "moon_house": house_of("Moon"),
        "lagna_sub_lord": lords_of(asc)["sub_lord"],
    }


def planet_position(year: int, month: int, day: int, hour: int, minute: int,
                    tz_offset: float, lat: float, lon_geo: float) -> dict:
    """KP planet-position sheet (author's OPTIONS MERSAL format): full
    sidereal degrees (KP ayanamsa) as DEG:MN:SE, KP Placidus house, and
    sign/star/sub lords per planet, plus the ruling chain ("star lord of
    Moon is X, star lord of X is Y") and the day lord."""
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    jd = swe.julday(year, month, day, hour + minute / 60 - tz_offset)
    cusps, ascmc = swe.houses_ex(jd, lat, lon_geo, b'P', swe.FLG_SIDEREAL)
    if len(cusps) == 13:            # some builds return a leading dummy
        cusps = cusps[1:]
    asc = ascmc[0] % 360

    def house_of(pl: float) -> int:
        for i in range(12):
            c1, c2 = cusps[i] % 360, cusps[(i + 1) % 12] % 360
            if (c1 <= pl < c2) if c1 <= c2 else (pl >= c1 or pl < c2):
                return i + 1
        return 1

    def dms(pl: float) -> str:
        total = round(pl * 3600) % (360 * 3600)
        d, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        return f"{d:03d}:{m:02d}:{s:02d}"

    def row(name: str, pl: float, retro: bool, house: int) -> dict:
        return {"planet": name, "deg": dms(pl), "house": house,
                "retro": retro, **lords_of(pl)}

    rows = [row("Lag", asc, False, 1)]
    bodies = [("Sun", swe.SUN), ("Moo", swe.MOON), ("Mar", swe.MARS),
              ("Mer", swe.MERCURY), ("Jup", swe.JUPITER),
              ("Ven", swe.VENUS), ("Sat", swe.SATURN)]
    lons = {}
    for name, body in bodies:
        pos = swe.calc_ut(jd, body, FLAGS)[0]
        pl = pos[0] % 360
        lons[name] = pl
        retro = pos[3] < 0 and name not in ("Sun", "Moo")
        rows.append(row(name, pl, retro, house_of(pl)))
    rahu = swe.calc_ut(jd, swe.MEAN_NODE, FLAGS)[0][0] % 360
    ketu = (rahu + 180) % 360
    rows.append(row("Rah", rahu, True, house_of(rahu)))
    rows.append(row("Ket", ketu, True, house_of(ketu)))
    lons["Rah"], lons["Ket"] = rahu, ketu

    full = {"Sun": "Sun", "Moo": "Moon", "Mar": "Mars", "Mer": "Mercury",
            "Jup": "Jupiter", "Ven": "Venus", "Sat": "Saturn",
            "Rah": "Rahu", "Ket": "Ketu"}
    abbrev = {v: k for k, v in full.items()}
    x = DASHA_LORDS[int(lons["Moo"] // SEG) % 9]
    y = DASHA_LORDS[int(lons[abbrev[x]] // SEG) % 9]

    lord = WEEKDAY_LORDS[datetime.date(year, month, day).weekday()]
    return {
        "rows": rows,
        "chain": {"x": x, "y": y},
        "chain_text": [f"Star lord of Moon is {x}",
                       f"Star lord of {x} is {y}"],
        "day_lord": {"en": lord, "ta": GRAHA_TA[lord]},
    }


def ruling_chain(year: int, month: int, day: int, tz_offset: float,
                 lat: float, lon_geo: float) -> dict:
    """The day's ruling chain (star lord of Moon = X; star lord of X's
    position = Y), cast at SUNRISE — the same moment the prediction chain
    uses, so the sheet and the prediction never disagree."""
    rise = sunrise_hour(year, month, day, tz_offset, lat, lon_geo)
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    jd = swe.julday(year, month, day, rise - tz_offset)

    bodies = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
              "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
              "Venus": swe.VENUS, "Saturn": swe.SATURN}
    lons = {n: swe.calc_ut(jd, b, FLAGS)[0][0] % 360
            for n, b in bodies.items()}
    lons["Rahu"] = swe.calc_ut(jd, swe.MEAN_NODE, FLAGS)[0][0] % 360
    lons["Ketu"] = (lons["Rahu"] + 180) % 360

    x = DASHA_LORDS[int(lons["Moon"] // SEG) % 9]
    y = DASHA_LORDS[int(lons[x] // SEG) % 9]
    hh, mm = int(rise), round((rise % 1) * 60)
    if mm == 60:
        hh, mm = hh + 1, 0
    return {
        "x": x, "y": y,
        "chain_text": [f"Star lord of Moon is {x}",
                       f"Star lord of {x} is {y}"],
        "cast": f"{hh:02d}:{mm:02d} (sunrise)",
    }


def jupiter_nak_window(year: int, month: int, day: int,
                       tz_offset: float) -> dict:
    """The Jupiter-nakshatra period containing the date (KP ayanamsa).

    Long-term ("yearly") window of Astro Class 11. Found by daily sampling
    so retrograde ingresses work — the teacher's own July 2021 example is
    Jupiter sliding *backwards* into Dhanishta. The window is the contiguous
    run of days sharing the nakshatra; a later re-entry after an exit counts
    as a new window.
    """
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    jd_ref = swe.julday(year, month, day, 12 - tz_offset)
    fn = _lon_fn(swe.JUPITER)
    n = int(fn(jd_ref) // SEG)

    jd_start = jd_ref
    while jd_start > jd_ref - 450 and int(fn(jd_start - 1) // SEG) == n:
        jd_start -= 1
    jd_end = jd_ref
    while jd_end < jd_ref + 450 and int(fn(jd_end + 1) // SEG) == n:
        jd_end += 1

    def local_date(jd: float) -> str:
        y, m, d, _ = swe.revjul(jd + tz_offset / 24)
        return f"{y:04d}-{m:02d}-{d:02d}"

    return {
        "nak_num": n + 1,
        "nak": NAKSHATRAS[n],
        "nak_ta": NAKSHATRAS_TA[n],
        "lord": DASHA_LORDS[n % 9],
        "start": local_date(jd_start),
        "mid": local_date((jd_start + jd_end) / 2),
        "end": local_date(jd_end),
        "days": round(jd_end - jd_start),
    }


def day_chart(year: int, month: int, day: int, tz_offset: float) -> dict:
    """The KP day-chart extras: day lord, panchang end times, transit tables.

    Uses the KP (Krishnamurti) ayanamsa — this is a KP chart, and the author's
    printed times match KP, not Lahiri (verified against the 05/05/2021 chart;
    Lahiri is ~0.09° behind, which shifts Moon timings by ~10 minutes).
    The window runs from local midnight to +30h so late-night rows show as
    24:xx / 25:xx, matching the author's chart. The panchang block lists the
    elements running at day start with their end times, as the author does.
    """
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    jd0 = swe.julday(year, month, day, -tz_offset)          # local 00:00
    jd_end = jd0 + 30 / 24
    jd_ref = jd0 + 1e-6

    lord = WEEKDAY_LORDS[datetime.date(year, month, day).weekday()]

    moon_rows = _transits(swe.MOON, jd0, jd_end, step=20 / 1440)

    planet_rows = []
    for name, body in [("Sun", swe.SUN), ("Mars", swe.MARS),
                       ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
                       ("Venus", swe.VENUS), ("Saturn", swe.SATURN)]:
        for row in _transits(body, jd0, jd_end, step=2 / 24):
            planet_rows.append({"graha": name, "graha_ta": GRAHA_TA[name], **row})
    planet_rows.sort(key=lambda r: r["time"])

    return {
        "vaara": WEEKDAYS[datetime.date(year, month, day).weekday()],
        "day_lord": {"en": lord, "ta": GRAHA_TA[lord]},
        "panchang_ends": _panchang_ends(jd_ref, jd0),
        "moon_transits": moon_rows,
        "planet_transits": planet_rows,
    }
