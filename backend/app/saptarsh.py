"""Week-ahead Nifty / Gold / Silver outlook in the Saptarsh Insight style.

Reproduces, day by day, the components of Saptarsh's daily bulletins —
the Telegram "Saptarsh Insight" posts (Nifty) and the "Gold & Silver
Premium Report" images on X (@sonisunil59, Sunil J. Soni, Gujarat):

  * Moon sign + nakshatra during the session, with change times
  * panchang end-times; Vishti karana, Vaidhriti / Vyatipata yoga
  * Vaar-Tithi yoga (weekday x tithi, classical tables)
  * Rahu Kaal, Yamaganda, Gulika Kaal, Abhijit from sunrise-sunset
  * exact-time aspects at 0/45/60/90/120/135/150/180 between Sun, Moon,
    Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu
  * lunar / solar eclipse on the date
  * a Nifty, Gold and Silver call built from those, NSE session windows
    for Nifty and 03:30-27:30 IST (Globex) windows with ET for metals
  * a slow-moving "regime" block: Jupiter's sidereal sign, Sun+Ketu,
    and the conjunction calendar (planets sharing a sign, entry/exit)

Every label carries a `source`: "observed" means the channel wrote that
exact call in its Jul-Aug 2026 posts; "extrapolated" means it comes
from the simple rule below (nakshatra lord / aspect family) and has NOT
been seen in their output. Nothing here is backtested.

Sidereal Lahiri like engine.py (the channel's tables imply it). Aspect
separations are ayanamsa-free.
"""
import datetime

import swisseph as swe

from . import nse_holidays
from .engine import FLAGS
from .names import NAKSHATRAS, RASIS, THITHIS
from .transit import DASHA_LORDS, SEG, _next_cross, _panchang_ends

TZ = 5.5
IST = datetime.timezone(datetime.timedelta(hours=TZ))
OPEN_H, CLOSE_H = 9.25, 15.5           # NSE 09:15 - 15:30
METAL_OPEN_H, METAL_CLOSE_H = 3.5, 27.5  # the report's Globex day, IST

BODIES = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
          ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
          ("Saturn", swe.SATURN), ("Uranus", swe.URANUS),
          ("Neptune", swe.NEPTUNE), ("Pluto", swe.PLUTO),
          ("Rahu", swe.MEAN_NODE)]          # the channel's "Mn Node"
ANGLES = [0, 45, 60, 90, 120, 135, 150, 180]
ASPECT_NAMES = {0: "conjunction", 45: "semi-square", 60: "sextile",
                90: "square", 120: "trine", 135: "sesquiquadrate",
                150: "quincunx", 180: "opposition"}
SIGN_EN = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
           "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# 1-based segment (of 8 between sunrise and sunset) per weekday Mon..Sun.
RAHU_SEG = [2, 7, 5, 6, 4, 3, 8]
YAMA_SEG = [4, 3, 2, 1, 7, 6, 5]
GULIKA_SEG = [6, 5, 4, 3, 2, 1, 7]

# ---------------------------------------------------------- rule tables
# (a, b, angle) -> tone, exactly as the channel labelled them. Pairs are
# stored in BODIES order (Sun before Moon before Mercury ...).
OBSERVED_ASPECTS: dict[tuple[str, str, int], str] = {
    ("Sun", "Moon", 135): "bull",
    ("Sun", "Mercury", 0): "bull",
    ("Sun", "Neptune", 150): "bull",
    ("Sun", "Pluto", 150): "bear",
    ("Moon", "Mercury", 135): "bull",
    ("Moon", "Mercury", 180): "neutral",
    ("Moon", "Venus", 90): "bear",
    ("Moon", "Venus", 120): "bull",
    ("Moon", "Mars", 135): "bull",
    ("Moon", "Mars", 150): "bull",
    ("Moon", "Jupiter", 150): "bull",
    ("Moon", "Jupiter", 180): "bear",
    ("Moon", "Saturn", 45): "bear",
    ("Moon", "Saturn", 60): "bull",
    ("Moon", "Saturn", 90): "bear",
    ("Moon", "Uranus", 90): "bear",
    ("Moon", "Uranus", 120): "bull",
    ("Moon", "Uranus", 135): "vol",
    ("Moon", "Neptune", 45): "bear",
    ("Moon", "Rahu", 0): "bear",
    ("Moon", "Rahu", 45): "bear",
    ("Mercury", "Neptune", 150): "vol",
    ("Mercury", "Pluto", 150): "vol",
    ("Mercury", "Rahu", 180): "vol",
    # X premium reports (metals), Jul-Aug 2026
    ("Sun", "Jupiter", 120): "bull",        # 27 Jul "Sun-Jupiter become bullish"
    ("Moon", "Pluto", 0): "bull",           # 2 Jul
    ("Venus", "Rahu", 150): "vol",          # 29 Jul "will affect silver"
}
BENEFIC = {"Venus", "Jupiter", "Mercury", "Sun", "Moon"}
HEAVY = {"Saturn", "Rahu", "Pluto"}
OUTER = {"Uranus", "Neptune", "Pluto"}


