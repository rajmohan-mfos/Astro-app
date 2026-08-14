"""12 bhavam significations — reference table (12 BHAVAM EXPLANATION).

Built from the raw caption file, cross-checked against the clean Buzz
transcript of the same video. The market mapping the course actually uses
is the house-count table (உபஜெய/அபஜெய) and the prasanam judgment houses
(2/6/11 profit, 5/8/12 loss), both codified elsewhere; this table glosses
the houses a prasanam's significators land in (see rules/prasanam.py).
"""

BHAVAM = {
    1: "self, the querent",
    2: "wealth, family, speech — profit house [video @ 00:23]",
    3: "siblings, courage/victory, short travel, communication, "
       "press/media, brokers",
    4: "mother, education, vehicles, property, agriculture [@ 03:21]",
    5: "children, love, speculation — stock exchange, gambling",
    6: "hard work, service, enemies, temporary income — negative for the "
       "native but a profit house for the market (2/6/11)",
    7: "spouse, business partners — explicitly NOT used for market "
       "judgment ('we don't use this much for the stock')",
    9: "father, fortune/luck, long-distance travel, places of worship — "
       "an angle house in graph work",
    8: "obstacles, heavy loss house",
    10: "profession, action",
    11: "gains, income without investment, sudden luck — heavy profit",
    12: "loss, expenditure — median loss house",
}

MARKET_PROFIT_HOUSES = {2, 6, 11}     # [video @ 00:23] "2,6,11 is profit"
MARKET_LOSS_HOUSES = {5, 8, 12}
