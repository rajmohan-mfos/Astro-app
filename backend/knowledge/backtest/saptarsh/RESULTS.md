# Saptarsh-style outlook — backtest 2016-01-01 → 2026-08-28

Method: `app/saptarsh.py` is run for every day of the window and
its calls are scored against the realised move. Nifty = close vs
open of the session (the call is a session call); gold / silver =
COMEX front-month close vs previous close on the New-York-dated bar,
which is the 03:30 → 27:30 IST Globex day the metals report covers.
`base` is the up-rate over the same days; `naive` is what always
calling the majority side would have scored on exactly those days;
z is against base; p is the exact two-sided binomial against 50%;
perm-p is a 2,000-draw moving-block permutation of the returns.
Nothing here was tuned on these prices — the rules come from his
posts, the base tables from classical texts.

## NIFTY — 2626 trading days, base up-rate 46.9%

| Test | n | hit | 95% CI | naive | z vs base | p | perm-p |
|---|---|---|---|---|---|---|---|
| Final call, all directional days | 1946 | 51.9% | [49.7, 54.1] | 52.4% | -0.41 | 0.098 | 0.075 |
|   source = observed | 1757 | 52.3% | [50.0, 54.6] | 53.2% | -0.72 | 0.056 | nan |
|   source = extrapolated | 189 | 48.1% | [41.1, 55.2] | 55.0% | -1.90 | 0.663 | nan |
|   Mercury direct | 1561 | 52.1% | [49.6, 54.6] | 53.2% | -0.86 | 0.105 | nan |
|   Mercury retrograde (his moratorium) | 385 | 51.2% | [46.2, 56.1] | 50.9% | +0.10 | 0.684 | nan |
| Nakshatra base call alone | 1950 | 49.1% | [46.9, 51.3] | 52.5% | -2.95 | 0.455 | 0.556 |
| Window lean (duration-weighted, |lean| > 0.2) | 2061 | 52.0% | [49.9, 54.2] | 52.9% | -0.84 | 0.071 | 0.134 |
| 'Volatile' call → |move| above median | 489 | 46.0% | [41.6, 50.4] | 0.0% | -1.76 | 0.086 | nan |

Per year (final call): 2016 51.1% (n=180) · 2017 47.4% (n=175) · 2018 46.0% (n=187) · 2019 50.3% (n=177) · 2020 60.0% (n=185) · 2021 51.6% (n=188) · 2022 51.6% (n=184) · 2023 59.7% (n=181) · 2024 46.6% (n=189) · 2025 51.7% (n=180) · 2026 56.7% (n=120)

### Moon nakshatra at the open

| Nakshatra | his call | n | up-rate | mean (bp) | z | p vs base |
|---|---|---|---|---|---|---|
| Ashwini | bear (obs) | 98 | 50.0% | -9.5 | +0.61 | 0.546 |
| Bharani | bear (obs) | 89 | 43.8% | -16.8 | -0.59 | 0.596 |
| Krittika | neutral (obs) | 99 | 55.6% | +10.2 | +1.72 | 0.088 |
| Rohini | bull (obs) | 95 | 54.7% | +2.0 | +1.53 | 0.150 |
| Mrigashira | bull (obs) | 98 | 43.9% | -17.2 | -0.60 | 0.613 |
| Ardra | bear (ext) | 97 | 57.7% | -0.6 | +2.13 | 0.041 |
| Punarvasu | bull (obs) | 96 | 51.0% | +2.0 | +0.81 | 0.474 |
| Pushya | bull (obs) | 94 | 51.1% | -3.9 | +0.81 | 0.470 |
| Ashlesha | bull (obs) | 99 | 42.4% | -13.0 | -0.90 | 0.421 |
| Magha | bear (obs) | 103 | 39.8% | -11.7 | -1.45 | 0.167 |
| Purva Phalguni | bull (ext) | 95 | 49.5% | -7.3 | +0.50 | 0.681 |
| Uttara Phalguni | neutral (ext) | 91 | 50.5% | +1.4 | +0.69 | 0.529 |
| Hasta | bull (obs) | 101 | 46.5% | -8.4 | -0.08 | 1.000 |
| Chitra | bull (obs) | 91 | 53.8% | +3.4 | +1.32 | 0.208 |
| Swati | bear (obs) | 96 | 44.8% | +5.4 | -0.42 | 0.684 |
| Vishakha | vol (obs) | 90 | 41.1% | -3.8 | -1.10 | 0.292 |
| Anuradha | neutral (obs) | 104 | 38.5% | -19.9 | -1.73 | 0.095 |
| Jyeshtha | bull (obs) | 101 | 51.5% | +0.5 | +0.92 | 0.371 |
| Mula | bear (obs) | 104 | 49.0% | -3.5 | +0.43 | 0.695 |
| Purva Ashadha | bull (obs) | 98 | 37.8% | -21.2 | -1.82 | 0.085 |
| Uttara Ashadha | bull (obs) | 98 | 58.2% | +10.6 | +2.23 | 0.026 |
| Shravana | neutral (obs) | 91 | 48.4% | +3.6 | +0.27 | 0.834 |
| Dhanishta | bull (obs) | 95 | 41.1% | -13.3 | -1.15 | 0.260 |
| Shatabhisha | bear (obs) | 99 | 48.5% | -2.2 | +0.31 | 0.764 |
| Purva Bhadrapada | bull (obs) | 103 | 36.9% | -23.6 | -2.04 | 0.048 |
| Uttara Bhadrapada | neutral (obs) | 103 | 39.8% | -17.5 | -1.45 | 0.167 |
| Revati | neutral (obs) | 98 | 42.9% | -8.4 | -0.81 | 0.479 |