def aspect_tone(a: str, b: str, angle: int) -> tuple[str, str]:
    """(tone, source) for a pair at an angle."""
    if (a, b, angle) in OBSERVED_ASPECTS:
        return OBSERVED_ASPECTS[(a, b, angle)], "observed"
    other = b if a in ("Sun", "Moon") else a
    if angle in (60, 120):
        return "bull", "extrapolated"
    if angle == 0:
        if other in HEAVY:
            return "bear", "extrapolated"
        if other in OUTER or other == "Mars":
            return "vol", "extrapolated"
        return "bull", "extrapolated"
    if angle in (45, 90, 180):
        return ("vol" if {a, b} & {"Mercury"} and other in OUTER
                else "bear"), "extrapolated"
    # 135 / 150
    if other in HEAVY:
        return "bear", "extrapolated"
    if other in OUTER:
        return "vol", "extrapolated"
    return "bull", "extrapolated"


# Moon nakshatra -> (nifty, metals) as the channel called it. None means
# no clean base call was seen for that instrument. Nifty column from the
# Telegram posts (19-28 Aug); metals column from the X premium reports
# (2 Jul - 19 Aug) plus the Telegram Gold/Silver lines.
OBSERVED_NAK: dict[str, tuple[str | None, str | None]] = {
    "Ashwini": (None, "bull"),
    "Bharani": (None, "bear"),
    "Rohini": (None, "bear"),               # 10 Aug "not much favourable"
    "Ardra": (None, "bear"),                # 10 Aug
    "Punarvasu": (None, "bear"),            # 14 Jul
    "Pushya": (None, "bear"),               # 15 Jul
    "Ashlesha": (None, "neutral"),          # 15 Jul
    "Hasta": (None, "bear"),                # 20 Jul
    "Chitra": (None, "bull"),               # 20 Jul
    "Swati": ("bear", "vol"),               # 18 Aug
    "Vishakha": ("bull", "vol"),            # 19 Aug
    "Anuradha": ("neutral", "vol"),         # bearish on 20 Aug, supportive on 21
    "Jyeshtha": ("bull", "vol"),
    "Mula": (None, "bear"),                 # 27 Jul
    "Purva Ashadha": ("bull", "bear"),      # 24 Aug / 28 Jul
    "Uttara Ashadha": (None, "bull"),       # 2 Jul, 28-29 Jul, 25 Aug
    "Shravana": ("neutral", "bear"),        # 26 Aug / 2 Jul, 29 Jul
    "Dhanishta": ("bull", "bull"),
    "Shatabhisha": ("bear", "bear"),
    "Uttara Bhadrapada": (None, "bull"),    # 7 Jul
    "Revati": (None, "bear"),               # 7-8 Jul
}
# Moon SIGN -> metals bias, only where the report printed one next to
# the sign itself (used when the nakshatra is unobserved).
OBSERVED_SIGN_METALS = {"Makara": "bull", "Kumbha": "bear", "Meena": "bear",
                        "Kataka": "bear", "Mithuna": "neutral"}
LORD_TONE = {"Venus": "bull", "Jupiter": "bull", "Mercury": "bull",
             "Mars": "bull", "Moon": "neutral", "Sun": "neutral",
             "Saturn": "bear", "Rahu": "bear", "Ketu": "bear"}
TONE_WORD = {"bull": "bullish", "bear": "bearish", "vol": "volatile",
             "neutral": "neutral"}


def nak_tone(nak: str, sign: str, instrument: str) -> tuple[str, str]:
    idx = NAKSHATRAS.index(nak)
    obs = OBSERVED_NAK.get(nak)
    col = 0 if instrument == "nifty" else 1
    if obs and obs[col]:
        return obs[col], "observed"
    if instrument != "nifty" and sign in OBSERVED_SIGN_METALS:
        return OBSERVED_SIGN_METALS[sign], "observed"
    return LORD_TONE[DASHA_LORDS[idx % 9]], "extrapolated"


