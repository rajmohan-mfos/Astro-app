# Vikas — backtest 2011-01-01 → 2026-08-28

Method: `app/vikas.py` computes his dates and day-lords from the
ephemeris (sidereal Lahiri; GannZilla-style tropical where he uses
it) for every day of the window; nothing was fitted to prices.
Nifty = ^NSEI daily bars. `base` is the same statistic over all
trading days; p is an exact binomial against that base (or a
random-subset permutation for mean returns). Where he gives a
number ('90%', '100%') it is quoted next to the result.

## A. Nakshatra-lord daily rule — malefic lord → up, benefic → down

His claim [V5]: the lord's nature sets the day's direction; he
excludes Sun and Moon days himself. Only sessions where one star
covers ≥ 4 h are used.

| rule | hits | rate | naive | 95% CI | p vs 50% | perm-p |
|---|---|---|---|---|---|---|
| lord rule (oc), ex Sun/Moon days | 1398/2808 |  49.8% |  54.6% | [47.9, 51.6] | 0.836 | 0.330 |
| lord rule (cc), ex Sun/Moon days | 1420/2807 |  50.6% |  51.6% | [48.7, 52.4] | 0.546 | 0.343 |

By lord (close vs open). `up` = share of those days that closed
up, then the same for the first / second half of the window — the
classical reading (benefic up, malefic down) is `100 − rate` where
the lord is malefic:

| lord | hits | rate (his reading) | up | up h1 | up h2 | p vs 50% |
|---|---|---|---|---|---|---|
| Ketu days (oc) | 179/407 |  44.0% |  44.0% |  44.8% |  43.1% | 0.017 |
| Venus days (oc) | 227/399 |  56.9% |  43.1% |  37.7% |  48.5% | 0.007 |
| Sun days (oc) | 208/391 |  53.2% |  53.2% |  52.8% |  53.6% | 0.225 |
| Moon days (oc) | 193/383 |  50.4% |  49.3% |  43.5% |  55.2% | 0.919 |
| Mars days (oc) | 192/393 |  48.9% |  48.9% |  50.0% |  47.7% | 0.687 |
| Rahu days (oc) | 193/394 |  49.0% |  49.0% |  45.7% |  52.3% | 0.724 |
| Jupiter days (oc) | 222/402 |  55.2% |  44.8% |  42.8% |  46.8% | 0.041 |
| Saturn days (oc) | 169/406 |  41.6% |  41.6% |  42.4% |  40.9% | 0.001 |
| Mercury days (oc) | 216/407 |  53.1% |  46.9% |  46.8% |  47.1% | 0.234 |

## B. The carry-over (day 1 closes against its lord → day 2 goes the other way)

Strict = his full condition set [V5]: consecutive trading days, opposite
natures, same Moon sign, no other planet changed sign. Loose = same Moon
sign only [V1]. His claim: 'this works 100%'.

| rule | hits | rate | naive | 95% CI | p vs 50% | perm-p |
|---|---|---|---|---|---|---|
| carry-over strict (day-2 close vs open) | 200/423 |  47.3% |  53.7% | [42.6, 52.0] | 0.285 | 0.550 |
| carry-over strict (day-2 close vs day-1 close) | 207/423 |  48.9% |  50.1% | [44.2, 53.7] | 0.697 | 0.745 |
| carry-over loose (day-2 close vs open) | 227/481 |  47.2% |  53.6% | [42.8, 51.7] | 0.236 | 0.584 |
| carry-over loose (day-2 close vs day-1 close) | 237/481 |  49.3% |  50.3% | [44.8, 53.7] | 0.784 | 0.686 |

| rule | hits | rate | base | 95% CI | p vs base |
|---|---|---|---|---|---|
| carry-over strict: day 2 does not close beyond day-1 extreme | 267/423 |  63.1% |  61.7% | [58.4, 67.6] | 0.582 |
| carry-over loose: day 2 does not close beyond day-1 extreme | 306/481 |  63.6% |  61.7% | [59.2, 67.8] | 0.399 |

## C. Saturn star falls → Mercury star retraces at least half next day

His claim: '90–100%', 'once in 2–3 months'. Hit = next day's high
reaches the 50% retracement of the fall (body: open→close; range:
high→low). Base = any down day followed by the next calendar day.

| rule | hits | rate | base | 95% CI | p vs base |
|---|---|---|---|---|---|
| Saturn→Mercury half-retrace (body) | 96/136 |  70.6% |  68.8% | [62.4, 77.6] | 0.712 |
| Saturn→Mercury half-retrace (range) | 92/136 |  67.6% |  70.3% | [59.4, 74.9] | 0.511 |