### Rules as event studies (direction; 'wide' = |move| above the median)

| Rule | n | up-rate | base | mean (bp) | all (bp) | wide | z | p vs base |
|---|---|---|---|---|---|---|---|---|
| Amavasya in session | 111 | 50.5% | 46.9% | -3.4 | -6.2 | 45% | +0.75 | 0.506 |
| Purnima in session | 97 | 49.5% | 46.9% | -4.8 | -6.2 | 43% | +0.51 | 0.613 |
| Kshaya tithi | 113 | 47.8% | 46.9% | +1.8 | -6.2 | 46% | +0.19 | 0.851 |
| Vishti karana in session | 537 | 41.5% | 46.9% | -13.8 | -6.2 | 49% | -2.50 | 0.014 |
| Vaidhriti yoga | 103 | 50.5% | 46.9% | -7.5 | -6.2 | 57% | +0.73 | 0.490 |
| Vyatipata yoga | 96 | 44.8% | 46.9% | -4.8 | -6.2 | 50% | -0.42 | 0.684 |
| Mercury retrograde | 516 | 48.1% | 46.9% | -4.7 | -6.2 | 50% | +0.52 | 0.628 |
| Mercury retro midpoint | 22 | 50.0% | 46.9% | +0.2 | -6.2 | 50% | +0.29 | 0.833 |
| Mercury combust | 1025 | 46.2% | 46.9% | -6.8 | -6.2 | 47% | -0.43 | 0.684 |
| Eclipse day | 26 | 34.6% | 46.9% | -12.0 | -6.2 | 23% | -1.26 | 0.242 |
| Sun–Moon aspect in session | 392 | 47.2% | 46.9% | -4.8 | -6.2 | 48% | +0.11 | 0.919 |
| Slow-planet sign ingress (Mars..Uranus) | 73 | 45.2% | 46.9% | -11.4 | -6.2 | 62% | -0.29 | 0.815 |
| Planetary station | 95 | 48.4% | 46.9% | -0.6 | -6.2 | 56% | +0.29 | 0.837 |
| Kaal Sarp yog | 598 | 45.3% | 46.9% | -10.5 | -6.2 | 55% | -0.78 | 0.437 |
| Grand trine | 44 | 38.6% | 46.9% | -12.5 | -6.2 | 57% | -1.10 | 0.293 |
| Nakshatra stellium (≥3) | 542 | 51.3% | 46.9% | -2.5 | -6.2 | 58% | +2.04 | 0.043 |
| Sign stellium (≥4) | 606 | 47.5% | 46.9% | -5.4 | -6.2 | 53% | +0.30 | 0.776 |
| Early-degree cluster (≥6 under 10°) | 481 | 40.3% | 46.9% | -8.7 | -6.2 | 50% | -2.89 | 0.004 |
| Moon in Scorpio (debilitated) | 225 | 43.6% | 46.9% | -10.6 | -6.2 | 56% | -1.01 | 0.317 |
| Moon in Taurus (exalted) | 215 | 51.6% | 46.9% | +0.1 | -6.2 | 52% | +1.38 | 0.172 |
| Moon in a Rahu-ruled star | 292 | 50.3% | 46.9% | +0.8 | -6.2 | 52% | +1.17 | 0.242 |
| Moon in a Saturn-ruled star | 301 | 42.9% | 46.9% | -14.1 | -6.2 | 53% | -1.41 | 0.166 |
| Moon in a Venus/Jupiter-ruled star | 571 | 43.3% | 46.9% | -12.0 | -6.2 | 46% | -1.75 | 0.086 |
| Vaar-Tithi observed bullish | 54 | 48.1% | 46.9% | +4.7 | -6.2 | 54% | +0.18 | 0.892 |
| Vaar-Tithi observed bearish | 160 | 43.8% | 46.9% | -9.1 | -6.2 | 55% | -0.80 | 0.430 |
| Vaar-Tithi classical bullish | 335 | 47.2% | 46.9% | -7.6 | -6.2 | 50% | +0.09 | 0.956 |
| Vaar-Tithi classical bearish | 874 | 48.1% | 46.9% | -6.5 | -6.2 | 48% | +0.68 | 0.520 |
| Vaar-Nakshatra bullish | 458 | 46.7% | 46.9% | -8.8 | -6.2 | 56% | -0.08 | 0.963 |
| Vaar-Nakshatra bearish | 231 | 45.9% | 46.9% | -9.0 | -6.2 | 51% | -0.31 | 0.792 |
| Nakshatra changes in session | 664 | 48.2% | 46.9% | -4.0 | -6.2 | 50% | +0.66 | 0.509 |
| Moon changes sign in session | 302 | 46.7% | 46.9% | -6.2 | -6.2 | 50% | -0.08 | 0.954 |

