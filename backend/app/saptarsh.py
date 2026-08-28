"""Week-ahead Nifty / Gold / Silver outlook in the Saptarsh Insight style.

Reproduces, day by day, the components of that channel's daily bulletin
(see frontend NewConceptsPanel for the study notes):

  * Moon sign + nakshatra during the session, with change times
  * panchang end-times; Vishti karana and Vaidhriti / Vyatipata yoga
  * Rahu Kaal, Yamaganda, Gulika Kaal, Abhijit from sunrise-sunset
  * exact-time aspects at 0/45/60/90/120/135/150/180 between Sun, Moon,
    Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu
  * lunar / solar eclipse on the date
  * a Nifty, Gold and Silver call built from those

Every label carries a `source`: "observed" means the channel wrote that
exact call in the 14-28 Aug 2026 posts; "extrapolated" means it comes
from the simple rule below (nakshatra lord / aspect family) and has NOT
been seen in their output. Nothing here is backtested.

Sidereal Lahiri like engine.py. Aspect separations are ayanamsa-free.
"""
import datetime

import swisseph as swe

from . import nse_holidays
from .engine import FLAGS
from .names import NAKSHATRAS, RASIS, THITHIS
from .transit import DASHA_LORDS, SEG, _next_cross, _panchang_ends

TZ = 5.5
IST = datetime.timezone(datetime.timedelta(hours=TZ))
OPEN_H, CLOSE_H = 9.25, 15.5           # 09:15 - 15:30

BODIES = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
          ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
          ("Saturn", swe.SATURN), ("Uranus", swe.URANUS),
          ("Neptune", swe.NEPTUNE), ("Pluto", swe.PLUTO),
          ("Rahu", swe.MEAN_NODE)]          # the channel's "Mn Node"
ANGLES = [0, 45, 60, 90, 120, 135, 150, 180]
ASPECT_NAMES = {0: "conjunction", 45: "semi-square", 60: "sextile",
                90: "square", 120: "trine", 135: "sesquiquadrate",
                150: "quincunx", 180: "opposition"}

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
# the post gave no clean base call for that nakshatra.
OBSERVED_NAK: dict[str, tuple[str | None, str | None]] = {
    "Vishakha": ("bull", None),
    "Anuradha": ("neutral", "vol"),     # bearish on 20 Aug, supportive on 21
    "Jyeshtha": ("bull", "vol"),
    "Purva Ashadha": ("bull", "bear"),
    "Uttara Ashadha": (None, "bull"),
    "Shravana": ("neutral", "neutral"),
    "Dhanishta": ("bull", "bull"),
    "Shatabhisha": ("bear", "bear"),
}
LORD_TONE = {"Venus": "bull", "Jupiter": "bull", "Mercury": "bull",
             "Mars": "bull", "Moon": "neutral", "Sun": "neutral",
             "Saturn": "bear", "Rahu": "bear", "Ketu": "bear"}
TONE_WORD = {"bull": "bullish", "bear": "bearish", "vol": "volatile",
             "neutral": "neutral"}


def nak_tone(nak: str, instrument: str) -> tuple[str, str]:
    idx = NAKSHATRAS.index(nak)
    obs = OBSERVED_NAK.get(nak)
    col = 0 if instrument == "nifty" else 1
    if obs and obs[col]:
        return obs[col], "observed"
    return LORD_TONE[DASHA_LORDS[idx % 9]], "extrapolated"


# ---------------------------------------------------------- ephemeris

def _jd_local(d: datetime.date, hour: float) -> float:
    return swe.julday(d.year, d.month, d.day, hour - TZ)