Instances (136): 2025-01-06 (-1.8% → miss, next +0.1%), 2025-02-11 (-1.3% → miss, next -0.0%), 2025-03-10 (-0.3% → hit, next +0.7%), 2025-06-10 (-0.4% → hit, next +0.0%), 2025-06-19 (-0.0% → hit, next +1.3%), 2025-08-21 (-0.2% → miss, next -0.8%), 2025-12-08 (-0.8% → miss, next -0.1%), 2026-03-10 (-0.1% → hit, next -1.5%), 2026-03-19 (-0.8% → hit, next +0.0%), 2026-05-21 (-0.7% → hit, next +0.2%), 2026-07-07 (-0.3% → miss, next -1.6%), 2026-07-15 (-0.0% → hit, next -0.3%) …

## D. The date candle — is his date's high/low a better breakout level?

For each date: first cross of the date candle's high or low within
5 sessions; follow-through = session 5 closes beyond the crossed
level; cross-day = the crossing session itself closes beyond;
held = neither side crossed in 5 sessions. Base over all Nifty days:
follow-through 57.5%, cross-day 66.0%, held 0.3%.
Forward returns: mean k-session return on the dates vs all days
(p = random-subset permutation).

| date family | n | follow-through | cross-day close | held | +1d bp (p) | +5d bp (p) | +10d bp (p) |
|---|---|---|---|---|---|---|---|
| Moon in a Saturn star (Nifty date) | 329 | 161/296 = 54% (p 0.29) | 69% | 0% (p 0.63) | +2 vs +4 (0.64) | +35 vs +21 (0.24) | +59 vs +42 (0.32) |
| Moon in Pushya | 112 | 51/98 = 52% (p 0.31) | 71% | 0% (p 1.00) | -12 vs +4 (0.09) | +25 vs +21 (0.83) | +84 vs +42 (0.16) |
| Moon in Anuradha | 106 | 53/95 = 56% (p 0.76) | 65% | 0% (p 1.00) | +4 vs +4 (0.96) | +27 vs +21 (0.79) | +23 vs +42 (0.57) |
| Moon in Uttara Bhadrapada | 111 | 57/103 = 55% (p 0.69) | 69% | 0% (p 1.00) | +14 vs +4 (0.32) | +53 vs +21 (0.15) | +68 vs +42 (0.40) |
| Moon in Mesha (both days) | 322 | 170/282 = 60% (p 0.37) | 64% | 0% (p 1.00) | +6 vs +4 (0.76) | +35 vs +21 (0.26) | +55 vs +42 (0.46) |
| Moon in Meena (both days) | 330 | 173/303 = 57% (p 0.91) | 66% | 1% (p 0.28) | +5 vs +4 (0.83) | +31 vs +21 (0.41) | +62 vs +42 (0.25) |
| Sun nakshatra ingress (any) | 423 | 212/366 = 58% (p 0.92) | 66% | 0% (p 0.65) | +4 vs +4 (0.95) | +13 vs +21 (0.46) | +39 vs +42 (0.83) |
| Mercury sign ingress (any) | 231 | 121/201 = 60% (p 0.48) | 60% | 0% (p 1.00) | -3 vs +4 (0.30) | +24 vs +21 (0.85) | +60 vs +42 (0.39) |
| Mercury enters Mesha | 18 | 12/16 = 75% (p 0.21) | 75% | 0% (p 1.00) | -22 vs +4 (0.26) | -34 vs +21 (0.29) | -21 vs +42 (0.39) |
| Venus sign ingress | 199 | 89/168 = 53% (p 0.24) | 64% | 0% (p 1.00) | +7 vs +4 (0.71) | +33 vs +21 (0.45) | +45 vs +42 (0.88) |
| Mars sign ingress | 112 | 59/100 = 59% (p 0.84) | 66% | 1% (p 0.30) | +0 vs +4 (0.70) | +18 vs +21 (0.88) | +67 vs +42 (0.41) |
| Jupiter sign ingress | 24 | 12/20 = 60% (p 1.00) | 55% | 0% (p 1.00) | +30 vs +4 (0.20) | +7 vs +21 (0.77) | +34 vs +42 (0.90) |
| Saturn sign ingress | 12 | 9/12 = 75% (p 0.26) | 58% | 0% (p 1.00) | -9 vs +4 (0.65) | -89 vs +21 (0.10) | -36 vs +42 (0.39) |
| Mars nakshatra ingress | 245 | 126/215 = 59% (p 0.78) | 65% | 0% (p 0.54) | -7 vs +4 (0.08) | +16 vs +21 (0.71) | +27 vs +42 (0.47) |
| big×small 30°/60° (any) | 659 | 327/580 = 56% (p 0.59) | 67% | 1% (p 0.06) | +9 vs +4 (0.21) | +20 vs +21 (0.89) | +39 vs +42 (0.85) |
| big×small conjunction | 186 | 87/162 = 54% (p 0.34) | 61% | 1% (p 0.12) | +5 vs +4 (0.95) | +14 vs +21 (0.68) | +24 vs +42 (0.46) |
| Jupiter 30° Mercury | 43 | 26/38 = 68% (p 0.19) | 68% | 0% (p 1.00) | -12 vs +4 (0.31) | +20 vs +21 (0.98) | +49 vs +42 (0.87) |
| Sun conjunct Neptune | 16 | 8/12 = 67% (p 0.58) | 75% | 0% (p 1.00) | +6 vs +4 (0.94) | -46 vs +21 (0.24) | -57 vs +42 (0.22) |
| Venus conjunct Ketu/Rahu | 36 | 16/30 = 53% (p 0.71) | 73% | 0% (p 1.00) | -29 vs +4 (0.05) | +5 vs +21 (0.67) | +71 vs +42 (0.58) |
| Mercury conjunct Ketu/Rahu | 41 | 21/37 = 57% (p 1.00) | 68% | 0% (p 1.00) | -4 vs +4 (0.62) | -23 vs +21 (0.22) | +38 vs +42 (0.94) |
| Moon 45/135/225/315° at open (tropical) | 323 | 180/281 = 64% (p 0.03) | 68% | 0% (p 0.63) | +3 vs +4 (0.89) | +25 vs +21 (0.75) | +59 vs +42 (0.33) |
| Moon 45/135/225/315° at open (sidereal) | 319 | 155/284 = 55% (p 0.34) | 65% | 0% (p 0.63) | +7 vs +4 (0.61) | +24 vs +21 (0.79) | +65 vs +42 (0.19) |
| Moon 270° at open (tropical) | 76 | 27/65 = 42% (p 0.01) | 52% | 1% (p 0.21) | +6 vs +4 (0.89) | -31 vs +21 (0.05) | +5 vs +42 (0.32) |
| Venus within 8° of Uranus (same sign) | 12 | 7/10 = 70% (p 0.53) | 70% | 0% (p 1.00) | +10 vs +4 (0.84) | +72 vs +21 (0.44) | +39 vs +42 (0.98) |
| Venus at 45° longitude (tropical) | 16 | 11/15 = 73% (p 0.30) | 80% | 0% (p 1.00) | +65 vs +4 (0.02) | +70 vs +21 (0.40) | +74 vs +42 (0.68) |
| Sun–Venus 45° (semi-square) | 38 | 17/31 = 55% (p 0.86) | 77% | 3% (p 0.11) | +6 vs +4 (0.92) | +4 vs +21 (0.65) | +2 vs +42 (0.44) |
| Moon in a Jupiter star (Bank Nifty date) | 320 | 162/283 = 57% (p 0.47) | 62% | 0% (p 1.00) | +3 vs +5 (0.77) | +31 vs +26 (0.79) | +61 vs +53 (0.76) |
| Moon in a Saturn star (Bank Nifty) | 329 | 167/291 = 57% (p 0.41) | 64% | 0% (p 1.00) | +5 vs +5 (0.94) | +51 vs +26 (0.16) | +98 vs +53 (0.08) |

