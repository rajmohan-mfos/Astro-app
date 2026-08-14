"""12 bhavam significations — reference table (12 BHAVAM EXPLANATION).

The market mapping the course actually uses is the house-count table
(உபஜெய/அபஜெய) and the prasanam judgment houses (2/6/11 profit, 5/8/12
loss), both codified elsewhere; this table glosses the houses a
prasanam's significators land in (see rules/prasanam.py).

SOURCE QUALITY (re-read 2026-08-14, both transcripts side by side). This
is the worst-transcribed video in the set and the entries are only as
good as what survived:

- The raw caption file COLLAPSES between 05:06 and 07:12 — fourteen
  consecutive lines of "8th house is for business partners" — which is
  exactly where houses 6, 7 and 8 are explained. It also drops ~2.5
  minutes outright (00:33–01:04, 01:26–02:26, 02:51–03:21, 04:08–04:38),
  including the whole of house 2.
- The Buzz translation of the same video carries those stretches, so
  houses 1, 2, 6, 7 and 8 below rest on Buzz ALONE. Houses 3, 4, 5, 9,
  10, 11 and 12 are attested in both and are the trustworthy rows.
- Where the two disagree only on wording, both were read; nothing here
  is taken from a single mangled line.

BHAVAM_SOURCE records which rows have one witness rather than two, so a
future reader can weigh a row without re-doing this comparison.
"""

# The gloss shown to the reader. Deliberately free of timestamps and
# provenance markers — these strings are concatenated into a prasanam
# finding (see prasanam._bhavam_finding), and a Telegram reply is not the
# place for citations. Provenance lives in BHAVAM_SOURCE below, where it
# can be checked without being read aloud.
BHAVAM = {
    1: "self, mind, one's own thoughts and troubles",
    2: "wealth, family, speech, eyes, food, early education — profit "
       "house",
    3: "siblings, courage/victory, short travel, communication, "
       "press/media, brokers",
    4: "mother, education, vehicles, property, cattle, agriculture, "
       "land and buildings",
    5: "children, grandfather, love, cinema, politics, music — "
       "speculation, stock exchange, gambling",
    6: "illness, hard work/service, enemies, others' goods, temporary "
       "income — negative for the native but a profit house for the "
       "market (2/6/11)",
    7: "spouse, business partners — explicitly NOT used for market "
       "judgment ('we don't use this much for the stock')",
    8: "heavy negativity — loss, theft of one's wealth, trouble with "
       "the law, ruin; the heavy loss house",
    9: "father, fortune/luck, long-distance travel, places of worship — "
       "an angle house in graph work",
    10: "profession and action, fame, social status, business",
    11: "gains, income without investment, sudden luck, no obstacles — "
        "heavy profit",
    12: "loss, expenditure, hidden and secret matters — median loss "
        "house",
}

# house → (witnesses, where). "buzz" means the raw caption file lost this
# stretch and only the Buzz translation carries it — one witness, not two.
BHAVAM_SOURCE = {
    1: ("buzz", "raw file drops 01:26–02:26"),
    2: ("buzz", "raw file drops 01:26–02:26; the 2/6/11 profit "
                "statement itself is at 00:23 in both"),
    3: ("both", "02:26–02:51"),
    4: ("both", "03:21–03:43"),
    5: ("both", "03:50–04:08"),
    6: ("buzz", "raw file collapses 05:06–07:12"),
    7: ("buzz", "raw file collapses 05:06–07:12"),
    8: ("buzz", "raw file collapses 05:06–07:12"),
    9: ("both", "07:12–07:50"),
    10: ("both", "07:50–08:25"),
    11: ("both", "08:29–09:46"),
    12: ("both", "09:46–10:16"),
}

SINGLE_WITNESS = {h for h, (w, _) in BHAVAM_SOURCE.items() if w == "buzz"}

MARKET_PROFIT_HOUSES = {2, 6, 11}     # [video @ 00:23] "2,6,11 is profit"
MARKET_LOSS_HOUSES = {5, 8, 12}

# [@ 01:04] "When we see from Rasi this is 1, and when we look from
# Lakkad this is 1"; [@ 10:32–10:40] "you can see it from your Rasi, you
# can see it from your Lakanam"; [@ 11:22–11:32] "when the moon is going
# we get negativity … the moon will be in a structure for 2.5 days".
#
# This is the third independent statement of the frame that
# prasanam.natal_moon_gate() implements — count from BOTH the janma rasi
# and the lagna — and it settles a discrepancy: [P2 @ 03:08] renders the
# Moon's stay as "2.5 hours", which is an ASR error. 2.5 days is right
# (the Moon crosses a rasi in ~2.25 days) and this video says it twice.
COUNT_FRAMES = ("janma rasi", "lagna")
MOON_DAYS_PER_RASI = 2.5