# Vaar-Tithi yoga: weekday x tithi (1-15 within the paksha), from the
# classical muhurta tables. The channel prints "Vaar-Tithi yog is
# bullish / bearish" without publishing its table, so these are the
# standard ones, labelled classical. Weekday index Mon=0 .. Sun=6.
NANDA, BHADRA, JAYA, RIKTA, PURNA = {1, 6, 11}, {2, 7, 12}, {3, 8, 13}, {4, 9, 14}, {5, 10, 15}
SIDDHA = {4: NANDA, 2: BHADRA, 1: JAYA, 5: RIKTA, 3: PURNA}
MRITYU = {6: NANDA, 1: NANDA, 0: BHADRA, 4: BHADRA, 2: JAYA, 3: RIKTA, 5: PURNA}
DAGDHA = {6: 12, 0: 11, 1: 5, 2: 3, 3: 6, 4: 8, 5: 9}
VISHA = {6: 4, 0: 6, 1: 7, 2: 2, 3: 8, 4: 9, 5: 7}
HUTASANA = {6: 12, 0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11}


def vaar_tithi_yoga(weekday: int, tithi_num: int) -> dict | None:
    t = (tithi_num - 1) % 15 + 1
    hits = []
    if t in SIDDHA.get(weekday, ()):
        hits.append(("Siddha", "bull"))
    if t in MRITYU.get(weekday, ()):
        hits.append(("Mrityu", "bear"))
    if DAGDHA.get(weekday) == t:
        hits.append(("Dagdha", "bear"))
    if VISHA.get(weekday) == t:
        hits.append(("Visha", "bear"))
    if HUTASANA.get(weekday) == t:
        hits.append(("Hutasana", "bear"))
    if not hits:
        return None
    return {"names": [h[0] for h in hits],
            "tone": "bear" if any(h[1] == "bear" for h in hits) else "bull",
            "source": "classical"}


# ---------------------------------------------------------- ephemeris

def _jd_local(d: datetime.date, hour: float) -> float:
    return swe.julday(d.year, d.month, d.day, hour - TZ)


def _hhmm(jd: float, jd0: float) -> str:
    """Clock time on the civil day of jd0; '+1' suffix past midnight."""
    total = round((jd - jd0) * 1440)
    day, rem = divmod(total, 1440)
    h, m = divmod(rem, 60)
    return f"{h:02d}:{m:02d}" + (f" (+{day})" if day else "")


def _hhmm24(jd: float, jd0: float) -> str:
    """The report's Vedic-day clock: hours run past 24 (27:30)."""
    total = round((jd - jd0) * 1440)
    return f"{total // 60:02d}:{total % 60:02d}"


def _us_dst(dt_utc: datetime.datetime) -> bool:
    """US daylight time: 2nd Sunday of March 07:00 UTC .. 1st Sunday of
    November 06:00 UTC (the 02:00 local switch expressed in UTC)."""
    y = dt_utc.year
    mar = datetime.datetime(y, 3, 1, 7, tzinfo=datetime.timezone.utc)
    mar += datetime.timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = datetime.datetime(y, 11, 1, 6, tzinfo=datetime.timezone.utc)
    nov += datetime.timedelta(days=(6 - nov.weekday()) % 7)
    return mar <= dt_utc < nov


def _et(jd: float) -> str:
    """Clock time in US Eastern (the report prints IST / ET side by side)."""
    y, m, d, h = swe.revjul(jd)
    # round to the minute as one quantity — 13:04:59.98 must print 13:05
    utc = datetime.datetime(y, m, d, tzinfo=datetime.timezone.utc) \
        + datetime.timedelta(minutes=round(h * 60))
    off = -4 if _us_dst(utc) else -5
    loc = utc + datetime.timedelta(hours=off)
    return f"{loc.hour:02d}:{loc.minute:02d}"


def _lon(body: int, jd: float) -> float:
    return swe.calc_ut(jd, body, FLAGS)[0][0] % 360


def _wrap(x: float) -> float:
    return -((-x + 180) % 360 - 180)


def _rise_set(d: datetime.date, lat: float, lon: float) -> tuple[float, float]:
    jd_mid = _jd_local(d, 0)
    geo = (lon, lat, 0)
    r = swe.rise_trans(jd_mid, swe.SUN, swe.CALC_RISE, geo, 0, 0, swe.FLG_MOSEPH)
    s = swe.rise_trans(jd_mid, swe.SUN, swe.CALC_SET, geo, 0, 0, swe.FLG_MOSEPH)
    if r[0] != 0 or s[0] != 0:
        raise ValueError("sunrise/sunset not found")
    return r[1][0], s[1][0]