## E. Sun nakshatra ingresses (his yearly dates)

Base over all days: week holds the day's low 31.0%, 5-day reversal 49.7%, mean 5-day return +21 bp.

| Sun enters | n | week holds low | reversal | +3d bp | +5d bp (p) | his note | years |
|---|---|---|---|---|---|---|---|
| Ashwini | 16 | 4/16 = 25% | 25% | +57 | +69 (0.39) |  | 2011:broke 2012:hold 2013:hold 2014:broke 2015:broke 2016:broke 2017:broke 2018:hold 2019:broke 2020:broke 2021:broke 2022:broke 2023:broke 2024:broke 2025:hold 2026:broke |
| Bharani | 16 | 2/16 = 12% | 44% | -33 | -129 (0.02) |  | 2011:broke 2012:broke 2013:broke 2014:broke 2015:broke 2016:broke 2017:broke 2018:broke 2019:broke 2020:broke 2021:broke 2022:broke 2023:hold 2024:broke 2025:hold 2026:broke |
| Krittika | 16 | 4/16 = 25% | 50% | +60 | +66 (0.43) |  | 2011:broke 2012:broke 2013:broke 2014:hold 2015:broke 2016:broke 2017:broke 2018:broke 2019:broke 2020:broke 2021:broke 2022:hold 2023:broke 2024:hold 2025:hold 2026:broke |
| Rohini | 16 | 8/16 = 50% | 31% | +97 | +110 (0.11) | Moon-lorded star → minor top, reversal date | 2011:hold 2012:broke 2013:broke 2014:broke 2015:broke 2016:hold 2017:hold 2018:hold 2019:hold 2020:hold 2021:hold 2022:broke 2023:hold 2024:broke 2025:broke 2026:broke |
| Mrigashira | 16 | 4/16 = 25% | 50% | -59 | -45 (0.24) |  | 2011:broke 2012:hold 2013:broke 2014:broke 2015:broke 2016:broke 2017:broke 2018:hold 2019:broke 2020:broke 2021:broke 2022:broke 2023:hold 2024:broke 2025:broke 2026:hold |
| Ardra | 16 | 6/16 = 38% | 62% | +74 | +154 (0.02) |  | 2011:hold 2012:hold 2013:hold 2014:hold 2015:broke 2016:broke 2017:broke 2018:broke 2019:broke 2020:broke 2021:broke 2022:broke 2023:broke 2024:hold 2025:hold 2026:broke |
| Punarvasu | 16 | 5/16 = 31% | 56% | -13 | +14 (0.90) |  | 2011:broke 2012:broke 2013:hold 2014:broke 2015:broke 2016:broke 2017:hold 2018:hold 2019:broke 2020:broke 2021:broke 2022:hold 2023:hold 2024:broke 2025:broke 2026:broke |
| Pushya | 16 | 3/16 = 19% | 56% | +23 | -22 (0.45) |  | 2011:broke 2012:broke 2013:broke 2014:hold 2015:broke 2016:broke 2017:broke 2018:hold 2019:broke 2020:hold 2021:broke 2022:broke 2023:broke 2024:broke 2025:broke 2026:broke |
| Ashlesha | 16 | 6/16 = 38% | 50% | +19 | +11 (0.87) |  | 2011:broke 2012:hold 2013:broke 2014:broke 2015:broke 2016:broke 2017:broke 2018:hold 2019:hold 2020:hold 2021:hold 2022:broke 2023:broke 2024:hold 2025:broke 2026:broke |
| Magha | 16 | 6/16 = 38% | 38% | -47 | -38 (0.30) |  | 2011:broke 2012:hold 2013:broke 2014:hold 2015:broke 2016:broke 2017:broke 2018:hold 2019:broke 2020:hold 2021:broke 2022:broke 2023:broke 2024:hold 2025:hold 2026:broke |
| Purva Phalguni | 15 | 7/15 = 47% | 47% | +40 | +64 (0.45) |  | 2011:broke 2012:broke 2013:broke 2014:hold 2015:broke 2016:hold 2017:hold 2018:broke 2019:broke 2020:broke 2021:hold 2022:hold 2023:hold 2024:broke 2025:hold |
| Uttara Phalguni | 15 | 6/15 = 40% | 47% | +25 | +62 (0.48) |  | 2011:hold 2012:hold 2013:broke 2014:broke 2015:hold 2016:hold 2017:broke 2018:broke 2019:broke 2020:broke 2021:hold 2022:broke 2023:broke 2024:broke 2025:hold |
| Hasta | 15 | 1/15 = 7% | 73% | -28 | +2 (0.75) | Moon-lorded star → top (27 Sep 2024 ATH), reversal date | 2011:broke 2012:broke 2013:broke 2014:broke 2015:broke 2016:broke 2017:broke 2018:broke 2019:broke 2020:hold 2021:broke 2022:broke 2023:broke 2024:broke 2025:broke |
| Chitra | 15 | 6/15 = 40% | 40% | +65 | +112 (0.12) |  | 2011:hold 2012:broke 2013:broke 2014:broke 2015:broke 2016:broke 2017:hold 2018:hold 2019:hold 2020:broke 2021:hold 2022:hold 2023:broke 2024:broke 2025:broke |
| Swati | 15 | 4/15 = 27% | 47% | +22 | +58 (0.51) |  | 2011:hold 2012:broke 2013:broke 2014:hold 2015:broke 2016:broke 2017:hold 2018:broke 2019:hold 2020:broke 2021:broke 2022:broke 2023:broke 2024:broke 2025:broke |
| Vishakha | 15 | 3/15 = 20% | 33% | -39 | -102 (0.04) |  | 2011:broke 2012:broke 2013:broke 2014:hold 2015:broke 2016:broke 2017:broke 2018:broke 2019:broke 2020:hold 2021:broke 2022:broke 2023:hold 2024:broke 2025:broke |
| Anuradha | 15 | 5/15 = 33% | 40% | +59 | +92 (0.22) |  | 2011:broke 2012:broke 2013:broke 2014:hold 2015:broke 2016:hold 2017:hold 2018:broke 2019:broke 2020:broke 2021:broke 2022:hold 2023:hold 2024:broke 2025:broke |
| Jyeshtha | 15 | 4/15 = 27% | 33% | -8 | -28 (0.42) |  | 2011:broke 2012:broke 2013:broke 2014:broke 2015:broke 2016:hold 2017:broke 2018:broke 2019:broke 2020:hold 2021:broke 2022:broke 2023:hold 2024:hold 2025:broke |
| Mula | 15 | 3/15 = 20% | 40% | -14 | +0 (0.71) |  | 2011:broke 2012:broke 2013:broke 2014:broke 2015:hold 2016:broke 2017:hold 2018:broke 2019:hold 2020:broke 2021:broke 2022:broke 2023:broke 2024:broke 2025:broke |
| Purva Ashadha | 16 | 5/16 = 31% | 56% | +69 | +13 (0.89) |  | 2010:hold 2011:hold 2012:hold 2013:broke 2014:broke 2015:broke 2016:hold 2017:broke 2018:broke 2019:broke 2020:hold 2021:broke 2022:broke 2024:broke 2024:broke 2025:broke |
| Uttara Ashadha | 16 | 6/16 = 38% | 44% | +42 | +49 (0.63) | market does not fall that week (his '95%'); sell puts | 2011:broke 2012:hold 2013:hold 2014:hold 2015:broke 2016:broke 2017:hold 2018:broke 2019:broke 2020:broke 2021:broke 2022:hold 2023:broke 2024:broke 2025:hold 2026:broke |
| Shravana | 16 | 3/16 = 19% | 69% | -50 | +15 (0.93) | Moon-lorded star → bottom / support, reversal date | 2011:broke 2012:broke 2013:hold 2014:broke 2015:broke 2016:broke 2017:hold 2018:broke 2019:broke 2020:broke 2021:broke 2022:broke 2023:broke 2024:hold 2025:broke 2026:broke |
| Dhanishta | 16 | 4/16 = 25% | 44% | -47 | -27 (0.38) | bearish 2–3 days | 2011:broke 2012:hold 2013:broke 2014:hold 2015:broke 2016:broke 2017:broke 2018:hold 2019:broke 2020:broke 2021:broke 2022:broke 2023:hold 2024:broke 2025:broke 2026:broke |
| Shatabhisha | 16 | 3/16 = 19% | 56% | -133 | -167 (0.00) |  | 2011:broke 2012:broke 2013:broke 2014:hold 2015:broke 2016:broke 2017:hold 2018:broke 2019:hold 2020:broke 2021:broke 2022:broke 2023:broke 2024:broke 2025:broke 2026:broke |
| Purva Bhadrapada | 16 | 5/16 = 31% | 50% | +1 | -31 (0.37) |  | 2011:hold 2012:broke 2013:hold 2014:hold 2015:broke 2016:broke 2017:broke 2018:broke 2019:hold 2020:broke 2021:broke 2022:broke 2023:broke 2024:broke 2025:hold 2026:broke |
| Uttara Bhadrapada | 16 | 3/16 = 19% | 31% | -80 | -13 (0.55) |  | 2011:broke 2012:broke 2013:broke 2014:broke 2015:broke 2016:hold 2017:broke 2018:broke 2019:broke 2020:broke 2021:broke 2022:broke 2023:hold 2024:broke 2025:hold 2026:broke |
| Revati | 16 | 5/16 = 31% | 31% | +22 | +69 (0.40) |  | 2011:hold 2012:broke 2013:broke 2014:broke 2015:hold 2016:broke 2017:hold 2018:broke 2019:broke 2020:broke 2021:broke 2022:hold 2023:hold 2024:broke 2025:broke 2026:broke |