31 rule tests; Bonferroni α = 0.0016; **0 survive**.

### Observed aspect labels (exact hit on the day; n ≥ 15)

| Aspect → his label | n | label hit | up-rate | mean (bp) | p (hit vs 50%) |
|---|---|---|---|---|---|
| Moon 150 Mars → bull | 57 | 56.1% | 56.1% | +1.5 | 0.427 |
| Moon 60 Rahu → bear | 55 | 50.9% | 49.1% | -5.8 | 1.000 |
| Sun 72 Moon → bear | 55 | 47.3% | 52.7% | +10.1 | 0.788 |
| Moon 60 Uranus → bear | 52 | 40.4% | 59.6% | +2.4 | 0.212 |
| Moon 90 Venus → bear | 50 | 46.0% | 54.0% | +15.2 | 0.672 |
| Moon 60 Saturn → bull | 50 | 48.0% | 48.0% | -8.2 | 0.888 |
| Moon 90 Uranus → bear | 50 | 48.0% | 52.0% | +4.4 | 0.888 |
| Moon 90 Saturn → bear | 49 | 53.1% | 46.9% | -18.6 | 0.775 |
| Moon 150 Jupiter → bull | 49 | 38.8% | 38.8% | -9.3 | 0.152 |
| Moon 120 Venus → bull | 48 | 50.0% | 50.0% | -6.2 | 1.000 |
| Moon 45 Neptune → bear | 48 | 45.8% | 54.2% | +7.3 | 0.665 |
| Moon 45 Rahu → bear | 47 | 59.6% | 40.4% | -10.7 | 0.243 |
| Sun 135 Moon → bull | 46 | 39.1% | 39.1% | -13.1 | 0.184 |
| Moon 135 Mars → bull | 46 | 60.9% | 60.9% | +16.7 | 0.184 |
| Sun 120 Moon → bear | 45 | 51.1% | 48.9% | +8.1 | 1.000 |
| Moon 120 Uranus → bull | 44 | 50.0% | 50.0% | +9.8 | 1.000 |
| Moon 135 Mercury → bull | 44 | 54.5% | 54.5% | -3.9 | 0.652 |
| Moon 45 Saturn → bear | 42 | 50.0% | 50.0% | -4.3 | 1.000 |
| Moon 0 Neptune → bear | 28 | 50.0% | 50.0% | -5.0 | 1.000 |
| Moon 180 Saturn → bull | 25 | 60.0% | 60.0% | +26.4 | 0.424 |
| Moon 180 Rahu → bull | 25 | 32.0% | 32.0% | -24.1 | 0.108 |
| Moon 0 Pluto → bull | 25 | 60.0% | 60.0% | +3.2 | 0.424 |
| Moon 0 Rahu → bear | 24 | 45.8% | 54.2% | +22.0 | 0.839 |
| Moon 0 Mars → bull | 24 | 45.8% | 45.8% | -36.8 | 0.839 |
| Moon 0 Saturn → bull | 23 | 43.5% | 43.5% | -12.9 | 0.678 |
| Moon 0 Jupiter → bear | 23 | 47.8% | 52.2% | -5.5 | 1.000 |
| Moon 180 Jupiter → bear | 22 | 54.5% | 45.5% | -6.2 | 0.832 |
| Moon 0 Venus → bear | 21 | 52.4% | 47.6% | +2.9 | 1.000 |

## GOLD — 2678 trading days, base up-rate 53.9%

| Test | n | hit | 95% CI | naive | z vs base | p | perm-p |
|---|---|---|---|---|---|---|---|
| Final call, all directional days | 1947 | 48.8% | [46.6, 51.0] | 54.6% | -5.19 | 0.297 | 0.668 |
|   source = observed | 1788 | 49.0% | [46.7, 51.3] | 54.6% | -4.75 | 0.408 | nan |
|   source = extrapolated | 159 | 46.5% | [39.0, 54.3] | 55.3% | -2.23 | 0.428 | nan |
|   Mercury direct | 1583 | 48.8% | [46.4, 51.3] | 54.1% | -4.19 | 0.366 | nan |
|   Mercury retrograde (his moratorium) | 364 | 48.6% | [43.5, 53.7] | 57.1% | -3.28 | 0.637 | nan |
| Nakshatra base call alone | 2386 | 49.7% | [47.7, 51.7] | 54.5% | -4.73 | 0.790 | 0.545 |
| Window lean (duration-weighted, |lean| > 0.2) | 1695 | 49.4% | [47.0, 51.8] | 53.0% | -2.97 | 0.627 | 0.399 |
| 'Volatile' call → |move| above median | 688 | 49.0% | [45.3, 52.7] | 0.0% | -0.53 | 0.620 | nan |

Per year (final call): 2016 51.6% (n=186) · 2017 47.8% (n=186) · 2018 47.3% (n=182) · 2019 40.7% (n=182) · 2020 52.1% (n=192) · 2021 54.9% (n=182) · 2022 51.1% (n=180) · 2023 54.2% (n=179) · 2024 48.0% (n=177) · 2025 39.8% (n=181) · 2026 49.2% (n=120)

### Moon nakshatra at the open