def _hhmm(jd: float, jd0: float) -> str:
    """Clock time on the civil day of jd0; '+1' suffix past midnight."""
    total = round((jd - jd0) * 1440)
    day, rem = divmod(total, 1440)
    h, m = divmod(rem, 60)
    return f"{h:02d}:{m:02d}" + (f" (+{day})" if day else "")


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
    out = {"sign": RASIS[sign_i], "nakshatra": NAKSHATRAS[nak_i],
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


def _call(instrument: str, moon: dict, flags: list[str],
          karanas: list[dict], yoga: str) -> dict:
    nak = moon["nakshatra"]
    tone, src = nak_tone(nak, instrument)
    why = [f"Moon in {moon['sign']} / {nak} — {TONE_WORD[tone]} ({src})"]
    if moon["sign"] == "Vrischika":
        tone = "bear"
        why.append("Moon debilitated in Scorpio — bearish (their 20 Aug reading)")
    elif moon["sign"] == "Vrishabha" and tone != "bear":
        tone = "bull"
        why.append("Moon exalted in Taurus")
    if any(k["name"] == "Vishti" for k in karanas):
        if tone == "bull":
            tone = "vol"
        elif tone == "neutral":
            tone = "bear"
        why.append("Vishti karana in session — \"be very careful following "
                   "a bullish trend\"")
    if yoga in ("Vaidhriti", "Vyatipata"):
        tone = "vol" if tone != "bear" else "bear"
        why.append(f"{yoga} yoga — inauspicious, treat as volatile")
    caution = [f for f in flags]
    return {"tone": tone, "source": src, "why": why, "caution": caution}


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
    ecl = eclipse_on(d)

    flags: list[str] = []
    tithi = pe["thithi"]
    if tithi["num"] in (15, 30):
        flags.append(f"{'Purnima' if tithi['num'] == 15 else 'Amavasya'} — "
                     "Full/New Moon: a potential turning point, watch for a "
                     "change in price structure.")
    if ecl:
        flags.append(f"{ecl[0].upper() + ecl[1:]} today — many astro events on "
                     "the same day, confidence is low.")
    if any(a["a"] == "Mercury" and a["b"] == "Rahu" and a["angle"] == 180
           for a in aspects):
        flags.append("Mercury 180 Rahu — unclear trend, traders may get confused.")

    calls = {inst: _call(inst, moon, flags, karanas, pe["yogam"]["name"])
             for inst in ("nifty", "gold", "silver")}
    if moon["sign"] == "Kumbha" and ecl:
        calls["silver"]["why"].append(
            "Eclipse in Aquarius / Shatabhisha — the channel flags this as "
            "relevant to white metals")

    # session windows: split at in-session events, lean = latest driver
    events = [(e[0], e[1], None) for e in moon["_events"]]
    events += [(a["_jd"], f"{a['a']} {a['angle']} {a['b']}", a["tone"])
               for a in aspects if a["in_session"]]
    r0, r1 = kaal["_rahu_jd"]
    events += [(r0, "Rahu Kaal begins", "bear"), (r1, "Rahu Kaal ends", None)]
    for k in karanas:
        if k["_end"] and jd0 + OPEN_H / 24 < k["_end"] < jd0 + CLOSE_H / 24:
            events.append((k["_end"], f"{k['name']} karana ends", None))
    events = sorted(e for e in events
                    if jd0 + OPEN_H / 24 < e[0] < jd0 + CLOSE_H / 24)
    windows, start, tone, driver = [], jd0 + OPEN_H / 24, calls["nifty"]["tone"], "Moon nakshatra"
    for jd, label, t in events:
        windows.append({"start": _hhmm(start, jd0), "end": _hhmm(jd, jd0),
                        "tone": tone, "driver": driver})
        start, driver = jd, label
        if t:
            tone = t
        elif label.startswith("Moon enters"):
            tone = calls["nifty"]["tone"]
        elif label.startswith("Rahu Kaal ends") or label.endswith("karana ends"):
            tone = calls["nifty"]["tone"]
    windows.append({"start": _hhmm(start, jd0), "end": _hhmm(jd0 + CLOSE_H / 24, jd0),
                    "tone": tone, "driver": driver})

    for inst in calls:
        calls[inst]["text"] = _prose(inst, calls[inst], moon, aspects, kaal)

    for a in aspects:
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
            "tithi_ends": _strip(pe["thithi"]["ends"]),
            "nakshatra_ends": _strip(pe["natchathiram"]["ends"]),
            "yoga": pe["yogam"]["name"], "yoga_ends": _strip(pe["yogam"]["ends"]),
            "karanas": karanas,
        },
        "kaal": kaal,
        "aspects": aspects,
        "eclipse": ecl,
        "flags": flags,
        "calls": calls,
        "windows": windows,
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
        "note": ("Saptarsh Insight–style reconstruction. 'observed' = the "
                 "channel wrote this exact call in Aug 2026; 'extrapolated' "
                 "= filled in by nakshatra-lord / aspect-family rules never "
                 "seen in their output. Not backtested, not advice."),
    }