| rule | hits | rate | base | 95% CI | p vs base |
|---|---|---|---|---|---|
| all Sun ingresses: week holds the low | 121/423 |  28.6% |  31.0% | [24.5, 33.1] | 0.294 |
| all Sun ingresses: 5-day reversal | 195/423 |  46.1% |  49.7% | [41.4, 50.9] | 0.145 |

## F. Mercury enters Aries — 'the low is not closed below for months'

| rule | hits | rate | base | 95% CI | p vs base |
|---|---|---|---|---|---|
| Mercury→Mesha: low holds 20 sessions | 7/18 |  38.9% |  25.8% | [20.3, 61.4] | 0.278 |
| all Mercury sign ingresses: low holds 20 sessions | 63/230 |  27.4% |  25.8% | [22.0, 33.5] | 0.598 |
| Mercury→Mesha: low holds 40 sessions | 5/18 |  27.8% |  20.3% | [12.5, 50.9] | 0.389 |
| all Mercury sign ingresses: low holds 40 sessions | 44/229 |  19.2% |  20.3% | [14.6, 24.8] | 0.743 |
| Mercury→Mesha: low holds 60 sessions | 4/18 |  22.2% |  17.9% | [9.0, 45.2] | 0.548 |
| all Mercury sign ingresses: low holds 60 sessions | 42/228 |  18.4% |  17.9% | [13.9, 24.0] | 0.796 |