def kaal_windows(d: datetime.date, lat: float, lon: float) -> dict:
    jd0 = _jd_local(d, 0)
    rise, sset = _rise_set(d, lat, lon)
    seg = (sset - rise) / 8
    w = d.weekday()

    def win(n: int) -> list[str]:
        return [_hhmm(rise + (n - 1) * seg, jd0), _hhmm(rise + n * seg, jd0)]

    muh = (sset - rise) / 15
    return {
        "sunrise": _hhmm(rise, jd0), "sunset": _hhmm(sset, jd0),
        "rahu_kaal": win(RAHU_SEG[w]), "yamaganda": win(YAMA_SEG[w]),
        "gulika_kaal": win(GULIKA_SEG[w]),
        "abhijit": [_hhmm(rise + 7 * muh, jd0), _hhmm(rise + 8 * muh, jd0)],
        "_rahu_jd": (rise + (RAHU_SEG[w] - 1) * seg, rise + RAHU_SEG[w] * seg),
    }


def moon_path(d: datetime.date) -> dict:
    """Sign / nakshatra at the open and any change before the close."""
    jd0 = _jd_local(d, 0)
    jd_open, jd_close = _jd_local(d, OPEN_H), _jd_local(d, CLOSE_H)
    moon = lambda j: _lon(swe.MOON, j)         # noqa: E731
    lon_open = moon(jd_open)
    sign_i, nak_i = int(lon_open // 30), int(lon_open // SEG)
    out = {"sign": RASIS[sign_i], "sign_en": SIGN_EN[sign_i],
           "nakshatra": NAKSHATRAS[nak_i],
           "pada": int((lon_open % SEG) // (SEG / 4)) + 1,
           "sign_change": None, "nakshatra_change": None, "_events": []}
    c = _next_cross(moon, ((sign_i + 1) * 30) % 360, jd_open, jd_close, 1 / 24)
    if c is not None:
        out["sign_change"] = {"time": _hhmm(c, jd0),
                              "to": RASIS[(sign_i + 1) % 12]}
        out["_events"].append((c, f"Moon enters {RASIS[(sign_i + 1) % 12]}"))
    c = _next_cross(moon, ((nak_i + 1) * SEG) % 360, jd_open, jd_close, 1 / 24)
    if c is not None:
        out["nakshatra_change"] = {"time": _hhmm(c, jd0),
                                   "to": NAKSHATRAS[(nak_i + 1) % 27]}
        out["_events"].append((c, f"Moon enters {NAKSHATRAS[(nak_i + 1) % 27]}"))
    return out


def day_aspects(d: datetime.date) -> list[dict]:
    """Exact aspects between 00:00 and 24:00 IST on d, with clock times."""
    jd0, jd1 = _jd_local(d, 0), _jd_local(d, 24)
    step = 1 / 48
    n = int(round((jd1 - jd0) / step))
    grid = [jd0 + i * step for i in range(n + 1)]
    pos = {name: [_lon(b, j) for j in grid] for name, b in BODIES}
    found = []
    for i, (a, ba) in enumerate(BODIES):
        for b, bb in BODIES[i + 1:]:
            diffs = [_wrap(x - y) for x, y in zip(pos[a], pos[b])]
            for ang in ANGLES:
                for t in {_wrap(ang), _wrap(-ang)}:
                    g = [_wrap(x - t) for x in diffs]
                    for k in range(1, len(g)):
                        if g[k - 1] * g[k] <= 0 and g[k - 1] != g[k] \
                                and abs(g[k] - g[k - 1]) < 180:
                            def f(j, t=t):
                                return _wrap(_lon(ba, j) - _lon(bb, j) - t)
                            lo, hi = grid[k - 1], grid[k]
                            flo = f(lo)
                            for _ in range(30):
                                mid = (lo + hi) / 2
                                if (f(mid) < 0) == (flo < 0):
                                    lo, flo = mid, f(mid)
                                else:
                                    hi = mid
                            jd = (lo + hi) / 2
                            tone, src = aspect_tone(a, b, ang)
                            found.append({
                                "_jd": jd, "time": _hhmm(jd, jd0),
                                "et": _et(jd),
                                "a": a, "angle": ang, "b": b,
                                "name": ASPECT_NAMES[ang],
                                "tone": tone, "source": src,
                                "in_session": OPEN_H <= (jd - jd0) * 24 <= CLOSE_H,
                            })
    found.sort(key=lambda x: x["_jd"])
    # a 0°/180° hit can register on both signed targets — keep one
    dedup, last = [], None
    for x in found:
        key = (x["a"], x["b"], x["angle"], round(x["_jd"] * 24))
        if key != last:
            dedup.append(x)
        last = key
    return dedup


def eclipse_on(d: datetime.date) -> str | None:
    jd0, jd1 = _jd_local(d, 0), _jd_local(d, 24)
    try:
        r = swe.lun_eclipse_when(jd0 - 1, swe.FLG_MOSEPH, 0)
        if jd0 <= r[1][0] < jd1:
            return f"lunar eclipse {_hhmm(r[1][0], jd0)}"
        r = swe.sol_eclipse_when_glob(jd0 - 1, swe.FLG_MOSEPH, 0)
        if jd0 <= r[1][0] < jd1:
            return f"solar eclipse {_hhmm(r[1][0], jd0)}"
    except swe.Error:
        return None
    return None


# ---------------------------------------------------------- regime

def _sign_span(body: int, jd: float, ketu: bool = False) -> tuple[str, str]:
    """(entry date, exit date) of the sign the body occupies at jd, by a
    daily scan up to 400 days either way (retrograde re-entries count as
    the nearest boundary, which is what a calendar reader wants)."""
    def sign_at(j):
        lon = _lon(body, j)
        if ketu:
            lon = (lon + 180) % 360
        return int(lon // 30)

    s0 = sign_at(jd)
    back, back_clipped = jd, True
    for _ in range(400):
        if sign_at(back - 1) != s0:
            back_clipped = False
            break
        back -= 1
    fwd, fwd_clipped = jd, True
    for _ in range(400):
        if sign_at(fwd + 1) != s0:
            fwd_clipped = False
            break
        fwd += 1

    def iso(j, clipped, mark):
        y, m, d, _ = swe.revjul(j + TZ / 24)
        # a slow body (Ketu, Neptune) can sit in a sign longer than the
        # scan; say so instead of printing the scan edge as a date
        return (mark if clipped else "") + f"{y:04d}-{m:02d}-{d:02d}"
    return iso(back, back_clipped, "before "), iso(fwd, fwd_clipped, "after ")


JUPITER_CANCER_HISTORY = [
    ("07 Aug 1978", "29 Aug 1979", 387, 55.2, 69.45),
    ("20 Jul 1990", "14 Aug 1991", 390, 0.3, -19.18),
    ("05 Jul 2002", "30 Jul 2003", 390, 14.85, 3.66),
    ("19 Jun 2014", "14 Jul 2015", 390, -9.52, -2.0),
    ("20 Oct 2025", "05 Dec 2025", 46, -1.17, 13.2),
]


def regime(d: datetime.date) -> dict:
    """Slow-moving context the X account posts as calendars."""
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd = _jd_local(d, OPEN_H)
    bodies = [(n, b) for n, b in BODIES if n != "Moon"]
    pos = {n: _lon(b, jd) for n, b in bodies}
    pos["Ketu"] = (pos["Rahu"] + 180) % 360
    ids = dict(bodies)
    signs = {n: int(l // 30) for n, l in pos.items()}

    groups: dict[int, list[str]] = {}
    for n, s in signs.items():
        groups.setdefault(s, []).append(n)
    conj = []
    for s, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        rows = []
        for n in members:
            body = ids["Rahu"] if n == "Ketu" else ids[n]
            entry, exit_ = _sign_span(body, jd, ketu=(n == "Ketu"))
            rows.append({"planet": n, "entry": entry, "exit": exit_})
        conj.append({"sign": RASIS[s], "sign_en": SIGN_EN[s],
                     "planets": [r["planet"] for r in rows], "members": rows,
                     "until": min(r["exit"] for r in rows)})

    jup_sign = signs["Jupiter"]
    jup_entry, jup_exit = _sign_span(swe.JUPITER, jd)
    notes = []
    if SIGN_EN[jup_sign] == "Cancer":
        notes.append("Jupiter in sidereal Cancer — the X account's table of "
                     "every Cancer transit since 1978 shows silver weak in 3 "
                     "of 5 (their claim: 'not a supportive phase for "
                     "sustained bullish trends in Silver').")
    if signs["Sun"] == signs["Ketu"]:
        notes.append(f"Sun + Ketu together in {SIGN_EN[signs['Sun']]} — the "
                     "analog they flagged for the Aug 2025 metals rally "
                     "('almost same chart').")
    return {
        "as_of": d.isoformat(),
        "jupiter": {"sign": RASIS[jup_sign], "sign_en": SIGN_EN[jup_sign],
                    "entry": jup_entry, "exit": jup_exit,
                    "nakshatra": NAKSHATRAS[int(pos["Jupiter"] // SEG)]},
        "sun_ketu_same_sign": signs["Sun"] == signs["Ketu"],
        "conjunctions": conj,
        "notes": notes,
        "jupiter_cancer_history": [
            {"entry": a, "exit": b, "days": n, "gold_pct": g, "silver_pct": s}
            for a, b, n, g, s in JUPITER_CANCER_HISTORY],
    }


# ---------------------------------------------------------- one day

def _karanas_in_session(jd0: float) -> list[dict]:
    """Karana running at the open, and the next if it ends before close."""
    sun = lambda j: _lon(swe.SUN, j)          # noqa: E731
    moon = lambda j: _lon(swe.MOON, j)        # noqa: E731

    def elong(j):
        return (moon(j) - sun(j)) % 360

    from .panchang import karana_name
    out, jd = [], jd0 + OPEN_H / 24
    close = jd0 + CLOSE_H / 24
    for _ in range(3):
        k = int(elong(jd) // 6)
        c = _next_cross(elong, ((k + 1) * 6) % 360, jd, jd0 + 2, 1 / 24)
        out.append({"name": karana_name(k), "ends": _hhmm(c, jd0) if c else None,
                    "_end": c})
        if c is None or c > close:
            break
        jd = c + 1 / 1440
    return out


def _call(instrument: str, moon: dict, flags: list[str], karanas: list[dict],
          yoga: str, vt: dict | None, tithi_num: int) -> dict:
    nak = moon["nakshatra"]
    tone, src = nak_tone(nak, moon["sign"], instrument)
    why = [f"Moon in {moon['sign']} / {nak} — {TONE_WORD[tone]} ({src})"]
    if moon["sign"] == "Vrischika":
        tone = "bear"
        why.append("Moon debilitated in Scorpio — bearish (their 20 Aug reading)")
    elif moon["sign"] == "Vrishabha" and tone != "bear":
        tone = "bull"
        why.append("Moon exalted in Taurus")
    if instrument != "nifty" and tithi_num == 30:
        if tone != "bull":
            tone = "bull" if tone == "neutral" else "vol"
        why.append("Amavasya — \"considered bullish for gold and silver\" (14 Jul)")
    if any(k["name"] == "Vishti" for k in karanas):
        if tone == "bull":
            tone = "vol"
        elif tone == "neutral":
            tone = "bear"
        why.append("Vishti karana in session — \"be very careful following "
                   "a bullish trend\"")
    if yoga == "Vaidhriti":
        tone = "vol"
        why.append("Vaidhriti yog — \"volatility with bullish bias\" (27 Jul, 2 Jul)")
    elif yoga == "Vyatipata":
        tone = "vol" if tone != "bear" else "bear"
        why.append("Vyatipata yoga — inauspicious, treat as volatile")
    if vt:
        why.append(f"Vaar-Tithi yog {'/'.join(vt['names'])} — "
                   f"{TONE_WORD[vt['tone']]} (classical table; the channel's "
                   "own mapping is unpublished)")
    return {"tone": tone, "source": src, "why": why, "caution": list(flags)}


def _prose(inst: str, call: dict, moon: dict, aspects: list[dict],
           kaal: dict) -> str:
    name = {"nifty": "Nifty", "gold": "gold", "silver": "silver"}[inst]
    s = [f"The Moon is in {moon['sign']}"]
    if moon["sign_change"]:
        s[0] += (f" till {moon['sign_change']['time']} IST then enters "
                 f"{moon['sign_change']['to']}")
    s[0] += f" and stays in {moon['nakshatra']} nakshatra"
    if moon["nakshatra_change"]:
        s[0] += (f" till {moon['nakshatra_change']['time']} IST then "
                 f"{moon['nakshatra_change']['to']}")
    s[0] += f". This is {TONE_WORD[call['tone']]} for {name}."
    live = [a for a in aspects if a["in_session"] and "Moon" in (a["a"], a["b"])]
    if live:
        s.append("Intraday: " + "; ".join(
            f"{a['a']} {a['angle']} {a['b']} at {a['time']} ({TONE_WORD[a['tone']]})"
            for a in live[:4]) + ".")
    s.append(f"Rahu Kaal {kaal['rahu_kaal'][0]}–{kaal['rahu_kaal'][1]}.")
    if call["caution"]:
        s.append(" ".join(call["caution"]) + " Be careful.")
    return " ".join(s)


def _tile(events: list, start: float, end: float, tone: str, driver: str,
          jd0: float, clock=_hhmm, with_et: bool = False) -> list[dict]:
    """Split [start, end] at each event; the lean carries forward."""
    windows = []
    for jd, label, t in sorted(e for e in events if start < e[0] < end):
        if jd - start > 20 / 1440:           # swallow sub-20-minute slivers
            w = {"start": clock(start, jd0), "end": clock(jd, jd0),
                 "tone": tone, "driver": driver}
            if with_et:
                w["start_et"], w["end_et"] = _et(start), _et(jd)
            windows.append(w)
            start = jd
        driver = label
        if t:
            tone = t
    w = {"start": clock(start, jd0), "end": clock(end, jd0),
         "tone": tone, "driver": driver}
    if with_et:
        w["start_et"], w["end_et"] = _et(start), _et(end)
    windows.append(w)
    # merge neighbours that share a tone — the report prints 3-4 windows
    merged: list[dict] = []
    for w in windows:
        if merged and merged[-1]["tone"] == w["tone"]:
            merged[-1]["end"] = w["end"]
            if with_et:
                merged[-1]["end_et"] = w["end_et"]
        else:
            merged.append(w)
    return merged


def day(d: datetime.date, lat: float = 19.076, lon: float = 72.8777) -> dict:
    # swisseph's process-wide default sidereal mode is Fagan-Bradley
    # (+0.88° on Lahiri in 2026 — enough to move a Moon sign change by
    # ~1h40). The channel's tables imply Lahiri (24.23° on 27 Aug 2026).
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    jd0 = _jd_local(d, 0)
    closed = nse_holidays.closed_reason(d)
    moon = moon_path(d)
    pe = _panchang_ends(_jd_local(d, OPEN_H), jd0)
    karanas = _karanas_in_session(jd0)
    kaal = kaal_windows(d, lat, lon)
    aspects = day_aspects(d)
    # the metals day runs to 03:30 next morning — pull tomorrow's early hours
    nxt = day_aspects(d + datetime.timedelta(days=1))
    for a in nxt:
        a["time"] = _hhmm(a["_jd"], jd0)
        a["in_session"] = False
    ecl = eclipse_on(d)
    tithi = pe["thithi"]
    vt = vaar_tithi_yoga(d.weekday(), tithi["num"])
    # a tithi lasts 20-26 h, so one that begins after the open and ends
    # before tomorrow's open would never be sampled at 09:15 — look at
    # the close as well. Purnima / Amavasya must not slip through.
    elong_close = (_lon(swe.MOON, _jd_local(d, CLOSE_H))
                   - _lon(swe.SUN, _jd_local(d, CLOSE_H))) % 360
    tithis_in_session = sorted({tithi["num"], int(elong_close // 12) + 1})

    flags: list[str] = []
    if 15 in tithis_in_session:
        flags.append("Purnima — Full Moon: a potential turning point; "
                     "\"Full Moon can be trigger and form bottom\" (29 Jul).")
    elif 30 in tithis_in_session:
        flags.append("Amavasya — New Moon: turning-point watch; bullish for "
                     "metals in their reading (14 Jul).")
    if ecl:
        flags.append(f"{ecl[0].upper() + ecl[1:]} today — many astro events on "
                     "the same day, confidence is low.")
    for a in aspects:
        if a["a"] == "Mercury" and a["b"] == "Rahu" and a["angle"] == 180:
            flags.append("Mercury 180 Rahu — unclear trend, traders may get confused.")
        if a["a"] == "Mars" and a["b"] == "Rahu":
            flags.append(f"Mars {a['angle']} Rahu — \"neutral, confusing price "
                         "action\" (18 Aug).")
        if a["a"] == "Venus" and a["b"] == "Rahu":
            flags.append(f"Venus {a['angle']} Rahu — \"will affect silver "
                         "significantly\" (29 Jul).")
        if a["a"] == "Sun" and a["b"] == "Jupiter":
            flags.append(f"Sun {a['angle']} Jupiter — they read Sun–Jupiter "
                         "contacts on metals both ways (bullish 27 Jul, "
                         "bearish 10 Aug / 15 Jul); watch, don't assume.")

    calls = {inst: _call(inst, moon, flags, karanas, pe["yogam"]["name"], vt,
                         30 if 30 in tithis_in_session else tithi["num"])
             for inst in ("nifty", "gold", "silver")}
    if moon["sign"] == "Kumbha" and ecl:
        calls["silver"]["why"].append(
            "Eclipse in Aquarius / Shatabhisha — the channel flags this as "
            "relevant to white metals")

    # Nifty session windows: split at in-session events, lean carries
    events = [(e[0], e[1], None) for e in moon["_events"]]
    events += [(a["_jd"], f"{a['a']} {a['angle']} {a['b']}", a["tone"])
               for a in aspects if a["in_session"]]
    r0, r1 = kaal["_rahu_jd"]
    events += [(r0, "Rahu Kaal begins", "bear"),
               (r1, "Rahu Kaal ends", calls["nifty"]["tone"])]
    for k in karanas:
        if k["_end"] and jd0 + OPEN_H / 24 < k["_end"] < jd0 + CLOSE_H / 24:
            events.append((k["_end"], f"{k['name']} karana ends",
                           calls["nifty"]["tone"]))
    windows = _tile(events, jd0 + OPEN_H / 24, jd0 + CLOSE_H / 24,
                    calls["nifty"]["tone"], "Moon nakshatra", jd0)

    # Metals windows: the report's 03:30 -> 27:30 IST day, IST / ET,
    # split at every exact aspect (Globex trades through the night)
    m_events = [(a["_jd"], f"{a['a']} {a['angle']} {a['b']}", a["tone"])
                for a in aspects + nxt]
    m_events += [(e[0], e[1], None) for e in moon["_events"]]
    metal_windows = _tile(m_events, jd0 + METAL_OPEN_H / 24,
                          jd0 + METAL_CLOSE_H / 24, calls["gold"]["tone"],
                          "Moon nakshatra", jd0, clock=_hhmm24, with_et=True)

    for inst in calls:
        calls[inst]["text"] = _prose(inst, calls[inst], moon, aspects, kaal)

    all_aspects = aspects + [a for a in nxt
                             if (a["_jd"] - jd0) * 24 <= METAL_CLOSE_H]
    for a in all_aspects:
        a.pop("_jd", None)
    for k in karanas:
        k.pop("_end", None)
    moon.pop("_events", None)
    kaal.pop("_rahu_jd", None)

    return {
        "date": d.isoformat(), "weekday": d.strftime("%A"),
        "closed": closed,
        "moon": moon,
        "panchang": {
            "tithi": f"{THITHIS[(tithi['num'] - 1) % 15]} "
                     f"({'Shukla' if tithi['num'] <= 15 else 'Krishna'})",
            "tithi_num": tithi["num"],
            "tithis_in_session": tithis_in_session,
            "tithi_ends": _strip(pe["thithi"]["ends"]),
            "nakshatra_ends": _strip(pe["natchathiram"]["ends"]),
            "yoga": pe["yogam"]["name"], "yoga_ends": _strip(pe["yogam"]["ends"]),
            "karanas": karanas,
            "vaar_tithi": vt,
        },
        "kaal": kaal,
        "aspects": all_aspects,
        "eclipse": ecl,
        "flags": flags,
        "calls": calls,
        "windows": windows,
        "metal_windows": metal_windows,
    }


def _strip(clock: str | None) -> str | None:
    """'HH:MM:SS' (hours may pass 24) -> 'HH:MM' with a (+1) marker."""
    if not clock:
        return None
    h, m, _ = clock.split(":")
    h = int(h)
    return f"{h % 24:02d}:{m}" + (f" (+{h // 24})" if h >= 24 else "")


def week(start: datetime.date, days: int = 7,
         lat: float = 19.076, lon: float = 72.8777) -> dict:
    out = [day(start + datetime.timedelta(days=i), lat, lon)
           for i in range(days)]
    return {
        "start": start.isoformat(),
        "end": (start + datetime.timedelta(days=days - 1)).isoformat(),
        "days": out,
        "regime": regime(start),
        "note": ("Saptarsh-style reconstruction. 'observed' = the channel "
                 "wrote this exact call in Jul-Aug 2026; 'extrapolated' = "
                 "filled in by nakshatra-lord / aspect-family rules never "
                 "seen in their output; 'classical' = a standard muhurta "
                 "table standing in for their unpublished one. Not "
                 "backtested, not advice."),
    }
