"""Radix chart + transit-to-natal aspects — TROPICAL zodiac.

The radix is the Nifty 50 first-trade chart, 22 April 1996 — the one
specification of the source system confirmed from two independent
directions (stated on camera in Lesson 6, and reverse-engineered from
the Venus–Venus calls before he named it). Cast at
swe.julday(1996, 4, 22, 6.5); fixtures in test_gann_golden.py.

Computed tropically on purpose — see aspects.py's module docstring for
the zodiac decision. The ayanamsa does NOT cancel against a 1996 radix.
"""
from functools import lru_cache

import swisseph as swe

from ..engine import GANN_BODIES
from .aspects import TROPICAL_FLAGS

RADIX_JD = swe.julday(1996, 4, 22, 6.5)
RADIX_DATE = "1996-04-22"


@lru_cache(maxsize=1)
def radix() -> dict[str, float]:
    """Natal tropical longitudes of the Nifty birth chart."""
    out = {}
    for name, body in GANN_BODIES:
        out[name] = swe.calc_ut(RADIX_JD, body, TROPICAL_FLAGS)[0][0] % 360
    return out