Mercury→Mesha / 20: 2011-03-29:held, 2011-05-11:broke, 2012-05-07:broke, 2013-04-29:held, 2014-04-21:broke, 2015-04-13:broke, 2016-04-04:broke, 2017-03-27:held, 2018-05-10:broke, 2019-05-06:broke, 2020-04-27:broke, 2021-04-19:held, 2022-04-08:broke, 2023-03-31:held, 2024-03-26:held, 2024-05-13:held, 2025-05-07:broke, 2026-04-30:broke

Mercury→Mesha / 40: 2011-03-29:broke, 2011-05-11:broke, 2012-05-07:broke, 2013-04-29:broke, 2014-04-21:broke, 2015-04-13:broke, 2016-04-04:broke, 2017-03-27:held, 2018-05-10:broke, 2019-05-06:broke, 2020-04-27:broke, 2021-04-19:held, 2022-04-08:broke, 2023-03-31:held, 2024-03-26:held, 2024-05-13:held, 2025-05-07:broke, 2026-04-30:broke

Mercury→Mesha / 60: 2011-03-29:broke, 2011-05-11:broke, 2012-05-07:broke, 2013-04-29:broke, 2014-04-21:broke, 2015-04-13:broke, 2016-04-04:broke, 2017-03-27:held, 2018-05-10:broke, 2019-05-06:broke, 2020-04-27:broke, 2021-04-19:held, 2022-04-08:broke, 2023-03-31:held, 2024-03-26:broke, 2024-05-13:held, 2025-05-07:broke, 2026-04-30:broke

