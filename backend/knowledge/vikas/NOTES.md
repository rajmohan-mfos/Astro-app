# Vikas — "Astro class" method (provenance notes)

Source: the user's YouTube playlist "Vikas astro class" (9 videos, Hindi +
Tamil + English, ~8.5 h), audio pulled with yt-dlp and transcribed with
`tools/transcribe.py --lang auto` into `C:\Users\hgkri\Downloads\vikas\
transcripts\`. Tags: [V1] Astro class 1 (2 h), [V2] Astro class 2 (1 h 15),
[V3] Astro class 3 (1 h 15), [V4] Astro class 4 (1 h 07), [V5] Class 5
(1 h 26), [V6] Astro Class 6 (53 min), [VD1] Vikas – Demo class, [VD2]
Vikas Demo Class 2, [RRR] "RRR level file video on support and
resistance". Timestamps are transcript timestamps. [VD1] and [RRR] are
still transcribing and are not in these notes yet.

Vikas is a separate teacher from GRAHA MARKETS (Prediction tab) and
Saptarsh. His own framing [V1 @ 01:02–01:03, 01:17; V2 @ 30:25]: daily
intraday prediction of Nifty by astrology is "rubbish … brutally hammered
by market"; people who "add 10–15 yogas and say 60% astrology, 40%
technical" are confused; astrology is for **dates** — "mark simple date,
game over" — and the trade comes from the chart. Every concept must be
self-backtested: "if you get 80–90% accuracy note it down, otherwise
reject it" [V1 @ 17:51, 48:20; V2 @ 01:10:31–01:12:21; V3 @ 01:14:08]. He
uses drikpanchang.com's "upcoming planetary events" and planet
sign/nakshatra transit tables [V1 @ 00:00, 18:11; V4 @ 00:01–01:46],
GannZilla (geocentric, Mumbai) for degrees [V2 @ 01:02:42; V4 @ 27:35], a
radix tool for stocks [V6 @ 31:19], and TradingView charts.

The engine that implements the computable part is `backend/app/vikas.py`;
the backtest is `backend/scripts/backtest_vikas.py` → `backend/knowledge/
backtest/vikas/RESULTS.md`; section G below summarises what it found.

## A. The core mechanic — "important dates" as candles  [V1 @ 01:42–28:14]

1. A planetary event (sign or nakshatra ingress of a planet; an aspect
   between a *big* planet — Jupiter, Saturn, Uranus, Neptune, Sun — and a
   *small* planet — Mars, Mercury, Venus — at 30° or 60° [V1 @ 47:20];
   a same-degree conjunction; a Moon position) gives an **important date**.
2. **Which day**: if the event is after market close, or on a
   Friday/weekend/holiday, take the **next trading day**, and after a
   Friday always Monday ("on Saturday-Sunday there may be another event
   you might not study") [V1 @ 19:52–20:22, 25:16–25:34; V2 @ 01:08:07].
   "Most of the time Mondays are important — three days of astro events
   land on one day" [V2 @ 01:08:23–01:09:02]. If a degree match completes
   after midday, the next day is the date [V2 @ 22:25–22:50].
3. **Which candle**: the date's daily candle. If that candle is an inside
   candle of a nearby bigger one, take the outside candle ("iron law")
   [V1 @ 03:12–04:07]. A very big candle is "not good for trade" — the
   market will range inside it [V1 @ 36:19–36:47; V4 @ 43:17; V6 @ 07:56].
4. **The trade**: the candle's high/low become the levels. High-cross →
   long, low-cross → short, opposite side is the stop. If the stop is
   hit on a *big* date the move is "wild on the opposite side … double
   your quantity, go blind" [V1 @ 04:46–05:33].
5. **Reversal dates**: when the date lands at a swing bottom/top, do not
   take the first move — wait for the retest of the candle
   [V1 @ 38:00–40:30; V2 @ 38:15–38:35]. Big dates (Mercury→Aries) trade
   on the break; small dates wait for the retest. "Don't short on
   bottom, don't buy on top" [V5 @ 01:01:06–01:01:26].
6. **Timing inside the day** [V6 @ 02:17–02:41]: breakouts happen in the
   first 1–2 hours; if the low-cross comes after 1–2 pm, skip it and wait
   for the next day.
7. A date's level keeps working as support/resistance for weeks
   ("this is the power of only one date") [V1 @ 21:33–22:36; V2 @ 01:15:21].
8. **Confluence**: two concepts on one date "becomes more powerful"
   (3 Mar 2025: Mercury–Rahu 0° + Moon in Mesha; 13 May 2025: Mercury→
   Aries + Venus–Uranus + Saturn star) [V2 @ 36:37–37:00; V3 @ 52:53].
9. **Find your own**: look at every top and bottom, list the events of
   the 3–4 days around it, keep the ones that repeat in 3–5 years of
   history [V2 @ 01:10:31–01:12:21; V3 @ 01:14:08–01:14:34].

## B. Named date concepts with his claimed accuracy

| Concept | His claim | Examples cited | Tag |
|---|---|---|---|
| **Mercury enters Aries** (sidereal) | "big date"; the day's low is not closed below for months; 10–15% moves follow | 7 May 2025 → 13 May low; 31 Mar 2023; 8/11 Apr 2022 | [V1 @ 04:29–05:49, 19:32–28:14; V2 @ 25:26–27:16] |
| **Every planet entering Aries** | "Mesha is very important for all planets — backtest every planet for every instrument"; Rahu in Mesha → IT tops/bottoms | | [V2 @ 51:33–52:12] |
| **Moon in Mesha** (both days of the ~2¼-day transit; count Meena too when Mesha falls on a holiday) | Nifty date; if the market is at a top / channel line do not go long, wait for the pull-back | 6–7 Jan 2025 top; 3–4 Feb; 3–4 Mar 2025 bottom; 1–2 Apr 2025 gap-down; 9–10 Apr 2024 top | [V2 @ 32:29–45:12, 51:17–53:14] |
| **Mercury conjunct Rahu or Ketu at the same degree** (same sign, 0°) | "perfect reversal in Nifty"; "this single concept is enough to recover your fees"; 2–4 dates a year | 30 Sep 2024 top; 3 Mar 2025 bottom; 20 Mar 2024 bottom; 11 Apr 2022 top (10% straight) | [V2 @ 00:01–28:27] |
| **Venus within 8° of Uranus, same sign** | "that day is important"; use it for buying only — once its high is crossed the market does not come back | 19 Apr 2021 bottom → 30%; 6 Jun 2022; 26 Jun 2025 "the big date I announced on Twitter — 30,000 if it crosses the high" | [V2 @ 01:04:26–01:15:38; V6 @ 49:42] |
| **Sun enters Uttarashadha** (~11 Jan) | market does not fall that week; "95%"; sell puts | 2021–2025 | [V1 @ 29:02–33:00; VD2] |
| **Sun enters Shravana** (~24 Jan) | bottom / support; Moon-lorded stars matter | 2021–2025 | [V1 @ 33:58–39:00; V2 @ 39:36–39:52] |
| **Sun enters Rohini** (~25 May) | minor top | 2024, 2025 | [V1 @ 41:56–43:40] |
| **Sun enters Hasta** (~27 Sep) | top — 27 Sep 2024 all-time high | 2024 | [V1 @ 46:04–46:55] |
| **Sun enters Dhanishta** (~6 Feb) | bearish 2–3 days | 2023–2025 | [V1 @ 49:06–51:26; V3 @ 53:07] |
| Sun-nakshatra dates repeat on the same calendar day each year, ±1 | | | [V1 @ 44:41–45:20] |
| **Mars in the 12th sign from Saturn** (the sign *before* Saturn's) | metal sector falls from that day; Saturn in an **even** sign (2,4,6,8,10,12) → big fall, **odd** sign → small fall "but it will come" | 6 Feb 2024 (Saturn Kumbha, odd) → Hindalco −10%, gap-down −16%; 8 Feb 2020 (Saturn Makara, even) → −50% | [V4 @ 01:57–15:12] |
| **Mars enters Saturn's sign** | rise from that day ("you caught the top and the bottom, money is double in both") | 22 Mar 2020 → 23 Mar bottom | [V4 @ 13:58–15:12] |
| **Mars enters Dhanishta** | bearish for metals (Hindalco); Mars = metals | 7 Mar 2024 (−6–7%); 30 Mar 2022; 11 Nov | [V1 @ 52:03–58:34; V4 @ 21:17–23:20] |
| **Jupiter & Venus in the same sign** | bullish while together; "the market did not close below the 13 May [2024] date" | Venus → Taurus 19/20 May 2024; the Aries 2023 case "confusing, avoid" | [V4 @ 15:16–21:12] |
| **Jupiter 30° Mercury** | bottoms | 13 May 2024 Nifty; 15 Jun 2024 BTC | [V1 @ 01:09:44–01:14:36] |
| **Sun conjunct Neptune** (same degree) | bullish; buy only, above the date's high; a gap-up may be booked at the measuring gap | 8/9 Mar 2020; 11 Mar 2021; 13 Mar 2022; 17 Mar 2023 | [V4 @ 55:26–01:02:30] |
| **Venus conjunct Ketu / Rahu** (same degree, same sign) | reversal; "written wrong in the pdf — backtest and fix it" | 28 Nov 2023; 17 Apr 2024 "nothing with Rahu" | [V4 @ 46:19–55:18] |
| **Moon at 45°** (also 135/225/315, and 270°) at the 09:15 open, geocentric tropical, within ~2–3° | "universal date" — the high/low matter; not a reversal call; not on a holiday; "we will get very less dates"; "half the dates fall on holidays" | 18 Aug 2022 top; 8 Nov 2022 bottom; 12 Jul 2023; 8 Aug 2023 top; 14 Mar 2024 top; 4 Jun 2024 election day | [V4 @ 29:12–46:00; V6 @ 39:26–44:38] |
| Moon at 270° | same treatment, "test it yourself" | | [V4 @ 01:04:20–01:05:05] |
| **Venus 45°** | 11 May 2025 → 13 May bottom; 23 Jun 2025 | read in the engine as the Sun–Venus separation crossing 45° (those dates sit at 43.9° / 44.4°); the Class 2 Venus–Uranus 8° rule is probably what he meant | [V6 @ 48:32–51:17] |
| Sun in Dhanishta + Moon in Mesha + Venus–Uranus | "these four dates gave 6,000 points of Nifty" | Jan–Feb 2025 | [V3 @ 52:08–53:30] |
| "Saturn's-nakshatra swing date" | look for it at tops and bottoms | | [V6 @ 04:08–04:18] |
| Venus in Bharani | "not bearish" — he checked and dropped it | | [V4 @ 26:48–27:33] |

## C. The nakshatra-lord rules  [V1 @ 01:19:12–01:34:34; V5 @ 24:01–01:22:11]

- Sequence of nakshatra lords, fixed: **Ketu · Venus · Sun · Moon · Mars ·
  Rahu · Jupiter · Saturn · Mercury** (each has three stars, nine apart:
  Ketu = Ashwini, Magha, Mula; Saturn = Pushya, Anuradha, Uttara
  Bhadrapada; Mercury = Ashlesha, Jyeshtha, Revati; …) [V5 @ 27:19–31:36].
- Natures [V5 @ 28:03–30:40]: Ketu, Sun, Mars, Rahu, Saturn **malefic**;
  Venus, Jupiter, Mercury **benefic**; the **Moon** is benefic only from
  Shukla Dashami to Krishna Panchami and malefic otherwise — "don't use the
  Sun–Moon combination, it is in the circle of benefic and malefic".
- **Direction** [V1; V5 @ 31:46–33:47]: a **malefic** lord takes the
  market **up** ("paap-graha brings scarcity; supply falls, rates rise"),
  a **benefic** lord takes it **down** (supply rises). Opposite to the
  usual reading — he is explicit.
- **The carry-over** [V1 @ 01:25:10–01:26:30; V5 @ 49:03–01:13:00]: what
  matters is not whether the lord "took" the market its way but the *next*
  day: if Ketu took the market up, Venus next day brings sideways or down
  — "no matter what, don't take a positive trade; 50% of your trade is
  done". Conditions: (1) consecutive trading days, no holiday between
  ("that is why you can use it 7–8 times a month at most"); (2) lords of
  opposite nature — Mars→Rahu, or Chitra→Swati (both malefic) cannot be
  used; (3) the **Moon in the same sign** on both days; (4) **no other
  planet changed sign** between the two 09:15 charts; (5) the market is
  still inside the first day's range — "overlapping candles"; once the
  range breaks, stop using it [V5 @ 01:13:24–01:21:45]. Trade: mark the
  first day's high, look for a short below it on 5-minute momentum, "hold
  one move and go"; stop above the high.
- **Saturn nakshatra → Mercury nakshatra** [V1 @ 01:27:40–01:34:34;
  V5 @ 47:05–48:11, 53:25–56:00]: if the market falls the whole session
  in a Saturn star, the next day in the Mercury star reverses *at least
  half* of that leg, then falls again. "100%, don't doubt it"; Pushya →
  Ashlesha is the best; Anuradha is the best single star for Nifty tops.
  Requires the Saturn star to cover 09:15–15:30 and the Mercury star to
  be in from the open. Examples: 11–12 Feb 2025; 13–14 May 2025; 10–11
  Jun 2025.
- "Monday is green, Tuesday is red" — a second condition he pairs with
  the natures [V5 @ 49:03–49:25].

## D. Moon-in-a-lorded-star dates  [V3 @ 00:00–20:00, 52:00–01:06:11; V5 @ 34:49–47:05]

- Moon in a **Saturn star** (Pushya / Anuradha / Uttara Bhadrapada) is an
  important date for **Nifty** and **Reliance** (Saturn = oil & gas, IT,
  "Nifty is Saturn"); **Jupiter stars** (Punarvasu / Vishakha / Purva
  Bhadrapada) for **Bank Nifty** and banking/finance; **Venus stars** for
  Bajaj Finance; **Mars stars** for Hindalco; **Ketu** (Ashwini) for
  Glenmark. Use all three stars of the lord; if one star tests better,
  use that one [V5 @ 45:19–45:27].
- The star must cover the market hours (≥ 4–5 h; 09:15–15:30 or
  10:30–15:30); if it starts after 15:30 the next day is the date; a star
  ending near the close makes the next day important [V3 @ 10:30;
  V5 @ 35:01–35:57, 45:59–46:08].
- **No Friday dates** ("Friday is useless"); a date is usable till that
  week's Friday unless a top/bottom formed; the next date comes ~9 days
  later; "one date a month goes into a holiday" [V3; V5 @ 59:56].
- At a **top**: trade only the reverse (low-break → short, never buy);
  at a **bottom**: high-break → buy, never short; in the middle: leave it
  [V5 @ 37:15–37:30, 46:25–46:53]. Combine with a resistance — a gap or a
  level tested three times — and alert the low in the trading app
  [V5 @ 37:36–40:34].
- Reference for the date: 13 May 2025 — Mercury→Aries + Venus–Uranus +
  Anuradha, "triple confluence" [V3 @ 52:53].

## E. Technical layer (chart rules he pairs with the dates)

- **Measuring gap / order block**: a gap between candle 1's low (or high)
  and candle 3's high (or low) at the start of a leg — "made by the
  operator", "sign of big money"; mark it only at the top/bottom of a leg
  or the start of leg 2 after a pull-back, once the market has made a new
  swing high; it is support/resistance until one or two candles close
  through it, then delete it [V1 @ 06:04–17:05; V2 @ 14:12–18:45;
  V4 @ 58:36–01:02:30; V5 @ 00:00–10:15, 42:26–44:45; V6 @ 05:25–06:03].
  In intraday use the 5-minute gap, the 15-minute one only if there is
  none; wait for the positive move off the gap before entering.
- Never trade the break of a gap or a level — wait for the **retest**,
  then go with the direction [V1 @ 09:42–10:11; V6 @ 19:02–19:22].
- **Channels and trend lines**: at the top of a channel do not go long
  even on a date; "seven trades from one channel, no astrology needed"
  [V2 @ 35:32–36:03, 40:25–45:12].
- **Flags**: pole → sideways flag → breakout on a date; target = pole
  height; if the market has to fall it falls in 3–4 days, a week of
  "time pass" is a flag [V3 @ 57:31–01:04:37].
- Trend is read on the **weekly** chart; daily for structure; 5-minute /
  15-minute for intraday; hourly/2–4 h frames are useless for a 6-hour
  market; the first-hour candle has its own probabilities
  [V3 @ 01:01:02–01:02:08; V6 @ 26:56–29:02].
- After a big candle the market ranges for 4–5 candles — sell options;
  option selling on gap retests "safe and secure" [V6 @ 07:56, 09:19–16:39].
- **Previous day's high/low** are always important — "if it had to cross,
  it would have done so yesterday"; overlapping candles = range
  [V5 @ 01:19:49–01:21:09].
- Three-condition entry [V6 @ 25:35–25:53]: (1) at a support/resistance
  (gap or a level tested 3×), (2) the star/date is active, (3) its high or
  low has crossed. Book half, trail half. Next-month options so the
  premium does not decay while the market passes time [V4 @ 40:17–40:41].
- **RBI policy day** [V5 @ 10:15–23:46]: nothing till 10:00; the first
  5-minute candle at 10:00/10:05 is a trap (a 5–10-second move) — trade
  the opposite side with that candle's extreme as the stop, 15-point
  risk; "100% in the last 8, 90% last year"; the rest of the day is
  sideways.

## F. Stocks and sectors

- Sector lords: **Mars** metals (also property, power/energy), **Jupiter**
  banking/finance, **Saturn** oil/energy (ONGC, Reliance, NTPC), IT and
  Nifty itself, **Venus** luxury and finance, **Mercury** and **Rahu** IT,
  **Ketu** pharma (Glenmark) [V1 @ 01:05:25–01:05:45; V5 @ 40:34–41:34;
  V6 @ 35:36–36:04; V2 @ 52:04–52:24].
- Stock radix: incorporation date *or* listing date as the natal chart;
  the sector planet's transit at conjunction / 30° / 60° to its natal
  position marks tops and bottoms; "4–5 companies is enough"
  [V6 @ 31:19–36:25]. Homework: each student picks a stock by the first
  letter of their name and finds its nakshatra [V3 @ 01:06:29–01:08:10].

## G. What was tested, and what it found  (`backtest/vikas/RESULTS.md`)

Everything computable from the ephemeris was run on Nifty 2011–2026
(3,848 sessions), Bank Nifty, Nifty Metal and COMEX gold/silver, each
rule against the same statistic on every other day. Summary:

| Rule | Result | Reading |
|---|---|---|
| Day-lord direction (malefic up / benefic down) | 49.8% on 2,808 clean sessions | coin. Saturn-star days close **down** 58% (p 0.001, 1 of 9 lords) — the opposite of his reading |
| Carry-over, his full conditions | 47.3% on 423 setups; "not beyond day-1 extreme" 63% vs 62% base | nothing |
| Saturn → Mercury half-retrace | 70.6% of 136 vs 68.8% for any down day | nothing |
| Date candles as breakout levels (25 families) | follow-through 52–60% vs 57.5% for any candle; range held 5 sessions ≈ 0% | no family's candle is a better level |
| Sun → Uttarashadha week holds the low | 6 of 16 years (base 31%) | no |
| Mercury → Aries low holds 60 sessions | 4 of 18 (base 18%) | no |
| **Mars in the 12th sign from Saturn → fall** | Nifty −5.2% mean over the transit, 8/11 down vs 35% base (p 0.02); Nifty Metal −4.0%, 8/11; even-sign Saturn −10.8% vs odd +1.4%; gold +2.3% (no) | the one lead; n = 11 |
| **Mars in Saturn's sign → rise** | Nifty +7.5% mean, 11/11 up vs 65% base (p 0.01), both halves; Nifty Metal +8.2% | the one lead; n = 11 |
| Moon at 45/135/225/315° (tropical) at the open | follow-through 64% vs 57.5% (n 281, p 0.03); sidereal 55% | 1 of ~25 families — chance |
| Mars in Dhanishta → metals fall | gold +0.9%, silver +3.1%, Metal −0.7% | no |
| Jupiter & Venus one sign → bullish | +0.1% over 26 spans vs +0.8% | no |
| Monday green → Tuesday red | 58% vs 55.5% | no |

Not testable without intraday bars: the high/low-cross entries with the
candle's other side as stop, the first-1–2-hour rule, gap / order-block
retests, flag targets, the RBI-day fade, stock radix dates.

## H. Open items

- [VD1] Vikas – Demo class and [RRR] "RRR level file video" are still
  transcribing; fold them in when done (RRR is the Twitter handle he
  says learned the Moon-sign stock concept from him [V2 @ 57:30–01:01:46]).
- "Venus 45°" in [V6] is ambiguous; both readings are in the backtest and
  neither shows anything.
