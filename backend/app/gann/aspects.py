"""Aspect mechanics — TROPICAL zodiac (no FLG_SIDEREAL).

Zodiac decision (gann-engine-CLAUDE.md §2a): transit-to-transit
separations are identical in both zodiacs (the ayanamsa cancels), but
transit-to-natal ones drift ~0.42° between a 1996 radix and a 2026
transit. All Gann rules were derived tropically in GannZilla, so this
package calls swisseph WITHOUT FLG_SIDEREAL. Only this package.

Daily snapshots are taken at 09:15 IST = 3.75 UT, the market open.
"""
import datetime

import swisseph as swe

from ..engine import GANN_BODIES

TROPICAL_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED
SNAPSHOT_UT_HOUR = 3.75          # 09:15 IST

BODY_IDS = dict(GANN_BODIES)


def jd_at(d: datetime.date) -> float:
    return swe.julday(d.year, d.month, d.day, SNAPSHOT_UT_HOUR)


def positions(d: datetime.date) -> dict[str, tuple[float, float]]:
    """{body: (tropical longitude, daily speed)} at the 09:15 IST snapshot."""
    jd = jd_at(d)
    out = {}
    for name, body in GANN_BODIES:
        pos = swe.calc_ut(jd, body, TROPICAL_FLAGS)[0]
        out[name] = (pos[0] % 360, pos[3])
    return out


def wrap180(x: float) -> float:
    """Fold an angle into (-180, 180]."""
    return -((-x + 180) % 360 - 180)


def separation(a: float, b: float) -> float:
    """Angular separation in [0, 180]."""
    d = abs(a - b) % 360
    return min(d, 360 - d)


def crossings(dates: list[datetime.date], lons_a: list[float],
              lons_b: list[float], target: float) -> list[datetime.date]:
    """Dates where the a–b separation crosses `target` exactly.

    Works on the SIGNED difference so 0° and 180° are detectable (the
    unsigned separation only bounces off those, it never changes sign).
    The abs(step) < 180 guard rejects the 359°→1° wrap, which would
    otherwise fire every target on every lap (gann-engine-CLAUDE.md §2).
    Each hit is dated to whichever of the two days is nearer exactness.
    """
    diffs = [wrap180(a - b) for a, b in zip(lons_a, lons_b)]
    hits: set[datetime.date] = set()
    for t in {wrap180(target), wrap180(-target)}:
        g = [wrap180(d - t) for d in diffs]
        for i in range(1, len(g)):
            if g[i - 1] * g[i] <= 0 and g[i - 1] != g[i] \
                    and abs(g[i] - g[i - 1]) < 180:
                hits.add(dates[i] if abs(g[i]) < abs(g[i - 1])
                         else dates[i - 1])
    return sorted(hits)


def stations(dates: list[datetime.date],
             speeds: list[float]) -> list[tuple[datetime.date, str]]:
    """(date, "retrograde begins"|"retrograde ends") on speed sign flips."""
    out = []
    for i in range(1, len(speeds)):
        if speeds[i - 1] > 0 >= speeds[i]:
            out.append((dates[i], "retrograde begins"))
        elif speeds[i - 1] < 0 <= speeds[i]:
            out.append((dates[i], "retrograde ends"))
    return out