## G. Transit spans — metals and Jupiter+Venus

Return from the ingress session to the planet's next ingress; base
= every span of that planet (all its sign / nakshatra transits) on
the same instrument. `metal` = Nifty Metal index if Yahoo served it.

| rule / instrument | n | mean span return | base mean (n) | goes the claimed way | p (mean) |
|---|---|---|---|---|---|
| Mars in 12th sign from Saturn / gold (fall) | 8 | +2.3% | +1.9% (77) | 3/8 vs base 42% (p 1.00) | 0.82 |
| Mars in 12th sign from Saturn / silver (fall) | 8 | -1.2% | +2.6% (77) | 4/8 vs base 45% (p 1.00) | 0.37 |
| Mars in 12th sign from Saturn / metal (fall) | 11 | -4.0% | +1.8% (106) | 8/11 vs base 44% (p 0.07) | 0.07 |
| Mars in 12th sign from Saturn / nifty (fall) | 11 | -5.2% | +1.6% (111) | 8/11 vs base 35% (p 0.02) | 0.00 |
| Mars in Saturn's sign / gold (rise) | 7 | +3.5% | +1.9% (77) | 5/7 vs base 58% (p 0.71) | 0.44 |
| Mars in Saturn's sign / silver (rise) | 7 | +7.4% | +2.6% (77) | 5/7 vs base 55% (p 0.47) | 0.29 |
| Mars in Saturn's sign / metal (rise) | 11 | +8.2% | +1.8% (106) | 8/11 vs base 56% (p 0.37) | 0.05 |
| Mars in Saturn's sign / nifty (rise) | 11 | +7.5% | +1.6% (111) | 11/11 vs base 65% (p 0.01) | 0.00 |
| Mars in Dhanishta / gold (fall) | 6 | +0.9% | +0.9% (165) | 2/6 vs base 41% (p 1.00) | 1.00 |
| Mars in Dhanishta / silver (fall) | 6 | +3.1% | +1.3% (165) | 2/6 vs base 47% (p 0.69) | 0.59 |
| Mars in Dhanishta / metal (fall) | 8 | -0.7% | +0.8% (232) | 5/8 vs base 45% (p 0.48) | 0.55 |
| Mars in Dhanishta / nifty (fall) | 9 | -0.8% | +0.7% (244) | 7/9 vs base 43% (p 0.04) | 0.28 |
| Jupiter & Venus in one sign / nifty (rise) | 26 | +0.1% | +0.8% (198) | 13/26 vs base 56% (p 0.69) | 0.43 |
| Jupiter & Venus in one sign / banknifty (rise) | 26 | +1.3% | +1.0% (198) | 15/26 vs base 56% (p 1.00) | 0.86 |

Robustness (mean is dominated by the 2020 span):