| Nakshatra | his call | n | up-rate | mean (bp) | z | p vs base |
|---|---|---|---|---|---|---|
| Ashwini | bull (obs) | 100 | 58.0% | +6.5 | +0.83 | 0.424 |
| Bharani | bear (obs) | 91 | 54.9% | -0.9 | +0.20 | 0.916 |
| Krittika | bull (obs) | 104 | 62.5% | +20.4 | +1.76 | 0.094 |
| Rohini | bear (obs) | 95 | 61.1% | +15.7 | +1.40 | 0.181 |
| Mrigashira | bull (obs) | 98 | 44.9% | -8.8 | -1.78 | 0.085 |
| Ardra | bear (obs) | 98 | 56.1% | -2.4 | +0.44 | 0.686 |
| Punarvasu | bear (obs) | 101 | 56.4% | +14.2 | +0.51 | 0.619 |
| Pushya | bull (obs) | 94 | 45.7% | -4.9 | -1.58 | 0.121 |
| Ashlesha | neutral (obs) | 101 | 54.5% | +5.2 | +0.12 | 0.921 |
| Magha | bear (ext) | 101 | 55.4% | +8.4 | +0.31 | 0.766 |
| Purva Phalguni | bull (ext) | 102 | 50.0% | -0.5 | -0.79 | 0.487 |
| Uttara Phalguni | bull (obs) | 97 | 54.6% | +4.5 | +0.15 | 0.919 |
| Hasta | bear (obs) | 104 | 43.3% | -12.3 | -2.17 | 0.031 |
| Chitra | bull (obs) | 94 | 59.6% | -6.0 | +1.11 | 0.301 |
| Swati | bear (obs) | 106 | 61.3% | +29.4 | +1.54 | 0.144 |
| Vishakha | vol (obs) | 91 | 56.0% | +6.8 | +0.41 | 0.753 |
| Anuradha | bull (obs) | 105 | 52.4% | +8.2 | -0.31 | 0.770 |
| Jyeshtha | vol (obs) | 100 | 36.0% | -20.6 | -3.59 | 0.000 |
| Mula | bull (obs) | 102 | 66.7% | +29.0 | +2.59 | 0.010 |
| Purva Ashadha | bear (obs) | 104 | 57.7% | +7.0 | +0.78 | 0.491 |
| Uttara Ashadha | bull (obs) | 97 | 60.8% | +27.0 | +1.37 | 0.186 |
| Shravana | bear (obs) | 99 | 53.5% | +23.0 | -0.07 | 1.000 |
| Dhanishta | bull (obs) | 99 | 47.5% | -4.1 | -1.28 | 0.226 |
| Shatabhisha | bear (obs) | 100 | 53.0% | +6.1 | -0.18 | 0.920 |
| Purva Bhadrapada | bear (obs) | 98 | 52.0% | +8.5 | -0.37 | 0.761 |
| Uttara Bhadrapada | bull (obs) | 99 | 49.5% | -2.8 | -0.88 | 0.420 |
| Revati | bear (obs) | 98 | 51.0% | +3.8 | -0.57 | 0.613 |

### Rules as event studies (direction; 'wide' = |move| above the median)

