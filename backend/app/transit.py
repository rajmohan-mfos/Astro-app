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
from .names import (RASIS, RASIS_TA, NAKSHATRAS, THITHIS, YOGAS, GRAHA_TA,
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


def moon_rasi_exit(year: int, month: int, day: int, tz_offset: float,
                   lat: float, lon: float) -> str:
    """Local datetime when the transit Moon leaves its rasi at SUNRISE.

    Both the ayanamsa (KP) and the anchor moment (sunrise) must match the
    /api/can-trade charts this feeds. `rasi_until` answers "when does the
    Moon leave THIS rasi", where "this" is the `transit_rasi` computed in
    `can_trade` — so if either the zodiac or the cast moment differs, the
    two name different rasis on boundary days and the exit time is wrong
    by up to ~2.5 days.

    Consequence of the sunrise anchor: on days when the Moon changes rasi
    between sunrise and market open, the returned time is EARLIER than
    09:15 — the sunrise rasi has already expired by the time you trade.
    That is faithful to the sunrise reading rather than a bug.

    The Moon spends ~2.5 days per rasi, so the search window is 3 days.
    """
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    rise = sunrise_hour(year, month, day, tz_offset, lat, lon)
    jd_ref = swe.julday(year, month, day, rise - tz_offset)
    moon = _lon_fn(swe.MOON)
    target = (int(moon(jd_ref) // 30) + 1) * 30 % 360
    cross = _next_cross(moon, target, jd_ref, jd_ref + 3, step=2 / 24)
    if cross is None:
        return "—"
    y, m, d, h = swe.revjul(cross + tz_offset / 24)
    # Round to the minute as one quantity: formatting the hour and minute
    # independently produced "05:60" (and would produce "23:60") whenever
    # the seconds rounded up — 3 days in 2024 alone.
    total = round(h * 60)
    if total >= 24 * 60:
        nxt = datetime.date(y, m, d) + datetime.timedelta(days=1)
        y, m, d, total = nxt.year, nxt.month, nxt.day, total - 24 * 60
    return f"{y:04d}-{m:02d}-{d:02d} {total // 60:02d}:{total % 60:02d}"


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


# ---------------------------------------------------------------------------
# KP horary: the 1-249 seed number
#
# The taught method (PRASANAM VIDEO 1 @ 04:31-05:32): in AstroSage, KP Murai
# -> settings -> KP OLD method -> "KP Hora Ennai", think of a number 1..249
# and enter it. The number, not the clock, chooses the ascendant.
#
# The table is the 243 Vimshottari sub-divisions (27 nakshatras x 9 subs)
# with the 6 subs that straddle a rasi cusp split in two, giving 249. That
# yields the canonical KP per-sign counts 22/19/21/21 repeating -
# independently checkable, and the reason the number range is 249 not 243.
# ---------------------------------------------------------------------------
KP_HORARY: list[tuple[float, float, int, str]] = []
for _s, _e, _nak, _lord in _SUBS:
    _p = _s
    while _p < _e - 1e-9:
        _cusp = (int(_p // 30) + 1) * 30
        _q = min(_e, _cusp)
        KP_HORARY.append((_p, _q, _nak, _lord))
        _p = _q
assert len(KP_HORARY) == 249, len(KP_HORARY)


def horary_ascendant(number: int) -> dict:
    """Sidereal ascendant selected by KP horary number 1..249.

    The number designates a SPAN, not a point — every longitude inside it
    shares the same sign, star and sub lords. The ascendant is taken at
    the span's MIDPOINT rather than its start: the start is a knife-edge
    boundary, and solving for it lands fractions of an arcsecond either
    side, which flips the lagna sub lord into the neighbouring division
    (number 45 did exactly that). The midpoint is robust to solver error
    and is at most half a sub (~1 deg) from the start.
    """
    if not 1 <= number <= 249:
        raise ValueError("horary number must be between 1 and 249")
    start, end, nak, sub = KP_HORARY[number - 1]
    return {"number": number, "start": start % 360, "end": end % 360,
            "asc": ((start + end) / 2) % 360,
            "rasi": RASIS[int(start // 30) % 12],
            "nakshatra": NAKSHATRAS[nak],
            "star_lord": DASHA_LORDS[nak % 9], "sub_lord": sub}


def _armc_for_ascendant(target_trop: float, lat: float, eps: float) -> float:
    """ARMC whose Placidus ascendant equals `target_trop` (tropical).

    The ascendant increases monotonically with ARMC, so bisect on the
    wrapped difference.
    """
    def asc_at(armc: float) -> float:
        return swe.houses_armc(armc % 360, lat, eps, b'P')[1][0] % 360

    def diff(armc: float) -> float:
        return ((asc_at(armc) - target_trop + 180) % 360) - 180

    lo = 0.0
    for step in range(360):
        a, b = float(step), float(step + 1)
        if diff(a) <= 0 < diff(b):
            lo = a
            break
    hi = lo + 1
    for _ in range(60):
        mid = (lo + hi) / 2
        if diff(mid) <= 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def horary_chart(number: int, year: int, month: int, day: int, hour: int,
                 minute: int, tz_offset: float, lat: float,
                 lon: float) -> dict:
    """KP horary chart for a seed number — the taught prasanam method.

    The number fixes the ASCENDANT (via the 249-fold sub division); the
    remaining 11 cusps follow by Placidus for that ascendant at this
    latitude; the planets are placed for the actual moment of judgment.
    Question planet = the LAGNA's sub lord [P1: "Lakkana Upanachathram is
    the question"] — which is exactly what the number selects, so the
    number-based method and P1's phrasing agree. Answer = that planet's
    own star lord.

    UNVALIDATED against the teacher's worked example: PRASANAM VIDEO 1
    quotes number 88 with significators {4,9,10,11}/{4,10,12} but gives no
    DATE, so the planets cannot be reproduced, and its machine translation
    is too corrupted to trust the planet names. The 249 table itself IS
    validated (canonical per-sign counts; #1 = Ketu 0deg00'-0deg46'40").
    Compare against AstroSage before relying on the cusp derivation.
    """
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI, 0, 0)
    jd = swe.julday(year, month, day, hour + minute / 60 - tz_offset)
    seed = horary_ascendant(number)

    # the table is SIDEREAL; houses_armc works tropically, so add the
    # ayanamsa going in and take it off coming out — never both ways
    ayan = swe.get_ayanamsa_ut(jd)
    eps = swe.calc_ut(jd, swe.ECL_NUT)[0][0]
    armc = _armc_for_ascendant((seed["asc"] + ayan) % 360, lat, eps)
    cusps_trop, ascmc_trop = swe.houses_armc(armc, lat, eps, b'P')
    cusps = [(c - ayan) % 360 for c in cusps_trop]
    asc = (ascmc_trop[0] - ayan) % 360

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

    question = seed["sub_lord"]
    answer = lords_of(lons[question])["nak_lord"]
    return {
        "seed": seed,
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


# Abbreviations and order as they appear in the author's chart image
# ("I need the panchang chart in this manner.png", OPTIONS MERSAL format).
CHART_BODIES = [
    ("Lagna", "Lag", None), ("Sun", "Sun", swe.SUN),
    ("Moon", "Moo", swe.MOON), ("Mars", "Mar", swe.MARS),
    ("Mercury", "Mer", swe.MERCURY), ("Jupiter", "Jup", swe.JUPITER),
    ("Venus", "Ven", swe.VENUS), ("Saturn", "Sat", swe.SATURN),
    ("Rahu", "Rah", swe.MEAN_NODE), ("Ketu", "Ket", None),
    ("Uranus", "Uran", swe.URANUS), ("Neptune", "Nept", swe.NEPTUNE),
    ("Pluto", "Plut", swe.PLUTO),
]


def chart_cells(year: int, month: int, day: int, hour: int, minute: int,
                tz_offset: float, lat: float, lon_geo: float,
                ayanamsa_mode: int = swe.SIDM_LAHIRI) -> list[dict]:
    """The author's panchang chart: 12 rasi cells, each listing the bodies
    in it with degree, star lord and sub lord.

    Reproduces the reference image's content — including the LAGNA and the
    three outer planets (Uranus, Neptune, Pluto), which the nine-graha
    jothidam chart does not carry. Degrees are DD.MM as the author prints
    them (26.36 = 26 deg 36 min), not decimal. The star and sub lord per
    body are the ring OUTSIDE the grid, star lord nearest the cell.

    AYANAMSA IS LAHIRI, established from the reference chart itself rather
    than assumed. Solving the implied ayanamsa from its printed degrees
    (06-01-2022) gives 24.1599 deg from the slow bodies, ~1 arcmin scatter:
    Lahiri is 24.1646 (0.3 arcmin away), KP is 24.0678 (5.5 arcmin away).
    Casting on Lahiri reproduces all 12 bodies to within 0.5 arcmin and
    12 of 13 star/sub lord pairs; KP misses every degree by 5-6 arcmin.

    This conflicts with the transit TIMING tables, which reproduce on KP
    and are ~10 min out on Lahiri (see RULES-SOURCES.md). Both are
    measured; they are different artifacts and may come from different
    tools. The chart follows the chart evidence.

    The reference's Lagna is the one body that does not fit — it sits
    ~10 deg from the ascendant at the moment its planets imply, so that
    chart was cast for a different place or the lagna was entered by
    hand. Planets are location-independent, so this does not affect the
    ayanamsa finding.
    """
    swe.set_sid_mode(ayanamsa_mode, 0, 0)
    jd = swe.julday(year, month, day, hour + minute / 60 - tz_offset)
    asc = swe.houses_ex(jd, lat, lon_geo, b'P', swe.FLG_SIDEREAL)[1][0] % 360

    cells: list[list[tuple[float, dict]]] = [[] for _ in range(12)]
    for name, short, body in CHART_BODIES:
        if name == "Lagna":
            lon, retro = asc, False
        elif name == "Ketu":
            rahu = swe.calc_ut(jd, swe.MEAN_NODE, FLAGS)[0][0] % 360
            lon, retro = (rahu + 180) % 360, False
        else:
            v = swe.calc_ut(jd, body, FLAGS)[0]
            lon, retro = v[0] % 360, v[3] < 0
            if name == "Rahu":
                retro = False           # nodes are always retrograde; not marked
        L = lords_of(lon)
        d = lon % 30
        cells[int(lon // 30)].append((d, {
            "name": name, "short": short,
            "deg": f"{int(d):02d}.{round((d - int(d)) * 60):02d}",
            "retro": retro,
            "star_lord": L["nak_lord"], "sub_lord": L["sub_lord"],
            "star_short": _SHORT.get(L["nak_lord"], L["nak_lord"]),
            "sub_short": _SHORT.get(L["sub_lord"], L["sub_lord"]),
        }))
    # within a cell the author lists bodies by DESCENDING degree
    # (reference chart, Makara: 18.41, 18.18, 10.44, 01.56)
    return [{"sign": i, "rasi": RASIS[i], "rasi_ta": RASIS_TA[i],
             "items": [it for _d, it in sorted(cells[i], key=lambda t: -t[0])]}
            for i in range(12)]


_SHORT = {"Sun": "Sun", "Moon": "Moo", "Mars": "Mar", "Mercury": "Mer",
          "Jupiter": "Jup", "Venus": "Ven", "Saturn": "Sat",
          "Rahu": "Rah", "Ketu": "Ket"}


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