| rule / instrument | median | base median | mean ex-2020 | mean 1st half | mean 2nd half | by key |
|---|---|---|---|---|---|---|
| Mars in 12th sign from Saturn / gold | +3.9% | +1.4% | +2.7% | +4.7% | -0.0% | 12th_from_saturn_even +1.9%, 12th_from_saturn_odd +3.1% |
| Mars in 12th sign from Saturn / metal | -4.0% | +1.2% | -0.1% | +3.7% | -10.5% | 12th_from_saturn_even -10.1%, 12th_from_saturn_odd +3.2% |
| Mars in 12th sign from Saturn / nifty | -3.4% | +1.7% | -2.1% | +0.9% | -10.3% | 12th_from_saturn_even -10.8%, 12th_from_saturn_odd +1.4% |
| Mars in Saturn's sign / gold | +1.8% | +1.4% | +2.6% | +1.5% | +4.9% | with_saturn +3.5% |
| Mars in Saturn's sign / metal | +6.0% | +1.2% | +7.7% | +7.3% | +8.8% | with_saturn +8.2% |
| Mars in Saturn's sign / nifty | +5.0% | +1.7% | +6.2% | +8.6% | +6.7% | with_saturn +7.5% |
| Mars in Dhanishta / gold | +1.2% | +0.7% | +0.8% | -0.9% | +2.7% | Dhanishta +0.9% |
| Mars in Dhanishta / metal | -1.9% | +0.8% | -1.2% | -2.0% | +0.6% | Dhanishta -0.7% |
| Mars in Dhanishta / nifty | -1.5% | +0.7% | -0.7% | -0.8% | -0.8% | Dhanishta -0.8% |
| Jupiter & Venus in one sign / nifty | +0.3% | +0.6% | +0.1% | +0.5% | -0.3% | with_jupiter +0.1%, with_venus +0.6% |

Mars in 12th sign from Saturn / gold: 2015-12-24→2016-02-22 +12.3% (dd -1.7%, 12th_from_saturn_even); 2016-06-20→2016-07-12 +3.4% (dd -2.8%, 12th_from_saturn_even); 2018-01-17→2018-03-08 -1.4% (dd -2.7%, 12th_from_saturn_odd); 2019-12-26→2020-02-10 +4.3% (dd -0.3%, 12th_from_saturn_odd); 2020-02-10→2020-03-23 -0.5% (dd -7.8%, 12th_from_saturn_even); 2022-01-18→2022-02-28 +4.8% (dd -1.8%, 12th_from_saturn_even); 2024-02-06→2024-03-18 +6.2% (dd -2.4%, 12th_from_saturn_odd); 2026-02-23→2026-04-02 -10.6% (dd -21.2%, 12th_from_saturn_even)

Mars in 12th sign from Saturn / nifty: 2011-10-31→2012-06-22 -3.4% (dd -14.9%, 12th_from_saturn_even); 2013-11-27→2014-02-04 -0.9% (dd -2.0%, 12th_from_saturn_odd); 2014-03-25→2014-07-14 +13.1% (dd -0.7%, 12th_from_saturn_odd); 2015-12-24→2016-02-22 -8.0% (dd -12.6%, 12th_from_saturn_even); 2016-06-20→2016-07-12 +3.4% (dd -3.8%, 12th_from_saturn_even); 2018-01-17→2018-03-08 -5.1% (dd -6.0%, 12th_from_saturn_odd); 2019-12-26→2020-02-10 -0.8% (dd -4.2%, 12th_from_saturn_odd); 2020-02-10→2020-03-23 -36.7% (dd -37.0%, 12th_from_saturn_even); 2022-01-17→2022-02-28 -8.3% (dd -11.5%, 12th_from_saturn_even); 2024-02-06→2024-03-18 +0.6% (dd -1.8%, 12th_from_saturn_odd); 2026-02-23→2026-04-02 -11.7% (dd -13.7%, 12th_from_saturn_even)

Mars in Saturn's sign / gold: 2016-02-22→2016-06-20 +6.7% (dd -0.9%, with_saturn); 2016-07-12→2016-09-19 -1.5% (dd -2.4%, with_saturn); 2018-03-08→2018-05-03 -0.7% (dd -1.3%, with_saturn); 2020-03-23→2020-05-05 +8.8% (dd -4.9%, with_saturn); 2022-02-28→2022-04-07 +1.8% (dd -0.3%, with_saturn); 2024-03-18→2024-04-23 +7.7% (dd -0.7%, with_saturn); 2026-04-02→2026-05-11 +1.4% (dd -3.0%, with_saturn)

Mars in Saturn's sign / nifty: 2012-06-22→2012-08-14 +4.6% (dd -2.2%, with_saturn); 2012-08-14→2012-10-01 +6.3% (dd -3.1%, with_saturn); 2014-02-04→2014-03-25 +9.8% (dd -1.1%, with_saturn); 2014-07-14→2014-09-05 +8.5% (dd -0.4%, with_saturn); 2016-02-22→2016-06-20 +13.9% (dd -5.6%, with_saturn); 2016-07-12→2016-09-19 +3.4% (dd -0.5%, with_saturn); 2018-03-08→2018-05-03 +4.3% (dd -2.8%, with_saturn); 2020-03-23→2020-05-05 +21.0% (dd -1.3%, with_saturn); 2022-02-28→2022-04-07 +5.0% (dd -6.7%, with_saturn); 2024-03-18→2024-04-23 +1.4% (dd -1.6%, with_saturn); 2026-04-02→2026-05-11 +4.9% (dd -2.3%, with_saturn)