| Rule | n | up-rate | base | mean (bp) | all (bp) | wide | z | p vs base |
|---|---|---|---|---|---|---|---|---|
| Amavasya in session | 107 | 59.8% | 53.9% | +21.5 | +6.1 | 50% | +1.23 | 0.245 |
| Purnima in session | 110 | 47.3% | 53.9% | -11.5 | +6.1 | 45% | -1.39 | 0.181 |
| Kshaya tithi | 115 | 53.0% | 53.9% | -8.9 | +6.1 | 51% | -0.18 | 0.852 |
| Vishti karana in session | 546 | 53.3% | 53.9% | +4.8 | +6.1 | 47% | -0.28 | 0.797 |
| Vaidhriti yoga | 104 | 51.9% | 53.9% | -4.6 | +6.1 | 49% | -0.40 | 0.695 |
| Vyatipata yoga | 98 | 54.1% | 53.9% | +18.0 | +6.1 | 58% | +0.04 | 1.000 |
| Mercury retrograde | 516 | 55.4% | 53.9% | +3.7 | +6.1 | 50% | +0.70 | 0.508 |
| Mercury retro midpoint | 21 | 57.1% | 53.9% | -1.9 | +6.1 | 62% | +0.30 | 0.829 |
| Mercury combust | 1042 | 54.4% | 53.9% | +8.1 | +6.1 | 50% | +0.34 | 0.756 |
| Eclipse day | 31 | 67.7% | 53.9% | -0.9 | +6.1 | 45% | +1.55 | 0.150 |
| Sun–Moon aspect in session | 406 | 55.9% | 53.9% | +10.1 | +6.1 | 51% | +0.82 | 0.426 |
| Slow-planet sign ingress (Mars..Uranus) | 76 | 50.0% | 53.9% | -1.1 | +6.1 | 45% | -0.68 | 0.565 |
| Planetary station | 97 | 59.8% | 53.9% | +11.6 | +6.1 | 47% | +1.17 | 0.263 |
| Kaal Sarp yog | 612 | 50.8% | 53.9% | -3.6 | +6.1 | 55% | -1.52 | 0.134 |
| Grand trine | 46 | 47.8% | 53.9% | -1.6 | +6.1 | 46% | -0.82 | 0.461 |
| Nakshatra stellium (≥3) | 554 | 55.1% | 53.9% | +8.3 | +6.1 | 60% | +0.55 | 0.609 |
| Sign stellium (≥4) | 623 | 54.3% | 53.9% | +7.8 | +6.1 | 55% | +0.19 | 0.872 |
| Early-degree cluster (≥6 under 10°) | 492 | 57.1% | 53.9% | +14.8 | +6.1 | 53% | +1.44 | 0.161 |
| Moon in Scorpio (debilitated) | 226 | 46.5% | 53.9% | -3.5 | +6.1 | 50% | -2.24 | 0.028 |
| Moon in Taurus (exalted) | 220 | 57.7% | 53.9% | +12.7 | +6.1 | 44% | +1.14 | 0.279 |
| Moon in a Rahu-ruled star | 304 | 56.9% | 53.9% | +11.5 | +6.1 | 53% | +1.06 | 0.301 |
| Moon in a Saturn-ruled star | 298 | 49.3% | 53.9% | +0.4 | +6.1 | 48% | -1.58 | 0.117 |
| Moon in a Venus/Jupiter-ruled star | 587 | 54.5% | 53.9% | +5.9 | +6.1 | 50% | +0.31 | 0.772 |
| Vaar-Tithi observed bullish | 57 | 54.4% | 53.9% | -3.0 | +6.1 | 47% | +0.08 | 1.000 |
| Vaar-Tithi observed bearish | 166 | 54.8% | 53.9% | +17.0 | +6.1 | 51% | +0.24 | 0.816 |
| Vaar-Tithi classical bullish | 352 | 56.0% | 53.9% | +9.0 | +6.1 | 56% | +0.78 | 0.454 |
| Vaar-Tithi classical bearish | 892 | 54.1% | 53.9% | +7.6 | +6.1 | 48% | +0.16 | 0.893 |
| Vaar-Nakshatra bullish | 461 | 53.1% | 53.9% | +8.6 | +6.1 | 50% | -0.32 | 0.779 |
| Vaar-Nakshatra bearish | 232 | 55.2% | 53.9% | +7.9 | +6.1 | 50% | +0.39 | 0.742 |
| Nakshatra changes in session | 688 | 57.1% | 53.9% | +12.0 | +6.1 | 52% | +1.70 | 0.092 |
| Moon changes sign in session | 307 | 53.4% | 53.9% | +4.0 | +6.1 | 55% | -0.16 | 0.909 |

31 rule tests; Bonferroni α = 0.0016; **0 survive**.

### Observed aspect labels (exact hit on the day; n ≥ 15)

| Aspect → his label | n | label hit | up-rate | mean (bp) | p (hit vs 50%) |
|---|---|---|---|---|---|
| Moon 90 Saturn → bear | 203 | 41.4% | 58.6% | +4.4 | 0.017 |
| Moon 60 Uranus → bear | 200 | 47.0% | 53.0% | +11.3 | 0.437 |
| Moon 135 Mars → bull | 199 | 53.8% | 53.8% | +5.2 | 0.321 |
| Moon 45 Rahu → bear | 198 | 47.0% | 53.0% | +0.8 | 0.434 |
| Moon 45 Neptune → bear | 197 | 47.2% | 52.3% | +10.4 | 0.476 |
| Moon 60 Rahu → bear | 195 | 44.1% | 55.9% | +10.3 | 0.115 |
| Moon 120 Uranus → bull | 195 | 59.0% | 59.0% | +16.2 | 0.015 |
| Moon 60 Saturn → bull | 195 | 50.8% | 50.8% | +0.9 | 0.886 |
| Moon 90 Uranus → bear | 189 | 43.9% | 55.6% | +16.9 | 0.109 |
| Moon 150 Jupiter → bull | 188 | 56.9% | 56.9% | +7.3 | 0.068 |
| Sun 72 Moon → bear | 186 | 52.7% | 46.8% | -2.1 | 0.509 |
| Moon 45 Saturn → bear | 186 | 42.5% | 57.0% | +19.9 | 0.047 |
| Moon 150 Mars → bull | 184 | 52.7% | 52.7% | -5.1 | 0.507 |
| Sun 135 Moon → bull | 184 | 47.8% | 47.8% | -0.0 | 0.606 |
| Moon 90 Venus → bear | 182 | 46.2% | 53.3% | +7.5 | 0.335 |
| Moon 135 Mercury → bull | 179 | 59.8% | 59.8% | +14.1 | 0.011 |
| Moon 120 Venus → bull | 179 | 57.5% | 57.5% | +12.4 | 0.052 |
| Sun 120 Moon → bear | 175 | 42.3% | 57.1% | +14.7 | 0.049 |
| Moon 0 Jupiter → bear | 111 | 48.6% | 51.4% | +0.9 | 0.850 |
| Moon 180 Jupiter → bear | 105 | 49.5% | 50.5% | +3.8 | 1.000 |
| Moon 0 Rahu → bear | 102 | 44.1% | 54.9% | +5.4 | 0.276 |
| Moon 0 Pluto → bull | 100 | 58.0% | 58.0% | +9.1 | 0.133 |
| Moon 0 Neptune → bear | 99 | 43.4% | 55.6% | +9.3 | 0.228 |
| Moon 180 Saturn → bull | 98 | 58.2% | 58.2% | +15.1 | 0.129 |
| Moon 180 Rahu → bull | 96 | 55.2% | 55.2% | +2.6 | 0.358 |
| Moon 0 Saturn → bull | 95 | 52.6% | 52.6% | -5.7 | 0.682 |
| Moon 0 Venus → bear | 92 | 48.9% | 50.0% | +4.3 | 0.917 |
| Moon 0 Mars → bull | 91 | 52.7% | 52.7% | +8.4 | 0.675 |
| Sun 0 Mercury → bull | 50 | 50.0% | 50.0% | +11.1 | 1.000 |
| Sun 120 Saturn → bull | 17 | 58.8% | 58.8% | +54.5 | 0.629 |
| Sun 150 Pluto → bear | 17 | 52.9% | 47.1% | -19.5 | 1.000 |
| Sun 45 Venus → bull | 17 | 52.9% | 52.9% | +22.4 | 1.000 |
| Sun 120 Jupiter → bull | 16 | 43.8% | 43.8% | -7.0 | 0.804 |
| Sun 45 Rahu → bear | 16 | 50.0% | 50.0% | +3.4 | 1.000 |
| Sun 60 Saturn → bear | 15 | 53.3% | 46.7% | -10.8 | 1.000 |
| Venus 120 Jupiter → bear | 15 | 33.3% | 66.7% | +38.3 | 0.302 |
| Sun 135 Pluto → bear | 15 | 40.0% | 60.0% | -14.2 | 0.607 |

