# Vikas — "Astro class" method (provenance notes)

Source: the user's YouTube playlist "Vikas astro class" (9 videos, Tamil +
Hindi + English, ~8.5 h), audio pulled with yt-dlp and transcribed with
`tools/transcribe.py --lang auto` into `C:\Users\hgkri\Downloads\vikas\
transcripts\`. Tags: [V1] Astro class 1 (2 h), [V2] Astro class 2, [V3],
[V4], [V5] Class 5, [V6] Astro Class 6 (53 min), [VD1] Vikas – Demo class,
[VD2] Vikas Demo Class 2, [RRR] "RRR level file video on support and
resistance". Timestamps are transcript timestamps.

Vikas is a separate teacher from GRAHA MARKETS (Prediction tab) and
Saptarsh. His own framing [V1 @ 01:02–01:03, 01:17]: daily intraday
prediction of Nifty by astrology is "rubbish … brutally hammered by
market"; astrology is for **dates**, and the trade comes from the chart.
Every concept must be self-backtested: "if you get 80–90% accuracy note it
down, otherwise reject it" [V1 @ 17:51, 48:20]. He uses drikpanchang.com's
"upcoming planetary events" and planet sign/nakshatra transit tables
[V1 @ 00:00, 18:11], a GannZilla-style radix tool for stocks
[V6 @ 31:19], and TradingView charts.

## A. The core mechanic — "important dates" as candles  [V1 @ 01:42–28:14]

1. A planetary event (sign or nakshatra ingress of a planet; an aspect
   between a *big* planet — Jupiter, Saturn, Uranus, Neptune, Sun — and a
   *small* planet — Mars, Mercury, Venus — at 30° or 60° [V1 @ 47:20])
   gives an **important date**.
2. **Which day**: if the event is after market close, or on a
   Friday/weekend/holiday, take the **next trading day**, and after a
   Friday always Monday ("on Saturday-Sunday there may be another event
   you might not study") [V1 @ 19:52–20:22, 25:16–25:34].
3. **Which candle**: the date's daily candle. If that candle is an inside
   candle of a nearby bigger one, take the outside candle ("iron law")
   [V1 @ 03:12–04:07]. A very big candle is "not good for trade" — the
   market will range inside it [V1 @ 36:19–36:47; V6 @ 07:56].
4. **The trade**: the candle's high/low become the levels. High-cross →
   long, low-cross → short, opposite side is the stop. If the stop is
   hit on a *big* date the move is "wild on the opposite side … double
   your quantity, go blind" [V1 @ 04:46–05:33].
5. **Reversal dates**: when the date lands at a swing bottom/top, do not
   take the first move — wait for the retest of the candle
   [V1 @ 38:00–40:30]. Big dates (Mercury→Aries) trade on the break;
   small dates wait for the retest.
6. **Timing inside the day** [V6 @ 02:17–02:41]: breakouts happen in the
   first 1–2 hours; if the low-cross comes after 1–2 pm, skip it and wait
   for the next day.
7. A date's level keeps working as support/resistance for weeks
   ("this is the power of only one date") [V1 @ 21:33–22:36].

## B. Named date concepts with his claimed accuracy

| Concept | His claim | Examples cited | Tag |
|---|---|---|---|
| **Mercury enters Aries** (sidereal) | "big date"; the day's low is not closed below for months; 10–15% moves follow | 13 May 2025 low; 3 Apr 2023; 8/11 Apr 2022 | [V1 @ 04:29–05:49, 19:32–28:14] |
| **Sun enters Uttarashadha** (~11 Jan) | market does not fall that week; "95%" | 2021–2025 | [V1 @ 29:02–33:00] |
| **Sun enters Shravana** (~24 Jan) | bottom / support; Moon-lorded stars matter | 2021–2025 | [V1 @ 33:58–39:00] |
| **Sun enters Rohini** (~25 May) | minor top | 2024, 2025 | [V1 @ 41:56–43:40] |
| **Sun enters Hasta** (~27 Sep) | top — 27 Sep 2024 all-time high | 2024 | [V1 @ 46:04–46:55] |
| **Sun enters Dhanishta** (~6 Feb) | bearish 2–3 days | 2023–2025 | [V1 @ 49:06–51:26] |
| Sun-nakshatra dates repeat on the same calendar day each year, ±1 | | | [V1 @ 44:41–45:20] |
| **Mars enters Dhanishta** | bearish for metals (Hindalco); Mars = metals | 7 Mar 2024, 30 Mar 2022 | [V1 @ 52:03–58:34] |
| **Jupiter 30° Mercury** | bottoms | 13 May 2024 Nifty; 15 Jun 2024 BTC | [V1 @ 01:09:44–01:14:36] |
| **Moon at 45° / 135° / 225° / 315°** at market open | that day's high/low is important; "2–3 dates a year"; Moon "should be at 40–60°" at opening | 7 Sep 2000, 15 Nov 2000, 28 Sep 2000 (Gann-era examples) | [V6 @ 39:26–44:38, 48:28] |
| **Venus 45°** | same treatment; 11 May 2025 → 13 May bottom; 23 Jun 2025 | | [V6 @ 48:32–51:17] |
| Uranus–Venus 8° apart on the same day | stacked with the above | 13 May 2025 | [V6 @ 49:42] |
| "Saturn's-nakshatra swing date" | look for it at tops and bottoms | | [V6 @ 04:08–04:18] |

(The 45° concepts are stated without the reference body; Class 2–5 may
define it — treat as open until then.)

## C. The nakshatra-lord daily rule  [V1 @ 01:19:12–01:34:34]

- Each day belongs to the Moon's nakshatra and its lord. **Malefic lord**
  (Ketu, Saturn, Mars, Sun, Rahu) takes the market **up**; **benefic lord**
  (Jupiter, Venus, Moon; Mercury when alone/with benefics) takes it
  **down**. (Opposite of the usual reading — he is explicit.)
- If the day goes *against* its lord, the next day goes against its lord
  too ("this works 100%"). Condition: **the Moon must be in the same sign
  on both days**; if it changes sign, skip [V1 @ 01:25:10–01:26:30].
- **Saturn nakshatra → Mercury nakshatra**: if the market falls the whole
  session in a Saturn star (Pushya, Anuradha, Uttara Bhadrapada), the next
  day in the Mercury star (Ashlesha, Jyeshtha, Revati) reverses *at least
  half* of that leg, then falls again. "90–100%", "once in 2–3 months";
  requires the Saturn star to cover 09:15–15:30 and the Mercury star to be
  in from the open [V1 @ 01:27:40–01:34:34]. Example: 11–12 Feb 2025
  (Pushya → Ashlesha); 14 May 2025 (posted in advance).
- He promised the full treatment in the next class ("it will take the
  whole class") — see [V2].

## D. Technical layer (chart rules he pairs with the dates)

- **Measuring gap**: a gap between candle 1's low/high and candle 3's
  high/low (skip the middle candle) at the start of a leg; created by "big
  money"; becomes support/resistance; "until market is above 24,000 it
  cannot fall" was this [V1 @ 06:04–17:05; V6 @ 05:25–06:03].
- Never trade the break of a gap or a level — wait for the **retest**,
  then go with the direction [V1 @ 09:42–10:11; V6 @ 19:02–19:22].
- Trend is read on the **weekly** chart; daily for structure; 5-minute
  for intraday; 2–4 h frames are useless for a 6-hour market [V6 @ 26:56–29:02].
- After a big candle the market ranges for 4–5 candles — sell options;
  option selling on gap retests "safe and secure" [V6 @ 07:56, 09:19–16:39].
- First 5-minute candle high/low matters, but big first candles are
  unusable [V6 @ 46:53–48:11].
- Three-condition entry [V6 @ 25:35–25:53]: (1) at a support/resistance
  (gap or a level tested 3×), (2) the star/date is active, (3) its high or
  low has crossed. Book half, trail half.

## E. Stocks and sectors

- Sector lords: **Mars** metals (also property, power/energy), **Jupiter**
  banking, **Saturn** oil/energy (ONGC, Reliance), **Venus** luxury and
  finance, **Mercury** and **Rahu** IT [V1 @ 01:05:25–01:05:45; V6 @ 35:36–36:04].
- Stock radix: incorporation date *or* listing date as the natal chart;
  the sector planet's transit at conjunction / 30° / 60° to its natal
  position marks tops and bottoms; "4–5 companies is enough" [V6 @ 31:19–36:25].

## F. What is testable in this app

Computable from the ephemeris with the existing harness:
1. Sun nakshatra-ingress dates (all 27) → forward 1/3/5-day Nifty
   return and "does the week hold the ingress-day low" (his Uttarashadha
   claim), with the Monday/next-session shift.
2. Mercury sign ingresses (Aries in particular) → does the ingress-day
   low/high hold for 20/40 sessions.
3. Big×small planet 30°/60° aspects → tops/bottoms within ±2 days vs base.
4. Nakshatra-lord direction rule (malefic up / benefic down), the
   "opposite carries over" rule with the same-sign condition, and the
   Saturn→Mercury half-retrace rule.
5. Mars nakshatra ingresses vs the metal index.
Not computable without intraday data: the candle high/low-cross entries,
first-1–2-hour rule, gap/retest mechanics, Moon-45° at the open (needs
the reference body first).