Mars in Dhanishta / gold: 2016-12-05→2016-12-20 -3.6% (dd -4.3%, Dhanishta); 2018-10-25→2018-11-19 -0.5% (dd -2.7%, Dhanishta); 2020-04-27→2020-05-14 +1.5% (dd -2.4%, Dhanishta); 2022-03-30→2022-04-18 +2.6% (dd -1.0%, Dhanishta); 2024-03-07→2024-03-25 +0.8% (dd -0.5%, Dhanishta); 2026-02-17→2026-03-04 +4.9% (dd -0.7%, Dhanishta)

Mars in Dhanishta / nifty: 2011-02-07→2011-02-24 -2.5% (dd -4.0%, Dhanishta); 2013-01-17→2013-02-04 -0.9% (dd -1.0%, Dhanishta); 2014-12-29→2015-01-13 +0.6% (dd -2.2%, Dhanishta); 2016-12-05→2016-12-20 -0.6% (dd -0.9%, Dhanishta); 2018-10-25→2018-11-19 +6.3% (dd -1.2%, Dhanishta); 2020-04-27→2020-05-14 -1.5% (dd -2.6%, Dhanishta); 2022-03-30→2022-04-18 -1.9% (dd -2.5%, Dhanishta); 2024-03-07→2024-03-26 -2.2% (dd -3.5%, Dhanishta); 2026-02-16→2026-03-04 -4.7% (dd -5.4%, Dhanishta)

Jupiter & Venus in one sign / nifty: 2011-04-18→2011-05-11 -2.9% (dd -5.0%, with_jupiter); 2011-05-11→2011-06-06 -0.6% (dd -4.2%, with_jupiter); 2012-02-29→2012-03-28 -3.5% (dd -4.0%, with_jupiter); 2012-05-17→2012-08-01 +7.6% (dd -2.1%, with_venus); 2013-05-06→2013-05-29 +2.2% (dd -0.7%, with_jupiter); 2013-05-31→2013-06-24 -6.6% (dd -7.0%, with_venus); 2014-08-08→2014-09-01 +6.1% (dd -0.4%, with_jupiter); 2015-06-01→2015-07-06 +1.1% (dd -5.8%, with_jupiter); 2015-07-14→2015-08-14 +0.8% (dd -1.6%, with_venus); 2015-10-01→2015-11-03 +1.4% (dd -0.3%, with_jupiter); 2016-08-01→2016-08-25 -0.5% (dd -1.4%, with_jupiter); 2016-08-25→2016-09-19 +2.5% (dd -0.6%, with_jupiter); 2017-11-03→2017-11-27 -0.5% (dd -3.4%, with_jupiter); 2018-09-03→2019-01-02 -6.8% (dd -13.6%, with_jupiter); 2019-01-02→2019-01-30 -1.3% (dd -1.9%, with_jupiter); 2019-10-29→2019-11-21 +1.5% (dd -1.4%, with_jupiter); 2019-11-21→2019-12-16 +0.7% (dd -1.1%, with_jupiter); 2021-01-28→2021-02-22 +6.2% (dd -1.6%, with_jupiter); 2022-03-31→2022-04-28 -1.3% (dd -3.7%, with_jupiter); 2022-04-28→2022-05-24 -6.5% (dd -8.8%, with_jupiter); 2023-02-16→2023-03-13 -4.9% (dd -5.1%, with_jupiter); 2024-04-25→2024-05-21 -0.2% (dd -3.3%, with_jupiter); 2024-05-21→2024-06-13 +3.9% (dd -5.5%, with_jupiter); 2025-07-28→2025-08-21 +1.6% (dd -1.4%, with_jupiter); 2026-05-14→2026-06-09 -1.9% (dd -2.6%, with_jupiter); 2026-06-09→2026-07-06 +5.1% (dd -0.7%, with_jupiter)

## I. Monday green → Tuesday red

| rule | hits | rate | base | 95% CI | p vs base |
|---|---|---|---|---|---|
| Monday green → Tuesday red | 206/353 |  58.4% |  55.5% | [53.2, 63.4] | 0.285 |
| Monday red → Tuesday green | 176/373 |  47.2% |  44.5% | [42.2, 52.3] | 0.298 |

## Not testable without intraday data

- the high-cross / low-cross entries with the candle's other side as stop
- the first-1–2-hour rule, gap / order-block retests, flag targets
- the RBI-policy-day fade of the 10:00 candle (needs 5-minute bars)
- stock radix dates (needs incorporation / listing dates per stock)