## SILVER — 2678 trading days, base up-rate 52.5%

| Test | n | hit | 95% CI | naive | z vs base | p | perm-p |
|---|---|---|---|---|---|---|---|
| Final call, all directional days | 1947 | 49.7% | [47.4, 51.9] | 52.5% | -2.50 | 0.786 | 0.472 |
|   source = observed | 1788 | 49.6% | [47.3, 51.9] | 52.7% | -2.65 | 0.759 | nan |
|   source = extrapolated | 159 | 50.3% | [42.6, 58.0] | 50.3% | +0.00 | 1.000 | nan |
|   Mercury direct | 1583 | 49.3% | [46.9, 51.8] | 52.1% | -2.16 | 0.615 | nan |
|   Mercury retrograde (his moratorium) | 364 | 51.1% | [46.0, 56.2] | 54.4% | -1.26 | 0.714 | nan |
| Nakshatra base call alone | 2386 | 50.1% | [48.1, 52.1] | 52.7% | -2.58 | 0.951 | 0.451 |
| Window lean (duration-weighted, |lean| > 0.2) | 1695 | 48.1% | [45.8, 50.5] | 52.1% | -3.26 | 0.132 | 0.859 |
| 'Volatile' call → |move| above median | 688 | 50.3% | [46.6, 54.0] | 0.0% | +0.15 | 0.909 | nan |

Per year (final call): 2016 50.5% (n=186) · 2017 53.2% (n=186) · 2018 50.5% (n=182) · 2019 44.0% (n=182) · 2020 47.4% (n=192) · 2021 56.6% (n=182) · 2022 47.2% (n=180) · 2023 55.3% (n=179) · 2024 49.2% (n=177) · 2025 44.2% (n=181) · 2026 47.5% (n=120)

### Moon nakshatra at the open

| Nakshatra | his call | n | up-rate | mean (bp) | z | p vs base |
|---|---|---|---|---|---|---|
| Ashwini | bull (obs) | 100 | 53.0% | +14.8 | +0.11 | 0.921 |
| Bharani | bear (obs) | 91 | 48.4% | -21.2 | -0.79 | 0.463 |
| Krittika | bull (obs) | 104 | 57.7% | +39.5 | +1.07 | 0.326 |
| Rohini | bear (obs) | 95 | 58.9% | +30.9 | +1.27 | 0.219 |
| Mrigashira | bull (obs) | 98 | 43.9% | -25.9 | -1.70 | 0.105 |
| Ardra | bear (obs) | 98 | 51.0% | -36.4 | -0.29 | 0.840 |
| Punarvasu | bear (obs) | 101 | 50.5% | +18.8 | -0.40 | 0.692 |
| Pushya | bull (obs) | 94 | 45.7% | +7.4 | -1.30 | 0.215 |
| Ashlesha | neutral (obs) | 101 | 56.4% | +24.1 | +0.80 | 0.486 |
| Magha | bear (ext) | 101 | 49.5% | -9.8 | -0.60 | 0.552 |
| Purva Phalguni | bull (ext) | 102 | 49.0% | -9.7 | -0.70 | 0.490 |
| Uttara Phalguni | bull (obs) | 97 | 51.5% | -3.1 | -0.18 | 0.919 |
| Hasta | bear (obs) | 104 | 49.0% | -36.3 | -0.70 | 0.494 |
| Chitra | bull (obs) | 94 | 54.3% | -0.0 | +0.35 | 0.757 |
| Swati | bear (obs) | 106 | 60.4% | +42.4 | +1.63 | 0.119 |
| Vishakha | vol (obs) | 91 | 54.9% | +14.5 | +0.47 | 0.675 |
| Anuradha | bull (obs) | 105 | 50.5% | +11.6 | -0.41 | 0.697 |
| Jyeshtha | vol (obs) | 100 | 40.0% | -53.8 | -2.50 | 0.016 |
| Mula | bull (obs) | 102 | 58.8% | +26.5 | +1.29 | 0.234 |
| Purva Ashadha | bear (obs) | 104 | 51.0% | +22.2 | -0.31 | 0.769 |
| Uttara Ashadha | bull (obs) | 97 | 57.7% | +30.9 | +1.04 | 0.311 |
| Shravana | bear (obs) | 99 | 59.6% | +52.7 | +1.42 | 0.160 |
| Dhanishta | bull (obs) | 99 | 59.6% | +14.4 | +1.42 | 0.160 |
| Shatabhisha | bear (obs) | 100 | 43.0% | +12.3 | -1.90 | 0.071 |
| Purva Bhadrapada | bear (obs) | 98 | 54.1% | +18.2 | +0.32 | 0.763 |
| Uttara Bhadrapada | bull (obs) | 99 | 53.5% | +12.9 | +0.21 | 0.841 |
| Revati | bear (obs) | 98 | 54.1% | +25.8 | +0.32 | 0.763 |

