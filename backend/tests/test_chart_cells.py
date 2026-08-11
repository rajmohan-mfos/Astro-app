"""The author's panchang chart (OPTIONS MERSAL format), pinned against the
reference image dated 06-01-2022.

The reference prints degrees but no time or place. The cast moment was
solved from the MOON (the fastest body, so it pins time hardest) and comes
out at 09:01 IST; every other body then falls into place to within half an
arcmin — which is itself the evidence that the solved time is right.

The reference's LAGNA is deliberately not asserted: it sits ~10° from the
ascendant at the moment its own planets imply, so that chart was cast for
a different place or had its lagna entered by hand. Planets are
location-independent, which is why the rest still pins cleanly.
"""
import swisseph as swe

from app import transit

REF = dict(year=2022, month=1, day=6, hour=9, minute=1,
           tz_offset=5.5, lat=13.0827, lon_geo=80.2707)

# (rasi, DD.MM) exactly as the reference image prints them
EXPECTED = {
    "Sun": ("Dhanu", "21.37"), "Moon": ("Kumbha", "07.44"),
    "Mars": ("Vrischika", "22.36"), "Mercury": ("Makara", "10.44"),
    "Jupiter": ("Kumbha", "07.25"), "Venus": ("Dhanu", "26.19"),
    "Saturn": ("Makara", "18.18"), "Uranus": ("Mesha", "16.44"),
    "Neptune": ("Kumbha", "26.36"), "Pluto": ("Makara", "01.56"),
    "Rahu": ("Vrishabha", "05.06"), "Ketu": ("Vrischika", "05.06"),
}

# the ring outside the grid, read [sub, star]
EXPECTED_LORDS = {
    "Sun": ("Jupiter", "Venus"), "Moon": ("Rahu", "Rahu"),
    "Mercury": ("Moon", "Moon"), "Jupiter": ("Rahu", "Rahu"),
    "Venus": ("Ketu", "Venus"), "Saturn": ("Mercury", "Moon"),
    "Uranus": ("Moon", "Venus"), "Neptune": ("Venus", "Jupiter"),
    "Pluto": ("Jupiter", "Sun"), "Rahu": ("Saturn", "Sun"),
}


def _by_name(cells):
    return {it["name"]: (c["rasi"], it)
            for c in cells for it in c["items"]}


def test_reference_chart_degrees_reproduce():
    got = _by_name(transit.chart_cells(**REF))
    for name, (rasi, deg) in EXPECTED.items():
        assert got[name][0] == rasi, (name, got[name][0], rasi)
        assert got[name][1]["deg"] == deg, (name, got[name][1]["deg"], deg)


def test_reference_chart_ring_lords_reproduce():
    got = _by_name(transit.chart_cells(**REF))
    for name, (sub, star) in EXPECTED_LORDS.items():
        it = got[name][1]
        assert it["star_lord"] == star, (name, it["star_lord"], star)
        assert it["sub_lord"] == sub, (name, it["sub_lord"], sub)


def test_chart_is_lahiri_not_kp():
    """The discriminating test. KP is 5.5 arcmin from the reference and
    misses every printed degree; Lahiri is 0.3 arcmin away and hits them.
    An earlier commit switched this to KP by mistake — this pins it."""
    lahiri = _by_name(transit.chart_cells(**REF))
    kp = _by_name(transit.chart_cells(**REF,
                                      ayanamsa_mode=swe.SIDM_KRISHNAMURTI))
    # Lahiri matches the reference exactly
    assert lahiri["Saturn"][1]["deg"] == "18.18"
    # KP does not — and differs by the expected ~6 arcmin
    assert kp["Saturn"][1]["deg"] != "18.18"
    assert kp["Saturn"][1]["deg"] == "18.24"


def test_outer_planets_and_lagna_are_present():
    """The format carries what the nine-graha chart does not."""
    names = {it["name"] for c in transit.chart_cells(**REF)
             for it in c["items"]}
    assert {"Uranus", "Neptune", "Pluto", "Lagna"} <= names
    assert len(names) == 13


def test_bodies_within_a_cell_run_descending_by_degree():
    """Reference Makara reads 18.41, 18.18, 10.44, 01.56."""
    for cell in transit.chart_cells(**REF):
        degs = [float(it["deg"]) for it in cell["items"]]
        assert degs == sorted(degs, reverse=True), cell["rasi"]
