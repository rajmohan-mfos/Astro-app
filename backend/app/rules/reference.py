"""Course reference tables — Kaala Purusha Chakram sheets (OPTIONS MERSAL).

Framework data the course displays but never turns into a market rule in
any class. Kept for display/lookup and future refinement; deliberately NOT
wired into the bias engine (see RULES-SOURCES.md — general background must
never masquerade as a transcribed market rule).
"""

# Lord → its three nakshatras, exactly as printed on the sheet.
NAKSHATRAS_BY_LORD = {
    "Ketu": ["Ashwini", "Magha", "Mula"],
    "Venus": ["Bharani", "Purva Phalguni", "Purva Ashadha"],
    "Sun": ["Krittika", "Uttara Phalguni", "Uttara Ashadha"],
    "Moon": ["Rohini", "Hasta", "Shravana"],
    "Mars": ["Mrigashira", "Chitra", "Dhanishta"],
    "Rahu": ["Ardra", "Swati", "Shatabhisha"],
    "Jupiter": ["Punarvasu", "Vishakha", "Purva Bhadrapada"],
    "Saturn": ["Pushya", "Anuradha", "Uttara Bhadrapada"],
    "Mercury": ["Ashlesha", "Jyeshtha", "Revati"],
}

# rasi index 0=Mesha … 11=Meena → (lord, quality, element, direction, gender)
RASI_ATTRS = [
    ("Mars", "movable", "fire", "east", "male"),
    ("Venus", "fixed", "earth", "south", "female"),
    ("Mercury", "dual", "air", "west", "male"),
    ("Moon", "movable", "water", "north", "female"),
    ("Sun", "fixed", "fire", "east", "male"),
    ("Mercury", "dual", "earth", "south", "female"),
    ("Venus", "movable", "air", "west", "male"),
    ("Mars", "fixed", "water", "north", "female"),
    ("Jupiter", "dual", "fire", "east", "male"),
    ("Saturn", "movable", "earth", "south", "female"),
    ("Saturn", "fixed", "air", "west", "male"),
    ("Jupiter", "dual", "water", "north", "female"),
]

# Central panel of the Kaala Purusha sheet
DEVA_TEAM = {"Jupiter", "Sun", "Moon", "Mars"}          # தேவர் அணி
ASURA_TEAM = {"Venus", "Mercury", "Saturn", "Rahu", "Ketu"}   # அசுர அணி

BENEFICS = {"Jupiter", "Venus"}          # + waxing Moon (சுபர்)
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}   # + waning Moon

MALE_PLANETS = {"Sun", "Mars", "Jupiter"}
FEMALE_PLANETS = {"Moon", "Venus", "Rahu"}
NEUTER_PLANETS = {"Mercury", "Saturn", "Ketu"}

# "புதன் சேரும் கிரகத்தின் தன்மை" — Mercury takes on the nature of the
# planet it joins. NOT applied: the market planet-list (கிரகங்கள்.docx)
# fixes Mercury as a sideways planet for trading, and no class applies the
# conjunction principle to a graph call. Candidate refinement only.
MERCURY_TAKES_CONJUNCT_NATURE = True

# Waxing Moon benefic / waning Moon malefic — same status: classical
# framework, not applied to the market bias by any class.