### Rules as event studies (direction; 'wide' = |move| above the median)

| Rule | n | up-rate | base | mean (bp) | all (bp) | wide | z | p vs base |
|---|---|---|---|---|---|---|---|---|
| Amavasya in session | 107 | 66.4% | 52.5% | +52.0 | +8.4 | 50% | +2.88 | 0.005 |
| Purnima in session | 110 | 45.5% | 52.5% | -18.6 | +8.4 | 58% | -1.47 | 0.152 |
| Kshaya tithi | 115 | 49.6% | 52.5% | -3.9 | +8.4 | 46% | -0.62 | 0.576 |
| Vishti karana in session | 546 | 51.5% | 52.5% | +11.3 | +8.4 | 49% | -0.47 | 0.668 |
| Vaidhriti yoga | 104 | 57.7% | 52.5% | -11.8 | +8.4 | 44% | +1.07 | 0.326 |
| Vyatipata yoga | 98 | 52.0% | 52.5% | +21.2 | +8.4 | 55% | -0.08 | 1.000 |
| Mercury retrograde | 516 | 52.9% | 52.5% | +0.1 | +8.4 | 50% | +0.20 | 0.860 |
| Mercury retro midpoint | 21 | 71.4% | 52.5% | +2.9 | +8.4 | 48% | +1.74 | 0.124 |
| Mercury combust | 1042 | 52.5% | 52.5% | +11.2 | +8.4 | 50% | +0.02 | 1.000 |
| Eclipse day | 31 | 58.1% | 52.5% | +0.8 | +8.4 | 48% | +0.62 | 0.592 |
| Sun–Moon aspect in session | 406 | 54.7% | 52.5% | +11.6 | +8.4 | 49% | +0.89 | 0.398 |
| Slow-planet sign ingress (Mars..Uranus) | 76 | 47.4% | 52.5% | -2.9 | +8.4 | 57% | -0.89 | 0.422 |
| Planetary station | 97 | 56.7% | 52.5% | +22.5 | +8.4 | 56% | +0.84 | 0.418 |
| Kaal Sarp yog | 612 | 50.7% | 52.5% | -3.1 | +8.4 | 52% | -0.90 | 0.374 |
| Grand trine | 46 | 50.0% | 52.5% | +36.8 | +8.4 | 57% | -0.33 | 0.769 |
| Nakshatra stellium (≥3) | 554 | 53.2% | 52.5% | +14.6 | +8.4 | 57% | +0.37 | 0.734 |
| Sign stellium (≥4) | 623 | 53.5% | 52.5% | +9.1 | +8.4 | 51% | +0.49 | 0.630 |
| Early-degree cluster (≥6 under 10°) | 492 | 54.1% | 52.5% | +25.7 | +8.4 | 56% | +0.71 | 0.498 |
| Moon in Scorpio (debilitated) | 226 | 46.9% | 52.5% | -12.9 | +8.4 | 50% | -1.67 | 0.096 |
| Moon in Taurus (exalted) | 220 | 54.1% | 52.5% | +24.5 | +8.4 | 48% | +0.48 | 0.637 |
| Moon in a Rahu-ruled star | 304 | 51.6% | 52.5% | +7.1 | +8.4 | 53% | -0.29 | 0.774 |
| Moon in a Saturn-ruled star | 298 | 50.0% | 52.5% | +10.7 | +8.4 | 52% | -0.85 | 0.417 |
| Moon in a Venus/Jupiter-ruled star | 587 | 51.3% | 52.5% | +7.5 | +8.4 | 51% | -0.58 | 0.591 |
| Vaar-Tithi observed bullish | 57 | 49.1% | 52.5% | +10.6 | +8.4 | 44% | -0.51 | 0.691 |
| Vaar-Tithi observed bearish | 166 | 50.0% | 52.5% | +16.6 | +8.4 | 47% | -0.64 | 0.535 |
| Vaar-Tithi classical bullish | 352 | 54.8% | 52.5% | +11.1 | +8.4 | 51% | +0.89 | 0.393 |
| Vaar-Tithi classical bearish | 892 | 52.1% | 52.5% | +11.5 | +8.4 | 53% | -0.20 | 0.841 |
| Vaar-Nakshatra bullish | 461 | 49.2% | 52.5% | +8.8 | +8.4 | 51% | -1.39 | 0.176 |
| Vaar-Nakshatra bearish | 232 | 50.4% | 52.5% | +1.6 | +8.4 | 53% | -0.62 | 0.554 |
| Nakshatra changes in session | 688 | 53.9% | 52.5% | +17.0 | +8.4 | 50% | +0.77 | 0.446 |
| Moon changes sign in session | 307 | 55.4% | 52.5% | -2.5 | +8.4 | 51% | +1.02 | 0.331 |

31 rule tests; Bonferroni α = 0.0016; **0 survive**.

### Observed aspect labels (exact hit on the day; n ≥ 15)

| Aspect → his label | n | label hit | up-rate | mean (bp) | p (hit vs 50%) |
|---|---|---|---|---|---|
| Moon 90 Saturn → bear | 203 | 42.4% | 57.6% | +9.0 | 0.035 |
| Moon 60 Uranus → bear | 200 | 47.0% | 53.0% | +7.8 | 0.437 |
| Moon 135 Mars → bull | 199 | 49.7% | 49.7% | -3.2 | 1.000 |
| Moon 45 Rahu → bear | 198 | 46.0% | 54.0% | -0.4 | 0.286 |
| Moon 45 Neptune → bear | 197 | 44.7% | 55.3% | +24.5 | 0.154 |
| Moon 60 Rahu → bear | 195 | 46.7% | 52.8% | +31.1 | 0.390 |
| Moon 120 Uranus → bull | 195 | 59.0% | 59.0% | +13.0 | 0.015 |
| Moon 60 Saturn → bull | 195 | 49.7% | 49.7% | -6.8 | 1.000 |
| Moon 90 Uranus → bear | 189 | 45.5% | 54.5% | +30.8 | 0.244 |
| Moon 150 Jupiter → bull | 188 | 54.8% | 54.8% | +22.2 | 0.215 |
| Sun 72 Moon → bear | 186 | 51.6% | 48.4% | +10.8 | 0.714 |
| Moon 45 Saturn → bear | 186 | 42.5% | 57.0% | +39.7 | 0.047 |
| Moon 150 Mars → bull | 184 | 53.3% | 53.3% | -9.0 | 0.417 |
| Sun 135 Moon → bull | 184 | 40.8% | 40.8% | -30.8 | 0.015 |
| Moon 90 Venus → bear | 182 | 48.9% | 51.1% | +7.7 | 0.824 |
| Moon 135 Mercury → bull | 179 | 57.0% | 57.0% | +9.3 | 0.073 |
| Moon 120 Venus → bull | 179 | 53.1% | 53.1% | +20.2 | 0.455 |
| Sun 120 Moon → bear | 175 | 41.7% | 58.3% | +31.1 | 0.034 |
| Moon 0 Jupiter → bear | 111 | 47.7% | 51.4% | -8.3 | 0.704 |
| Moon 180 Jupiter → bear | 105 | 48.6% | 51.4% | +0.8 | 0.845 |
| Moon 0 Rahu → bear | 102 | 47.1% | 52.9% | +31.3 | 0.621 |
| Moon 0 Pluto → bull | 100 | 51.0% | 51.0% | +4.8 | 0.920 |
| Moon 0 Neptune → bear | 99 | 41.4% | 57.6% | +19.3 | 0.107 |
| Moon 180 Saturn → bull | 98 | 59.2% | 59.2% | +10.7 | 0.085 |
| Moon 180 Rahu → bull | 96 | 55.2% | 55.2% | -6.8 | 0.358 |
| Moon 0 Saturn → bull | 95 | 45.3% | 45.3% | -5.3 | 0.412 |
| Moon 0 Venus → bear | 92 | 43.5% | 56.5% | +11.5 | 0.251 |
| Moon 0 Mars → bull | 91 | 42.9% | 42.9% | -25.1 | 0.208 |
| Sun 0 Mercury → bull | 50 | 54.0% | 54.0% | +6.9 | 0.672 |
| Sun 120 Saturn → bull | 17 | 70.6% | 70.6% | +62.6 | 0.143 |
| Sun 150 Pluto → bear | 17 | 58.8% | 41.2% | -16.3 | 0.629 |
| Sun 45 Venus → bull | 17 | 70.6% | 70.6% | +82.9 | 0.143 |
| Sun 120 Jupiter → bull | 16 | 43.8% | 43.8% | -6.3 | 0.804 |
| Sun 45 Rahu → bear | 16 | 50.0% | 50.0% | -11.0 | 1.000 |
| Sun 60 Saturn → bear | 15 | 60.0% | 40.0% | -40.0 | 0.607 |
| Venus 120 Jupiter → bear | 15 | 46.7% | 53.3% | +69.0 | 1.000 |
| Sun 135 Pluto → bear | 15 | 46.7% | 53.3% | -53.0 | 1.000 |
