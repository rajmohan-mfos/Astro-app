// "Saptarsh Insight channel" — a study tab for a new astrologer, with a
// computed week-ahead outlook on top (SaptarshWeek).
//
// Source: a screen recording (28 Aug 2026) scrolling through the
// "Saptarsh Insight" Telegram channel, a daily market-astrology bulletin
// for Nifty, Gold and Silver. The recording had no narration, so every
// concept below is read off the posts themselves (14–28 Aug 2026). The
// channel's interpretations are reported as THEIR practice — nothing
// here has been backtested by this app, and the app's own 5-year audit
// of the taught GRAHA MARKETS method found no edge. Study material.

import SaptarshWeek from './SaptarshWeek'
import SaptarshBacktest from './SaptarshBacktest'

type Tone = 'bull' | 'bear' | 'vol' | 'neutral'

const TONE_LABEL: Record<Tone, string> = {
  bull: '▲ Bullish', bear: '▼ Bearish', vol: '⇅ Volatile', neutral: '— Neutral',
}

function Tag({ tone }: { tone: Tone }) {
  return <span className={`learn-tag learn-tag-${tone}`}>{TONE_LABEL[tone]}</span>
}

// ---------------------------------------------------------------- data

const PANCHANG_FIELDS: [string, string][] = [
  ['Sunrise / Sunset', 'The Vedic day runs sunrise to sunrise. Everything else on the sheet is measured from sunrise.'],
  ['Tithi + ends', 'Lunar day (Shukla = waxing, Krishna = waning). Purnima / Amavasya days are flagged separately — see Full Moon below.'],
  ['Nakshatra + ends', 'The Moon\'s star. THE key field: the bulletin\'s base bias for the day comes from the Moon\'s sign + nakshatra during trading hours, and "Nakshatra ends" is quoted as a change-of-character time (e.g. "Anuradha till 11:53 IST then Jyeshtha").'],
  ['Yoga + ends', 'One of 27 nitya yogas (Indra, Vaidhriti, Shobhana, Sukarma, Ayushman …). Vaidhriti and Vyatipata are the classically inauspicious ones.'],
  ['Karana + ends', 'Half-tithi (Bava, Balava, Kaulava, Taitila, Gara, Vanija, Vishti …). Vishti (Bhadra) is singled out: "Strong bearish Vishti yog is active during the entire session" (27 Aug).'],
  ['Rahu Kaal', 'A ~90-minute daily window that moves with the weekday. Channel note: "RahuKaal — many times markets show weakness during this time."'],
  ['Yamaganda', 'Second inauspicious window of the day, also weekday-based.'],
  ['Gulika Kaal', 'Third inauspicious window (Saturn\'s portion of the day).'],
  ['Abhijit Muhurat', 'The auspicious ~50 min around local noon (≈12:17–13:08 in late August, Mumbai).'],
]

const POSITION_COLS: [string, string][] = [
  ['Planets', 'ASC (lagna) first, then Sun…Pluto. [R] = retrograde, [C] = combust (too close to the Sun).'],
  ['SIGN', 'Sidereal rasi. Cells are shaded red when the planet sits at a dignity extreme — observed: Jupiter in Cancer (exalted), Moon in Scorpio (debilitated), Uranus in Taurus (fall), Mercury in Cancer (enemy sign). Green = ordinary placement.'],
  ['DEGREE', 'Absolute sidereal longitude 0–360°. Aspects (below) are angles between two of these numbers.'],
  ['D-M-S', 'Degrees-minutes-seconds within the sign (000°–029°59\'59").'],
  ['Star (Pada)', 'Nakshatra and its quarter, 1–4. The pada sets the navamsa sign.'],
  ['NavSign', 'Navamsa (D-9) sign — used in the transit table\'s interpretation.'],
  ['SPEED', '°/day. Negative = retrograde. Moon ≈ 12–13, Sun ≈ 0.96, Mercury 1.9–2.0 when fast.'],
  ['LATTI', 'Ecliptic latitude — how far above/below the Sun\'s path.'],
  ['DECL.', 'Declination — distance from the celestial equator. Watched by Western financial astrologers for "parallel" contacts.'],
]

const ASPECTS: [number, string, string][] = [
  [0, 'Conjunction', 'Sun 0 Mercury (27 Aug 22:35) → Bullish; Moon 0 Mn Node (27 Aug 23:41) → Bearish'],
  [45, 'Semi-square', 'Moon 45 Saturn → Bearish; Moon 45 Neptune → Bearish; Moon 45 Mn Node → Bearish / Volatile'],
  [60, 'Sextile', 'Moon 60 Saturn (26 Aug 17:53) → Bullish; Venus 60 Jupiter; Sun 60 Moon'],
  [90, 'Square', 'Moon 90 Saturn → Bearish / Volatile; Moon 90 Venus → Bearish; Moon 90 Uranus → Bearish'],
  [120, 'Trine', 'Moon 120 Venus → Bullish; Moon 120 Uranus → Bullish; Moon 120 Jupiter'],
  [135, 'Sesquiquadrate', 'Moon 135 Mercury → Bullish; Sun 135 Moon → Bullish; Moon 135 Mars → Bullish; Moon 135 Uranus → Volatile'],
  [150, 'Quincunx', 'Sun 150 Pluto → Bearish; Sun 150 Neptune → Bullish; Mercury 150 Pluto / Neptune → Volatile; Moon 150 Jupiter → Bullish'],
  [180, 'Opposition', 'Moon 180 Jupiter → Bearish; Moon 180 Mercury → Neutral; "Mercury 180 Rahu will create unclear trend … traders may get confused"'],
]

const KARAKAS: [string, string, string][] = [
  ['AK', 'Atma karaka', 'highest-degree planet — Rahu on 24 Aug'],
  ['AmK', 'Amatya karaka', 'Venus'],
  ['BK', 'Bhratru karaka', 'Saturn'],
  ['MK', 'Matru karaka', 'Jupiter'],
  ['PiK', 'Pitru karaka', 'Mars'],
  ['PK', 'Putra karaka', 'Moon'],
  ['GK', 'Gnati karaka', 'Sun'],
  ['DK', 'Dara karaka', 'Mercury (lowest degree)'],
]

// Every Moon placement the channel wrote a Nifty bias for, in the window
// recorded. Same nakshatra can carry a different call on a different
// day because yogas and aspects are layered on top.
const MOON_CALLS: [string, string, string, Tone, string][] = [
  ['19 Aug', 'Libra', 'Vishakha', 'bull', 'slightly positive; volatile till 10:00, sluggish after 14:00'],
  ['20 Aug', 'Scorpio', 'Anuradha', 'bear', 'Moon debilitated — bearish; bearish yog opening→13:00, Saturn–Moon aspect "keeps the market in check"'],
  ['21 Aug', 'Scorpio', 'Anuradha → Jyeshtha 11:53', 'bull', 'both supportive; weakness possible till 11:40, bullish after — "avoid short after 11:40"'],
  ['24 Aug', 'Sagittarius', 'Purvashadha', 'bull', 'bullish; weakness/volatility opening→10:30, bullish yog 10:30→15:00'],
  ['25 Aug', 'Capricorn', 'Uttarashadha → Shravana 22:52', 'vol', 'Mercury 180 Rahu = unclear trend; positive till 13:00, Saturn aspect bearish after'],
  ['26 Aug', 'Capricorn', 'Shravana', 'neutral', 'neutral; bearish yog opening→09:45, range with positive bias 09:45→14:00, bearish after'],
  ['27 Aug', 'Capricorn → Aquarius 13:36', 'Dhanishta', 'bull', 'bullish BUT Vishti karana all session → "very careful following bullish trend"; 13:30→15:30 bearish yog'],
  ['28 Aug', 'Aquarius', 'Shatabhisha', 'bear', 'bearish; Full Moon + lunar eclipse same day → "we are not confident … be careful"; 13:00 pivot'],
]

const CONJUNCTIONS: [string, string, string, string][] = [
  ['Pisces', 'Saturn, Neptune', '11-May-26 → 15-Mar-27', '10.1 months'],
  ['Cancer', 'Sun, Mercury, Jupiter', '05-Aug-26 → 17-Aug-26', '12 days'],
  ['Leo', 'Sun, Ketu', '17-Aug-26 → 22-Aug-26', '5 days'],
  ['Cancer', 'Mercury, Jupiter', '17-Aug-26 → 22-Aug-26', '5 days'],
  ['Leo', 'Sun, Mercury, Ketu', '22-Aug-26 → 07-Sep-26', '16 days'],
]

const DIARY: [string, string][] = [
  ['Aug 27 17:06', 'Mercury in superior conjunction, 1°45\' N of Sun'],
  ['Aug 27 18:46', 'Moon in ascending node'],
  ['Aug 28 04:18', 'FULL MOON, lunar eclipse'],
  ['Aug 28 22:18', 'Uranus in square with Sun'],
  ['Aug 30 12:50', 'Neptune 4°.9 S of Moon'],
  ['Aug 31 08:07', 'Saturn 7°.0 S of Moon'],
  ['Sep 2 17:40', 'Moon greatest latitude N 5°12\''],
]

const APP_MAP: [string, string, boolean][] = [
  ['Panchang table (tithi, nakshatra, yoga, karana + end times)', 'Prediction tab → Panchang tiles; Panchang chart (KP) tab', true],
  ['Planet positions (sign, degree, star/pada, navamsa, speed)', 'Rasi chart (Lahiri) tab → Grahas table', true],
  ['Rahu Kaal / Yamaganda / Gulika / Abhijit windows', 'Week outlook above (per day, click to expand); Horai timeline covers the hour-lords', true],
  ['Timed planet-to-planet aspect table', 'Week outlook above — every exact aspect with IST and ET; the taught method uses the chain (X/X1/Y/Y1) instead', true],
  ['Metals trading windows IST / ET', 'Week outlook above, 03:30 → 27:30 IST split at each aspect', true],
  ['Vaar-Tithi yoga', 'Week outlook above — classical tables standing in for their unpublished one', true],
  ['Conjunction calendar / Jupiter transit history', 'Week outlook "Regime" block; Gann cosmogram tab for audited dated events', true],
  ['Jaimini chara karakas', 'Not in the app', false],
  ['Moon nakshatra → base bias', 'Prediction tab → day score (panchang tally) is the taught-method analogue', true],
  ['Volatility band (no astrology)', '/vol in the Telegram bot', true],
]

// ---- second learning pass: the X account @sonisunil59 (28 Aug 2026)

const REPORT_ANATOMY: [string, string][] = [
  ['Vedic Day (Tithi)', '"Ashadha Vad-12 continue till 16:38 IST then Vad-10 till 28:55" — lunar month + Sud (Shukla) / Vad (Krishna) + tithi number, with the switch time. Amavasya and Purnima are called out by name.'],
  ['Moon', 'Sign with its continuation time and, in the later format, a bias chip next to it ("Cancer — Bias-Bearish").'],
  ['Nakshatra', 'Current and next star with switch times in IST and ET, each with a bias chip.'],
  ['Astro. Events', 'The day\'s exact aspects with times ("Mercury 150 Rahu 05:07, Venus 120 Pluto") plus named yogas: Vaar-Tithi yog, Vaidhriti yog, "Today is Amavasya".'],
  ['Astro. Interpretations', 'One paragraph: nakshatra favourable or not, which planets are bullish, which aspect can "create bearish price action".'],
  ['Metal-wise outlook', 'Gold and Silver separately, each headed Bullish / Bearish / Bullish-Bearish / Cautiously bullish / Bearish with caution, with a paragraph of instruction.'],
  ['Trading Windows IST / (ET)', 'Three or four windows from 03:30 IST to ~27:30 IST (next 03:30), each with Bias-Bullish / Bearish / Neutral and a sentence on what to do in it. The clock runs past 24:00 the Vedic way.'],
]

const X_RULES: [string, string, string][] = [
  ['Amavasya', 'bullish for gold & silver', '14 Jul: "Today is Amavshya, this is considered bullish for gold and silver."'],
  ['Purnima', 'turning point / bottom trigger', '29 Jul: "Full Moon can be trigger and form bottom. Stay cautious."'],
  ['Vaidhriti yog', 'volatility with a bullish bias', '27 Jul and 2 Jul, both times for metals.'],
  ['Vaar-Tithi yog', 'bullish or bearish for the day', '28 Jul "is bullish", 27 Jul "is bearish" — the weekday × tithi table they use is not published; the app substitutes the classical Siddha / Mrityu / Dagdha / Visha / Hutasana tables and labels them "classical".'],
  ['Sun–Jupiter contacts', 'read both ways on metals', '27 Jul "Sun–Jupiter become bullish for precious metals"; 10 Aug "Jup–Sun aspect can create bearish price action"; 15 Jul "powerful bearish combination of Jupiter-Sun and Venus".'],
  ['Venus–Rahu aspect', 'moves silver', '29 Jul: "Venus–Rahu aspect will affect the silver significantly."'],
  ['Mars–Rahu aspect', 'neutral, confusing', '18 Aug (Nifty): "As Mars-Rahu is neutral, it would be confusing price action."'],
  ['Mercury retro conjunct Sun', 'stock markets turn bullish', 'Jul 12, quoting a classic: "If Mercury is retro and conjunct with the Sun, stock markets turns bullish."'],
  ['Jupiter changing nakshatra', 'bullish for stocks', '19 Aug: "Jupiter … enters in Ashlesha nakshatra. This is considered bullish for stock markets."'],
  ['Jupiter in sidereal Cancer', 'weak phase for silver', 'Jul 2 table of every Cancer transit since 1978 with gold % / silver % — silver negative in 3 of 5.'],
  ['Sun + Ketu in Leo', 'analog of the Aug 2025 metals rally', 'Aug 15: "17 Aug 2025 & 17 Aug 2026, Sun+Ketu in Leo. Almost same chart … could we see similar bullish phase?"'],
  ['Special weekly yog', 'up to 3% fall', 'Jun 28: "Strong bearish yog is starting from Monday midnight. Many times in past, this yog created up to 3% fall."'],
]

const METAL_NAK: [string, string, string][] = [
  ['Ashwini', 'slightly bullish', '15 May, 8–9 Jul'], ['Bharani', 'bearish', '15 May, 9 Jul'],
  ['Mrigashira', 'bullish', '19 May'],
  ['Krittika', 'bullish', '4 Dec 2025'],
  ['Rohini / Ardra', 'not favourable for higher prices; Rohini bearish, Ardra bearish', '4 Dec 2025, 30 Jan, 19–20 May, 10 Aug'],
  ['Punarvasu', 'bearish', '23 Apr, 20 May, 14 Jul'], ['Pushya', 'bullish (23 Apr, 21 May); bearish once (15 Jul) — majority bullish', '23 Apr, 21 May, 15 Jul'],
  ['Ashlesha', 'neutral', '15 Jul'], ['Hasta', 'bearish', '20 Jul'],
  ['Uttara Phalguni', 'bullish', '14 Nov 2025'],
  ['Chitra', 'bullish', '20 Jul'], ['Swati', 'bearish (18–19 Nov 2025); both sides (18 Aug) — majority bearish', '18–19 Nov, 18 Aug'],
  ['Vishakha', '"not much supportive" (19 Nov 2025); both sides (19 Aug)', '19 Nov, 19 Aug'],
  ['Anuradha → Jyeshtha', 'Anuradha bullish (6 Apr, 4 May), Jyeshtha neutral (8 Jul 2025) / bearish (4 May); both sides 21 Aug — majority: Anuradha bullish, Jyeshtha mixed', '8 Jul 2025, 6 Apr, 4 May, 21 Aug'],
  ['Mula', 'bullish (27 Oct 2025, 8 Apr, 2 Jun); bearish once (27 Jul) — 3 of 4 bullish', '27 Oct 2025, 8 Apr, 2 Jun, 27 Jul'], ['Purvashadha', 'bearish / slightly negative', '2–3 Jun, 28 Jul'],
  ['Uttarashadha', 'bullish', '2 Jul, 28–29 Jul, 25 Aug'],
  ['Shravana', 'bearish', '2 Jul, 29 Jul'], ['Dhanishta', 'bullish', '27 Aug'],
  ['Shatabhisha', 'bearish', '20–21 May 2025, 11 Aug 2025, 8 Jun, 28 Aug'], ['Purvabhadra', '"not supportive" (21 May 2025), bearish (11 Aug 2025); bullish once (8 Jun 2026) — majority bearish', '21 May 2025, 11 Aug 2025, 8 Jun'],
  ['Uttarabhadra', 'bullish / slightly bullish', '16 Apr, 10 Jun, 7 Jul'],
  ['Revati', 'bearish (10 Jun, 7–8 Jul); "neutral" once (16 Apr)', '16 Apr, 10 Jun, 7–8 Jul'],
]

const POSITION_RULES: string[] = [
  '"You must have stoploss order for position that goes in opposite side." — every window carries it.',
  '"Must book profit in that spike" — bullish windows are for taking, not holding: "sharp spike to higher side … do not create any new position."',
  '"Do not carry any long position" into a bearish next day (13 Jul); "avoid unnecessary risk of overnight positions."',
  'Investing: "buy in parts rather than all at once"; "at least 25% must be allocated" when both metals are down (7–8 Jul).',
  'Event days override the sky: "At 23:30 IST FED will give its rate decision … we are bullish but in past we failed during these events, so please do not take risk."',
  '"Timing matters" — a temporary move against the call is not a failed call if the window had not opened yet (10 Aug).',
]

// ---- third learning pass: X posts of 23 Apr - 18 Jun 2026 (may.mp4)

const MAY_CONCEPTS: [string, string, string][] = [
  ['Sun–Moon aspect windows', 'A Sun–Moon hard aspect is read as a multi-hour bearish WINDOW, not a moment: "Moon-Sun 08:00 to 21:15 IST — strong bearish aspect can create sharp downfall"; "Sun-Moon strong bearish aspect starts from 16:30"; "Moon-Sun bearish aspects run till 11:00".', '3 Jun, 4 May, 20 May'],
  ['72° quintile', 'Their angle set includes the quintile family: "Sun 72 Moon — 02:36 IST — Bias strong bearish". The outlook now scans 72° and 144° too.', '10 Jun'],
  ['Ingress events', 'Sign and nakshatra entries are listed as "Important Astro. Event" with a reading: Jupiter → Cancer "very important, can affect the market heavily for long term … bearish last Oct, careful for few days"; Venus → Ardra "bearish for Silver"; Mercury → Ardra "slightly bearish"; Venus → Cancer "bullish for Silver but not immediately"; Sun & Mercury → Taurus "trend changer but not for metals".', '2 Jun, 20 May, 8 Jun, 15 May'],
  ['Nakshatra + Vaar', 'A second weekday yoga, on the Moon\'s star: "Combination of Nakshatra and Vaar is bullish" (Thursday + Pushya = classical Sarvartha Siddhi and Amrita Siddhi). The outlook uses the classical Sarvartha / Amrita / Yamaghanta / Mrityu tables.', '21 May'],
  ['Vyatipata Mahapat yog', 'Read as BULLISH for metals ("Vyatipat Mahapat yog is running from 20:05 to 01:14 IST, this is also bullish") — the opposite of its classical inauspicious label. The outlook now applies bullish for metals, volatile for Nifty.', '21 May'],
  ['Active planets', '"Active planets are Venus, Jupiter, Saturn" — the bodies making an exact aspect that day; "Active planets are Jupiter, Sun, Mars — this will create high volatility and sharp moves." Listed per day in the outlook.', '10 Jun, 26 May'],
  ['Conditional yog', '"Bias — IF bearish it may continue / bullish it may continue. If prices go any direction and hold for 15–20 min, it may continue till the window ends"; "If prices continue to drop after 09:30 IST, it may continue for a day."', '10 Jun'],
  ['No-yog windows', '"No bullish or bearish yog present … better to use technical levels"; "Much depends on medium-term yogas and Nakshatra\'s strength" — the nakshatra is the fallback when nothing else is exact.', '3 Jun, 10 Jun'],
  ['Weekly / medium-term yogs', 'Dated multi-day calls: "Note the date 07 May 2026 — strong bearish yog for stock markets worldwide, sharp correction" (ended Sun 10 May, "Monday afternoon its all effect will end"); "A significant planetary shift starts today (1 May) — one-way move, trade with the trend"; "Mars, Mercury and Saturn will not allow markets to rise" (23 Apr).', 'Apr–May'],
  ['Pivotal time (Nifty)', '"12:00 IST — Important pivotal time. Watch for + or − 10 min. Bias is positive." An exact aspect time is quoted as a ±10-minute pivot for Nifty — the same idea as the session timers in the outlook.', '1 Apr'],
  ['Majority reading', 'The same nakshatra gets different calls on different days (Pushya bullish 23 Apr and 21 May, bearish 15 Jul). The outlook uses the majority call and shows the dates; the day\'s aspects and "yogs" clearly outrank the star in his verdicts.', 'Apr–Jul'],
  ['Ingress readings (April)', 'Venus → Bharani "bearish"; Mars → Uttarabhadra "bullish for gold and silver"; "many important changes in planetary placement today may bring volatility" (17 Apr, Sun and Mercury moving).', '6 Apr, 17 Apr'],
  ['Timing convention (origin)', '25 May notice: "we will continue to count beyond 24:00 till the Sun rise time … 25:00 IST (24:00+01:00). Eastern Time will be written as it is." CME Globex hours quoted: Sunday 04:30 IST → Saturday 03:30 IST.', '25 May'],
]

const MEDIUM_TERM_LOG: [string, string, string][] = [
  ['23 Apr', 'Stocks', '"Still fragile … Mars, Mercury and Saturn will not allow markets to rise. More pain in near future."'],
  ['28 Apr', 'Metals', '"Placements and aspects are not supporting bulls — this phase may last longer than expected."'],
  ['1 May', 'Global', '"Significant planetary shift starts today … one-way move. Trade with the trend."'],
  ['6–7 May', 'Stocks', '"From 07 May strong bearish yog … sharp correction" → 8 May Nifty −122 "exactly in line"; yog ends Sun 10 May.'],
  ['13 May', 'Both', '"Nifty — bottom is quite low. Gold and silver — new high? Not so soon." (re-affirmed 8 Jun)'],
  ['28 May', 'Metals', '"Any bounce would be dead cat bounce … resume uptrend in 3–4 …" (re-affirmed 8 Jun)'],
  ['10–11 Jun', 'Both', '"Gold nearing the 23 March 2026 low"; "still more pain for bulls" (Nifty).'],
  ['17 Jun', 'Metals', '"Gold and Silver dropped hard after FED interest rate decision to unchanged."'],
]

// ---- fifth learning pass: X posts of Nov 2025 - Jan 2026 (Nov 2025.mp4)

const NOV_CONCEPTS: [string, string, string][] = [
  ['Planet "states"', 'Each report names which planets are bullish or bearish that day: "Jupiter and Mars are bullish while Moon and Rahu are bearish" (30 Jan); "Sun, Saturn and Jupiter is bullish" (18 Nov); "Jupiter–Saturn is neutral" (19 Nov); "after 12:30 IST the Sun become bullish" (8 Apr). The rule behind a planet\'s state is not stated — it reads like the planet\'s current aspects and nakshatra.', 'Nov–Jan'],
  ['Nakshatra stellium', '"Sun+Mercury+Venus are in Shravan nakshatra from 26-1-26 to 28-1-26. From 29 Jan there are four planets in Shravan … bullish with high volatility. Very large gap up or gap down is possible." Computed in the Regime block (≥3 planets in one star).', '26 Jan'],
  ['Same-stellium analog', 'Sun+Mars+Venus(+Mercury) in Sagittarius, Dec 2025 = Dec 1993 (the only such event since 1970). Gold topped 5 Jan 1994, five days before Mercury separated; "Venus will leave the stellium on 13 Jan 2026 — will the bullish trend continue till 13 Jan?" The method: find the last identical stellium and read what prices did as it broke up.', '~5 Jan'],
  ['Early-degree cluster', '"Many planets today are below 10 degrees. This is unusual" (8 of 12 on 21 Jan) — "all financial markets are showing extreme, may be this is the reason". Computed in the Regime block (≥6 bodies under 10°).', '21 Jan'],
  ['Rahu–Ketu axis history', 'Rahu in Leo / Ketu in Aquarius (1979–80, 2016–17): explosive top then heavy correction. Ketu in Leo / Rahu in Aquarius (1997–99, 2006–08): sharp sell-off / weakness then breakout. Now Rahu Aquarius / Ketu Leo: "vulnerable to sharp corrections after reaching key resistance zones." Regime block flags the axis.', '6 Jan'],
  ['Sun–Pluto conjunction', '"Sun and Pluto at 0° this week. Stay cautious. Many times tops and …" — read as a top-risk signal for metals (20 Jan). In the outlook as an observed bearish aspect.', '20 Jan'],
  ['Jupiter transit by pada', 'A table of Jupiter\'s move through Aries by nakshatra and pada with the % gold/silver change in each cell, retrograde stretches highlighted — the pada-level version of the Jupiter-in-Cancer table.', '6 Jan'],
  ['Mercury station → banking', '"Mercury is reducing its speed and going to retrograde on Sunday night. BankNifty may get affected more." Stations of Mercury..Saturn are now listed as astro events.', '6 Nov'],
  ['Jupiter sign change → banking', '"Jupiter changing sign today, enters in Mercury\'s sign, difficult to predict. Something big in Banking sector."', '5 Dec'],
  ['Make-or-break time (Nifty)', '"Important time for Nifty – 11:30 IST. Make or break time. Any direction after this time may last till closing" (19 Nov); "12:30 IST, very important time. Weakness is possible after" (12 Dec); "sell off after 10:45" ; "weakness after 13:30 … sudden drop" (6 Nov); "stay cautious after 11:00" (22 Jan).', 'Nov–Jan'],
  ['Moon–Ketu = Moon 180 Rahu', '"Moon-Ketu at 0° at 09:22 IST is bullish. Do not short till this time" (14 Nov) — while Moon 0 Rahu is bearish (27 Aug). The nodal axis flips the reading.', '14 Nov'],
  ['Sun–Moon window, again', '"Moon-Sun aspect is strong from 12:10 IST till closing. This can create strong move any side, but we are biased to lower side" (14 Nov); "Sun-Moon aspect can create one side move today. In past this aspect created sudden fall" (4 Dec).', 'Nov–Dec'],
  ['He trades it', 'Option fills posted 4 Dec: NIFTY 26000 CE bought 09:25 @211.50, sold 10:42 @281.15; 26000 PE sold 13:53 — "I also trade as per my astrological analysis."', '4 Dec'],
]

const NOV_LOG: [string, string, string][] = [
  ['4 Nov 2025', 'Metals', '"Bullish time is starting now. Be careful in short."'],
  ['14 Nov', 'Metals', 'Report: Moon–Sun strong from 12:10, "biased to lower side" → seller circuit in gold & silver that day (hit, reposted).'],
  ['17 Nov', 'Metals', '"Stay cautious in short now. This is for intraday."'],
  ['19 Nov', 'Nifty', '"11:30 IST make or break; any direction after may last till closing."'],
  ['26 Nov', 'Nifty / Gold', '"Be careful in following bullish trend … spikes 10:00–14:00"; "Gold at imp level in triangle."'],
  ['4 Dec', 'Metals', 'Report: no bullish yog, strong bearish 09:30–15:00 → "seller circuit"; "everyone is bullish on precious metals. We are not."'],
  ['11–12 Dec', 'Nifty', '"Both directions … little weak"; "12:30 very important time, weakness after".'],
  ['22–29 Dec', 'Both', '"Nifty up 200, made a bottom? Expecting good rally"; "Both metals in free fall. Stay away if bullish"; "Big move going to start in new year."'],
  ['2 Jan 2026', 'Nifty', '"Anticipate a positive movement, expecting an upward shift of over 3%. Avoid short."'],
  ['20–22 Jan', 'Both', '"Gold and silver may be in final phase of bullish trend? Sun and Pluto at 0°"; "Nifty weakness after 11:00."'],
  ['26 Jan', 'Metals', 'Week note: Sun–Jupiter 160°, Mars→Shravana, four planets in Shravana — "bullish with high volatility".'],
  ['30 Jan', 'Metals', 'Report: weak bearish 09:00–16:30, strong bearish 16:30–22:00, STRONG BULLISH 22:00–24:00 → silver fell ~50% retrace ("unexpected free fall"); replies: "your prediction time frame was off, it was over 22pm ist, price keeps falling" — a MISS on the last window, reposted anyway.'],
]

// ---- sixth learning pass: X posts of Jul - Oct 2025 (August 2025.mp4)

const AUG_CONCEPTS: [string, string, string][] = [
  ['Grand trine', '"Mars, Jupiter and Saturn forming grand trine from Monday. One way …" — a three-planet 120° triangle read as a one-directional move (gold and silver fell hard on 27–28 Oct). Computed in the Regime block, 6° orb.', '26 Oct 2025'],
  ['Transition point dominates', '"Mars enters in Scorpio at 13:28 IST. This is strong bearish for precious metals for 1–2 days … MARS AT TRANSITION POINT AND SOME TIMES STRONG BEARISH TREND FOR 1–2 DAYS. IT MAY DOMINATE all bullish yog." A slow planet\'s sign change outranks the intraday yogs.', '27 Oct'],
  ['Mars 120 Jupiter is bearish', 'A soft angle read bearish — "Jupiter will aspect the Mars and it will also create 120° angle. This is also bearish." The Moon\'s trines are bullish in his system; planet-to-planet trines are not automatically so.', '27–28 Oct'],
  ['Mercury direct → reversal', '"With Mercury turning direct on 11 Aug and Mars shifting Nakshatra, the stars point to a possible reversal … 14 August 2025" → Nifty +350 on 18 Aug. Stations of either kind are now listed as astro events with this reading.', '9 Aug'],
  ['Sun + Mercury ingress', '"Sun ingress Virgo (sidereal) on 17 Sept, conjunct with Mercury. Powerful combination for stock market. BANKNIFTY may outperform. Avoid short."', '15 Sep'],
  ['Jupiter → Cancer', '"Sidereal Jupiter enters Cancer, its exalted sign. Major change in markets" (18 Oct); Telegram the same week: "MAJOR TURNING POINT TOMORROW AFTER 12:00 IST FOR GOLD AND SILVER. AVOID LONG" → 17 Oct sell-off (reposted 28 Oct).', '16 Oct'],
  ['Weekly bearish yog for stocks', '"Strong bearish yog is starting from Tuesday. It has capacity to push Mkt 500/600 points lower" (5 Oct) — then "This is possibility not sure shot" (8 Oct). "Planetary alignments indicate huge move is coming. High probability for sell off" (16 Jul) → Nifty −500 by 1 Aug.', 'Jul–Oct'],
  ['Make-or-break times', '"Important time to watch 12:45 IST" (Aug); "11:30 IST" (12 Aug, hit); "Avoid short after 10:45" (25 Aug, hit); "Bullish time starts after 10:30" (3 Sep, +100); "favorable for bulls after 9:45" (5 Sep); "11:50 IST, cautious after" (12 Sep); "Sharp move after 13:30, upside" (17 Sep); "may change direction after 13:00" (30 Oct — "Failed").', 'Aug–Oct'],
  ['His own terms', '22 Sep T&C: "Our reports should be considered supportive, akin to technical analysis … We provide only bullish or bearish time or reversal … We do not guarantee 100% accuracy … Use technical analysis simultaneously … always utilize stop-loss."', '22 Sep'],
  ['Service history', '"Nifty analysis will start only after getting higher accuracy. Gold and silver analysis is available at present" (Aug 2025) — the Nifty bulletin came later than the metals report.', 'Aug'],
  ['Posts that failed', 'He also posts misses: "Today\'s analysis Failed 😥" (26 Aug); "Failed." quoting his own 30 Oct call. Together with 30 Jan 2026 that is three acknowledged misses against ~20 reposted hits in the sample.', '26 Aug, 30 Oct'],
]

const AUG_LOG: [string, string, string][] = [
  ['16 Jul 2025', 'Nifty', '"Huge move is coming. High probability for sell off" → 1 Aug: "Nifty was 25100, lost 500 points. I\'m on spot."'],
  ['9 Aug', 'Nifty', '"Mercury direct 11 Aug + Mars shifting nakshatra → possible reversal, 14 August" → 18 Aug: "Market up more than 350 points."'],
  ['11 Aug', 'Nifty / Metals', '"Bullish time starting in few minutes. One way move" → +215; metals report: Shatabhisha/Purvabhadra bearish, Moon–Rahu 0° "volatility with negative bias", strong bearish yog after 18:30.'],
  ['12 Aug', 'Nifty', '"Approaching 11:30 IST. Mkt recovered from low. Bears, stay cautious" → "Nifty in green."'],
  ['25 Aug', 'Nifty', '"Avoid short after 10:45" → "Good upmove after 10:45."'],
  ['26 Aug', 'Nifty', '"Today\'s analysis Failed." (miss)'],
  ['3 Sep', 'Nifty', '"Bullish time starts after 10:30" → "+100 points."'],
  ['9–11 Sep', 'Metals', 'Reports: Uttarabhadra bullish, Vyatipat "will create volatility", bullish yog till 18:00; Revati→Ashwini bullish, strong bullish yog 16:00–21:30; Ashwini bullish, "cautious in short after 14:00" → "got predicted move".'],
  ['15–17 Sep', 'Nifty', '"Sun ingress Virgo conjunct Mercury — powerful; BankNifty may outperform; avoid short" → 17 Sep "sharp move after 13:30, upside".'],
  ['23 Sep', 'Metals', 'Report: Hasta→Chitra slightly bullish; Mars→Swati bearish; bullish yog 13:30–20:00 then "many strong bearish yog starting together" → "current bullish trend may end soon".'],
  ['30 Sep', 'Metals', 'Report: Purvashadha bearish; "higher till 12:40 then out of steam" → "Gold lost $70 after that" (a reply: "Your prediction is wrong" — he asked how).'],
  ['1 Oct', 'Metals', 'Report: Purvashadha→Uttarashadha slightly bullish; range till 14:15 then bullish yog till 20:30.'],
  ['5–8 Oct', 'Nifty', '"Strong bearish yog from Tuesday, 500/600 points lower" → "possibility, not sure shot".'],
  ['16–17 Oct', 'Metals', 'Telegram: "Major turning point tomorrow after 12:00 IST. Avoid long" → 17 Oct sell-off.'],
  ['20 Oct', 'Metals', 'Report: Hasta→Chitra bullish, Jupiter in Cancer bearish, Amavasya bullish, Vaidhriti bullish with volatility.'],
  ['26–28 Oct', 'Metals', 'Grand trine "one way"; Mars→Scorpio "strong bearish 1–2 days"; Mars 120 Jupiter bearish → "Gold and Silver continuously dropping. Predicted last week."'],
  ['30 Oct', 'Nifty', '"May change direction after 13:00. Recovery possible" → "Failed." (miss)'],
]

// ---- seventh learning pass: X posts of Mar - Jul 2025 (April 2025.mp4)

const EARLY_CONCEPTS: [string, string, string][] = [
  ['Kaal Sarp yog', '"From Monday, Kaal sarp yog is going to break. Mars is moving away from Ketu and leaving Leo. Major change in Geopolitical situations are coming." All classical planets on one side of the Rahu–Ketu axis; the breaking planet is the one nearest the axis. Computed in the Regime block.', '25 Jul 2025'],
  ['Kshaya tithi', '"Today is Kshay tithi which is considered as bearish for commodities" — a tithi that starts after one sunrise and ends before the next, so the panchang skips it. Computed per day; downgrades the metals call.', '19 May 2025'],
  ['Pluto is not in his system', '"This week we were not able to identify the bullish yog which gave solid upside in gold and silver. If we check, only 3–4 yogs are occurring which involve Pluto. Generally, in Vedic astrology (which I follow) does not consider Pluto." — a stated blind spot; the outlook keeps Pluto aspects, labelled.', '20 Apr 2025'],
  ['"IMP" aspects', 'Week notes mark a few exact aspects IMP: Venus 0 Mn Node, Venus 60 Uranus, Sun 90 Mars (20–21 Apr) → "very scary correction is expected … do not hold any risky overnight position" → gold $3,500 → $3,263 in two days. Jupiter 90 Mn Node = Volatility, Sun 45 Venus = Bullish (16 May). All in the aspect table as observed.', 'Apr–May 2025'],
  ['Orb matters', '"Those who are mentioning Mars conj. Ketu in Leo caused plane crash are not completely True. Mars is on 3° while Ketu on 28°, they are in one sign but not on conjunction." Same sign ≠ conjunction.', '13 Jun 2025'],
  ['Software', 'The horary example (21 Mar 2025, "Will I get US visa?") is a Jagannatha Hora screenshot — Lahiri by default, with the same DK/MK/BK/PK karaka columns that appear in his planet tables. Free software; the app\'s Lahiri choice matches it.', '22 Apr 2025'],
  ['Natal rules he shares', '"Mercury — key for trading. If Mercury is ahead of the Sun in your chart, you are very quick in trading decisions … If behind, cautious" (7 Jul). "Saturn retrograde from 13 July. If Saturn is lord of 5H or 2H, stay cautious and avoid speculation" (10 Jul). The app\'s profile panel does a comparable birth-chart gate.', 'Jul 2025'],
  ['Weekly "no strong yog" verdicts', '"Overall, it seems that there is no strong bullish yog which can lift gold and silver prices to the upside" (2 May) → "We were bearish in gold and silver since start of May" (12 May). The weekly note is where his medium-term bias is set; the daily report works inside it.', 'May 2025'],
  ['Ambiguity criticism', 'A reader: "As always no clear direction is mentioned always ambiguous … mention clearly bearish and bullish days." Reply: "not a magic crystal but a tool to assist, not a sure shot. You must also use technical levels." Same stance as his Sep T&C.', '8 Jul 2025'],
  ['Marketing voice', '"Nifty is weak as predicted. Astrology works. Also proved that free stuff has no value" (30 Apr); "This is the power of Astro-based timing" (23 Apr). Hits are amplified; treat the record as promotional until scored.', 'Apr 2025'],
]

const EARLY_LOG: [string, string, string][] = [
  ['28 Mar 2025', 'Nifty', '"Sun eclipse on 29 March and Saturn also change sign. This may be last phase of bullish trend."'],
  ['1–4 Apr', 'Both', '"Be careful if you are bullish" (metals); "Nakshatra is not supportive for higher prices. Blood bath??" (3 Apr) → 4 Apr crash; "Gold and silver may weaken after 18:00" → "both are down".'],
  ['20–23 Apr', 'Metals', 'Week note: IMP aspects → "very scary correction" → "Gold crashed from $3,500 to $3,263 in just 2 days … told them not to go long."'],
  ['21–22 Apr', 'Nifty', '"May not show strength till 11:30"; "important time from 14:00".'],
  ['28–30 Apr', 'Nifty', '"After 11:00 real move, cautious in shorts" → new day\'s high; "Do not carry long, weak" → "Nifty is weak as predicted."'],
  ['2 May', 'Metals', 'Week note: "no strong bullish yog" → 12 May "bearish since start of May, informed well in advance."'],
  ['6–7 May', 'Nifty', '"Mercury entering Aries conjunct Sun — reversal in many markets. FED tomorrow" → Operation Sindoor.'],
  ['15 May', 'Nifty', '"From 19 May strong bullish yog — NIFTY could leap 3–5% to 25,800–26,000", time frame 7 June. (Nifty reached ~25,100 by early June — a partial miss to grade.)'],
  ['16–23 May', 'Metals', 'Reports: Mula→Purvashadha bearish; Shravana→Dhanishta bullish + Kshaya tithi bearish; Dhanishta→Shatabhisha; Shatabhisha/Purvabhadra not supportive + Vaidhriti; Purvabhadra→Uttarabhadra bullish; Revati bearish. Posted as "check accuracy".'],
  ['29 May', 'Metals', 'Report: Ardra/Punarvasu not supportive; strong bullish yog 17:00–22:30 → "On spot."'],
  ['4–5 Jun', 'Nifty', '"Good after 9:45"; "avoid long carrying, looks weak"; "Mercury enters Gemini conjunct Jupiter before RBI — max 8% swings in past. Friday key day?"'],
  ['13 Jun', 'Nifty', '"Though gap down, careful following the downtrend, may recover" → recovered from −400 to −162.'],
  ['22–23 Jun', 'Nifty', '"Weakness to 11:30, recovery 11:30–15:00, careful in short after 11:30" → "approaching the bullish time".'],
  ['8–9 Jul', 'Both', 'Report: Jyeshtha neutral, Vaar-tithi bearish, "no strong yog … follow technical levels"; Nifty: "Mool nakshatra gives high volatility, your stop could be triggered."'],
  ['16–25 Jul', 'Both', '"Sun enters Cancer conjunct Mercury — trend changing, may start upward journey"; "huge move coming, high probability sell off, 21 July" → 18 Jul "effects started??"; 25 Jul Kaal Sarp breaking.'],
]

// ---- eighth learning pass: X posts of Jan - Mar 2025 (Jan 2025.mp4)

const NIFTY_NAK: [string, string, string][] = [
  ['Magha', '"unpredictable for stocks, but if we get uptrend, it will be quite strong" (Dow)', '20 Dec 2024'],
  ['Krittika', 'neutral to slightly positive', '10 Jan 2025'],
  ['Mrigashira', 'supportive for higher prices', '7 Jun 2024'],
  ['Rohini', 'supportive for stocks (bearish for metals the same day)', '10 Jan, 7 Feb 2025'],
  ['Hasta', 'favourable / supportive for stocks', '23–24 Dec 2024'],
  ['Chitra', 'supportive (24 Dec 2024, 17 Feb 2025); neutral once (27 Nov 2024)', '27 Nov 2024, 24 Dec 2024, 17 Feb 2025'],
  ['Swati', 'not much favourable for higher prices', '18 Feb 2025, 18 Aug 2026'],
  ['Vishakha', 'not supportive (20 Feb 2025) vs slightly positive (19 Aug 2026) — mixed', '20 Feb 2025, 19 Aug 2026'],
  ['Anuradha', 'not supportive (20 Feb 2025, 20 Aug 2026) vs supportive (21 Feb 2025, 21 Aug 2026) — 2–2', 'Feb 2025, Aug 2026'],
  ['Mula', '"bearish for stock markets" (5 Nov 2024), "not supportive" (30 Dec 2024), "high volatility" (9 Jul 2025)', '5 Nov 2024, 30 Dec 2024, 9 Jul 2025'],
  ['Purvashadha', 'supportive for higher prices / bullish', '6 Nov 2024, 24 Aug 2026'],
  ['Uttarashadha', 'supportive for stocks', '1 Jan 2025'],
  ['Shravana', 'neutral', '26 Aug 2026'],
  ['Dhanishta', 'bullish', '27 Aug 2026'],
  ['Shatabhisha', 'bearish', '28 Aug 2026'],
  ['Purvabhadra', '"later is bullish for stocks" (11 Nov 2024); recovery after 11:30 (27 Jun 2024); "neutral" (28 Jun 2024)', '27–28 Jun 2024, 11 Nov 2024'],
  ['Uttarabhadra', 'neutral for stocks', '28 Jun 2024'],
  ['Revati', 'neutral for stocks', '3 Feb 2025'],
]

const JAN_CONCEPTS: [string, string, string][] = [
  ['The Nifty report format', 'Same skeleton as metals, in three or four session windows: "The Moon is in Capricorn and it stays in Uttarshadha nakshatra during Indian market hours. This is supportive for stocks. Moon 45 Saturn will create volatility with negative bias. Intraday yogs are not bearish … 09:15–11:15 Bullish, 11:15–15:00 Flat to bullish, 15:00–15:30 Bullish." Dow Jones gets the same with ET windows.', '1 Jan 2025'],
  ['Avoid the first 45 minutes', '"Avoid trading till 10:00 IST, wrong decision may be taken" — the opening window is marked "Bearish — but avoid trading" rather than traded.', '17 Feb 2025'],
  ['Conditional reversal', '"Mention conditional sharp bullish reversal after 13:00 IST" — posted with the chart showing the 13:00 turn. The time is the call; the direction is conditional on where price arrives.', '8 Jan 2025'],
  ['Sun 45 Rahu', '"Sun 45° Rahu aspect is negative and high volatility is expected" (Nifty, 3 Feb). Observed bearish in the aspect table.', '3 Feb 2025'],
  ['Sun–Saturn approaching', '"Sun and Saturn are going to near each other, this is also bearish for whole metal sector including copper." Sun 0 Saturn is now observed bearish; note he reads the APPROACH, days before exactness.', '27 Feb 2025'],
  ['Kshaya on Amavasya', '"Today is Amavashya from 08:56 IST but it is khsaya tithi, this is considered as a bearish … Amavashya is bullish but as mentioned due to its kshaya, very difficult to know its effect on market." The outlook renders this day as volatile — both rules fire and cancel.', '27 Feb 2025'],
  ['Mars direct → metals & chemicals', '"Tomorrow Mars turning direct, this may impact the current trend in metal sector. Gold, Silver and copper may affected. Chemical sector will also affected." Mars stations now carry this note (24 Feb, 07:37 IST).', '23 Feb 2025'],
  ['Five-body sign stellium', '"Very dangerous time is coming. March end, Sun+Saturn+Rahu+Mercury+Venus in Pisces. Very critical time for global markets. Make or break for all financial markets." The Regime block now flags ≥4 bodies in one sign.', '14 Feb 2025'],
  ['Event stacking', '"Mercury retrograde on 15th March, Uranus enters Taurus 19th March, Saturn enters Pisces 29th March, Sun eclipse 29th March. These all have ability to turn the table." — several slow events in one fortnight is itself the signal.', '14 Mar 2025'],
  ['Vaar-Tithi for Nifty too', '"IF Vaar-Tithi yog dominate then we may get strong bearish trend in the market" — it is not only a metals rule. Three more dated calls: Wed 8 Jan and Fri 10 Jan bearish, Wed 19 Feb bearish. The classical table now agrees on 6 of his 10 dated calls; the other 4 are stored as observed overrides.', 'Jan–Feb 2025'],
  ['Self-grading, both ways', '"Nifty — Missed in second half but on spot overall. Gold — on spot" (10 Jan); "Irrespective of my accuracy, I am posting all my last week prediction" (9 Feb); to a troll: "You have time to point out my failure of predictions" (20 Feb). He also posts his broker trade summary (28 Jan).', 'Jan–Feb 2025'],
]

const JAN_LOG: [string, string, string][] = [
  ['1 Jan 2025', 'Nifty', 'Report: Uttarashadha supportive, Moon 45 Saturn volatile-negative, bullish windows → "not surprised by today\'s bullish trend … predicted a week ago."'],
  ['7 Jan', 'Metals', 'Report: Revati→Ashwini bullish, "AVOID SHORT TODAY", bullish yogs 12:00 and 17:30–23:30 → "On spot."'],
  ['8 Jan', 'Both', 'Metals: Ashwini→Bharani, Vaar-Tithi bearish, bearish yog till 16:30 then bullish; Nifty: "conditional sharp bullish reversal after 13:00" → chart posted.'],
  ['10 Jan', 'Both', 'Nifty: Krittika→Rohini neutral-positive, bullish yog from 09:45 → "Missed in second half but on spot overall"; Gold: Rohini bearish, Vaar-Tithi bearish, bullish yog till 19:30 → "on spot".'],
  ['17 Jan', 'Nifty', '"Be careful in short after 12:30 IST. Sharp upside is possible" → "recovered unexpectedly, hope to trade in green."'],
  ['28 Jan', 'Both', 'Metals: Purvashadha→Uttarashadha "not much supportive", Venus→Pisces slightly bearish, bearish yog till 14:45 then strong bullish till 20:45 → "On spot"; Nifty: "Bearish time starts 13:13 IST" → "100+ points fall in just 2 min."'],
  ['29 Jan', 'Nifty', '"Bearish time starts at 11:30 IST. Be careful."'],
  ['3 Feb', 'Nifty', 'Report: Revati neutral, Sun 45 Rahu negative/volatile; bullish 09:15–10:00, slightly bearish 10:00–12:00, bullish 12:00–13:15, strong bearish 13:15–15:30 (posted 9 Feb "irrespective of my accuracy").'],
  ['7 Feb', 'Nifty', 'Report: Rohini supportive; range-negative 09:30–12:00, strong bearish 12:00–13:30, bullish 13:30–15:30; "many planetary changes Saturday–Sunday, avoid risky positions; Delhi election results tomorrow."'],
  ['12–15 Feb', 'Both', '"Avoid short after 12:00" (Nifty); "Gold continues to rise. If you think it will, time to be cautious" → 15 Feb "Gold down $43 and $57 from day\'s high."'],
  ['17–21 Feb', 'Nifty', 'Reports: Chitra favourable, avoid till 10:00, bullish 10:00–13:30; Swati bearish 09:15–11:30 then recovery; Vishakha→Anuradha "not supportive", bearish 09:15–13:15; Anuradha "supportive" but "very difficult to predict today, follow technical levels."'],
  ['27 Feb', 'Metals', 'Report: Dhanishta→Shatabhisha, Kshaya Amavasya "very difficult to know its effect", Mercury→Pisces not favourable, Sun–Saturn nearing bearish for metals incl. copper; "Avoid risky long."'],
  ['4–5 Mar', 'Nifty', '"12:15 IST important time. If we fall, we may fall near day\'s low"; "Avoid long for tomorrow. Seems weak 60 min+ opening."'],
  ['13–14 Mar', 'Global', '"A very important prediction regarding global stock markets will be shared here soon"; event list (Mercury retro, Uranus→Taurus, Saturn→Pisces, eclipse): "These all have ability to turn the table."'],
]

// ---- ninth learning pass: X posts of Nov - Dec 2024 (Nov 2024.mp4) — the launch

const LAUNCH_CONCEPTS: [string, string, string][] = [
  ['How it started', 'Nov 2024: "Join my Gold & Silver channel for premium insights, available as a free trial throughout November"; a second Telegram for Dow Jones / S&P; Nifty analysis "shared in telegram channel" from 4 Nov. From Jan 2025: "Monthly fees will be Rs 2000/-." Profile: "A Vedic astrological approach to decoding market movements. Tweets are for education. Trollers will be blocked." (32.5K followers by Aug 2026).', 'Nov 2024 – Jan 2025'],
  ['The first Nifty reports', 'Same skeleton from day one: Moon sign + star read for stocks, then 3–4 session windows. "The Moon is in Scorpio, Jayestha nakshatra till 09:46 IST then enters in Sagittarius and Mool Nakshatra, this is bearish for stock markets … 09:15–09:35 Range bound to negative, 09:35–11:55 More bearishness, 13:00–15:30 If we drop, we may drop hard."', '5 Nov 2024'],
  ['"No planetary support"', '"When there is no planetary support, Market fall like today" (28 Nov, Swati, strong bearish yog at opening). The absence of bullish yogs is itself the bearish call.', '28 Nov 2024'],
  ['Mercury retrograde midpoint', '"Retrograde Mercury is at halfway mark of its entire journey. This is considered as a peak of its energy. Some changes are possible in all financial markets." Computed per day (stations 26 Nov and 16 Dec → midpoint 6 Dec, his date).', '6 Dec 2024'],
  ['Uranus ingress timing', '"Friday move did not expected but this may be effect if Uranus entering in Aries in retro motion. Nifty made day\'s low at 10:45 IST while Uranus enters in Aries at 11:24 IST. We should believe that today\'s volatility was only due to the Uranus." Uranus sign changes are now listed as astro events.', '16 Dec 2024'],
  ['Saturn direct', '"From today Saturn is turning to direct motion. Retrograde Saturn — this is one of many factors of bullish phase in all commodities market and stock markets. Watch for trend now. Stay cautious if you are too bullish." Saturn stations carry this note.', '15 Nov 2024'],
  ['One-way-turn aspects', 'Week note: "Venus–Neptune and Sun–Neptune aspects are very important and can turn the market in one way direction. It seems that Wednesday will be deciding day for bulls or bears. Friday aspects are bearish" (Venus 120 Jupiter, Sun 144 Mars). All four are in the aspect table.', '16 Dec 2024'],
  ['Medium-term yogs', '"Bullish yog is starting. Traders should avoid shorts. Please note — This is not intraday yog" (20 Nov, metals); "bearish yog is running in stock markets since 20th Oct … will neutralize the bullish yogs in coming days" (5 Nov). Two layers: the running medium-term yog and the intraday ones inside it.', 'Nov 2024'],
  ['Moon in Rahu\'s star', 'Muhurat trading: "The Moon is in Rahu\'s nakshatra, this is little supportive with volatility. Rahu–Venus combination may not allow dip in index." The star\'s lord is read directly — the same rule the outlook uses for unobserved stars.', '1 Nov 2024'],
  ['Natal warning', '"You may facing loss in speculation (Future/Options) if you have Sagittarius ascendant. Avoid it otherwise you will blow your account. (This is sidereal)." — Mars-related, per the hashtag.', '20 Nov 2024'],
  ['"New technique" — Failed', '"Bank Nifty may shows good strength after 11:15 IST to 14:15. This is new technique. Pls watch price action only" → "BANKNIFTY recovered all loss after 11:15 but soon unable to maintain gains. Down 600+ at present. Failed 😅". The fourth acknowledged miss in the sample.', '12 Nov 2024'],
  ['Mars–Venus for silver', '"Mars and Venus relation is occurring from 09:10 IST, this will impact Silver heavily. Must watch the price action before taking any position." No exact aspect at the eight standard angles that day — his "relation" here is looser than an exact aspect.', '4 Nov 2024'],
]

const LAUNCH_LOG: [string, string, string][] = [
  ['1 Nov 2024', 'Both', 'Muhurat: "little supportive with volatility"; metals "in red after reaching daily high on Payroll data" — "Astrologically, I\'m bearish."'],
  ['3–4 Nov', 'Metals', 'Week note: "bullish phase in gold and silver is ended … week from 4 Nov not supportive for bulls"; 4 Nov Jyeshtha bullish, yog till 14:33 then slide.'],
  ['4–5 Nov', 'Nifty', 'Range-negative → negative → high volatility (4 Nov); "Jayestha→Mool bearish for stocks … if we drop, we may drop hard" (5 Nov).'],
  ['5 Nov', 'Metals', 'Report: Jyeshtha→Mula supportive, Vaar-Tithi bullish, "the Sun is highly negative"; buy before 09:45, sell before 16:00.'],
  ['6 Nov', 'Both', 'Metals: Mula→Purvashadha slightly bearish, Moon 0 Venus bearish → "Gold and Silver are down heavily as per my analysis. Made good profit"; Nifty: Purvashadha supportive, "AVOID SHORT TODAY".'],
  ['11 Nov', 'Both', 'Nifty: Shatabhisha→Purvabhadra bullish for stocks, sharp fall 09:15–09:30 then recovery, weak after 12:30 → "Closed shorts. Small quantity long"; metals: Purvabhadra bearish, range-bound, spike then cool-down after 21:00.'],
  ['12 Nov', 'BankNifty', '"Good strength 11:15–14:15, new technique" → "Down 600+. Failed."'],
  ['13 Nov', 'Metals', 'Report: Revati not supportive, bullish till 11:00, bearish yog 11:00–22:00.'],
  ['15–20 Nov', 'Both', 'Saturn direct "watch for trend"; 20 Nov metals "Bullish yog is starting (not intraday). Avoid shorts."'],
  ['27–28 Nov', 'Nifty', '"Nifty may rise after 10:00. Avoid short" (Chitra neutral, bearish yog till 10:00) → hit; 28 Nov Swati "bearish for stocks", strong bearish at opening → "market fall like today".'],
  ['3–6 Dec', 'Nifty', '"Mercury is retrograde and big move is expected"; "Bullish time after 12:00, avoid short" (4 Dec); "Fall expected after 12:00" (5 Dec); "Retrograde Mercury at halfway mark" (6 Dec).'],
  ['11–13 Dec', 'Metals', 'Reports: Revati→Ashwini slightly bullish, Vaar-Tithi bearish, strong bearish 11:45–17:30 then bullish 17:30–23:00; Ashwini→Bharani bearish, Vaar-Nakshatra bearish, drift down till 15:30, strong bearish 15:30–20:45; Krittika bullish, Moon–Uranus volatility → "Again accurately predicted the trend."'],
  ['13 Dec', 'Nifty', '"Do you believe Monday will be bullish day? … my astro analysis indicate bearish price action" → "Warned my subscribers not to follow bullish trend after 13th Dec. Strong price reversal."'],
  ['16–20 Dec', 'Both', 'Week note: Uranus→Aries volatility; Wednesday Venus/Sun–Neptune "deciding day"; Friday aspects bearish; Dow 20 Dec Magha "unpredictable, avoid short sell".'],
  ['23–24 Dec', 'Nifty', 'Hasta favourable, bearish yog from 12:45 → "able to predict today\'s upmove as well as down move"; Hasta→Chitra bullish till 13:45 then bearish → "NIFTY +100. Trollers hiding."'],
  ['30 Dec', 'Nifty', 'Mula "not supportive for stocks", bearish yog from 09:30, strong bearish 13:15–15:30 → "again on spot today".'],
]

// ---- tenth learning pass: X posts of May - Oct 2024 (May 2024.mp4) — before the launch

const PRE_CONCEPTS: [string, string, string][] = [
  ['Mercury-retrograde moratorium', '"Mercury is unpredictable planet during retrograde. This is second time I am experiencing almost all predictions went wrong. Now decided to avoid making prediction during retro Mercury." Each day in the outlook now carries a Mercury ℞ badge and a low-confidence flag while it is retrograde.', '28 Aug 2024'],
  ['Combustion (Tara Asta)', 'He disputes a panchang site\'s Mercury-combustion dates with an Astro-Seek ephemeris set to "Sidereal – Lahiri": "According to the website, Mercury combustion started on 4 April 2024, distance 13° and ended on 1 May. However, on 1 May the distance was 23°. Not the 12° and 14° they used." Confirms Lahiri a third way; the outlook flags Mercury (and Venus) combustion with the classical orbs.', '29 Jun 2024'],
  ['Colour-coded aspect list', 'The 30 May election report rates each aspect green / yellow / orange / red: Mars 30 Uranus, Sun 72 Neptune, Sun 60 Node, Jupiter 120 Pluto green; Mars 36 Saturn and Mars 36 Jupiter yellow; Sun 135 Pluto orange; Sun 90 Saturn red. He uses 30° and 36° (decile) too. The rated 60/72/90/120/135 ones are now in the aspect table.', '30 May 2024'],
  ['Sun 180 Pluto', '"Sun 180° Pluto at 11:09 IST. Seems this aspect is responsible for huge drop in gold and silver prices today due to reduction of custom duty. This is not coincident." (23 Jul 2024, budget day). Observed bearish.', '23 Jul 2024'],
  ['Yog end-time explains the reversal', '"Why market reversed? Yog not failed. See the end time in image" — a Panchang-app screenshot with Tithi Ekadashi ends 09:39:09 and Karana Vishti ends 09:39:09 circled. The end-times are the pivots — the same idea the outlook\'s panchang block shows.', '16 Aug 2024'],
  ['Medium-term yog with an end date', '"Strong bearish yog will end on 29 August 2024. Till you have to be very careful in long. We may get little effects of this bearish yog after 25 August as Mercury going to direct in few days." (12 Aug); "From 8th Aug, approx 3% pullback is possible due to the Strong Bearish yog … Do your own research, I may go wrong" (7 Aug).', 'Aug 2024'],
  ['Conditional multi-day rule', '"Monday seems bullish but one special yog is occurring, clash between bullish and bearish yog. If we close in red, then we may witness weakness in the market for 2–3 trading days. This is purely conditional."', '19 Jul 2024'],
  ['Small-interval "new technique"', '"I am posting prediction of Monday\'s market movement at very small intervals. THIS IS TESTING OF NEW TECHNIQUE. I MAY GO WRONG, BUT MUST FOCUS ON STARTING TIME, MOVEMENT CAN START FROM THE GIVEN TIME." (15 Jul report in 5–6 windows.)', '14 Jul 2024'],
  ['Bhadra was NOT in his method in 2024', '"Received many queries, why market not dropped though Bhadra started during market hours? I do not follow this in my prediction, btw, my analysis also went wrong." (24 Jun). By 2026 Vishti is a headline rule in his reports — the method evolved.', '24 Jun 2024'],
  ['Aspects that failed', '"Many strong bearish aspects failed today. Moon 0 Pluto 11:22, Moon 45 Saturn 16:17. These are considered bearish but unable to create bearishness. Is there error in analysis and judgement?" (24 Jun). Moon 0 Pluto is read bullish in his 2026 reports — the sign flipped.', '24 Jun 2024'],
  ['Vaidhriti = bearish (Nifty)', 'Week note: "Vaidhruti yog is running from 11:52 IST, this is considered as a bearish." For metals in 2026 he reads it "volatility with bullish bias" — the outlook now applies bearish to Nifty, volatile-bullish to metals.', '23 Jun 2024'],
  ['Sun in Leo is not "always bullish"', 'Three years of Sun-in-Leo gold charts posted against the belief that "Sun in Leo is always bullish for gold and silver … pls post your analysis."', 'Aug 2024'],
  ['His background', '"I began studying astrology in 1995 and financial astrology in 2007. Despite my experience, I sometimes struggle to predict market movements and occasionally fail." "How can anyone learn this in a two-day workshop … Many fraudsters claim to teach."', '5 Aug 2024'],
  ['Free week → paid channels', '"A Chance to Access My Premium Channels – FREE for a Week … NIFTY, DOW JONES & GOLD-SILVER" (Jun 2024). Telegram screenshots reposted as proof ("These were my original post shared on my telegram channel").', 'Jun–Jul 2024'],
]

const PRE_LOG: [string, string, string][] = [
  ['30 May 2024', 'Nifty', 'Post-election report: "sharp rise from June 1 … few days after the results on June 4. Another turning point on 9th June. Avoid short positions from May 31."'],
  ['4 Jun', 'Nifty', '"Today\'s fall in Nifty was not expected. I failed in today\'s prediction … Still I believe bullish yog is running, avoid short." (election-day crash — miss)'],
  ['7 Jun', 'Both', 'Nifty: Mrigashira supportive, bullish 09:15–11:00, bearish 11:00–12:30, strong bullish 12:30–15:30 → "Successfully predicted"; metals: Ardra from 10:14 bearish, "bearish price action for entire day", NFP caution → hit.'],
  ['21–23 Jun', 'Both', '"Avoid long, Dow may give up uptrend"; week note: Vaidhriti bearish Monday, Venus 90 Uranus / Mercury 120 Saturn Wed, Mercury 45 Jupiter Fri — "sudden change in direction and high volatility".'],
  ['24 Jun', 'Nifty', '"Many strong bearish aspects failed today" (Moon 0 Pluto, Moon 45 Saturn) — miss, acknowledged.'],
  ['26–28 Jun', 'Both', 'Metals "again on spot"; Nifty 27 Jun Shatabhisha→Purvabhadra 11:37, strong bearish till 11:30 then recovery; 28 Jun Purvabhadra→Uttarabhadra 10:11 "neutral", bearish/volatile 10:00–13:30 → "Nifty gave up all gains … Trollers are hiding"; Dow 28 Jun Uttarabhadra supportive, bullish 09:30–12:30 ET.'],
  ['5–12 Jul', 'Nifty', '"No major planetary change next week … stay bullish with cautions"; "Monday seems bearish worldwide, one day only"; "bullish till 13:05, sharp reaction 13:05–13:40, again rise, avoid short".'],
  ['17 Jul', 'Metals', '"One of the bullish yog involving the Sun and Saturn is ending today. Very careful in long" (Sun 120 Saturn separating).'],
  ['19–24 Jul', 'Both', 'Conditional close-in-red rule (22 Jul); Sun 180 Pluto 11:09 on budget day → metals drop; "Nifty dropped as per my analysis 12:18 IST, missed by one minute"; "Avoid short, we may touch 25k till 5 Aug" (Nifty reached 25,000 on 1 Aug).'],
  ['30–31 Jul', 'Nifty', '"12:30 IST important time, weakness expected"; "Pls do not expect huge fall. We are in bullish planetary phase"; "new lifetime high, do not short … still time left".'],
  ['7–12 Aug', 'Global', '"From 8th Aug approx 3% pullback … Strong Bearish yog … I may go wrong" (markets rose from 8 Aug — miss); "Strong bearish yog will end on 29 August, careful in long".'],
  ['19–20 Aug', 'Both', '"Many important planetary aspects today + full Moon … capable of changing trend" → next day "No impact on markets of these aspects" (miss).'],
  ['27–30 Aug', 'Both', 'Metals "bearish price action possible, stay cautious"; Nifty "avoid shorts till 11:45" (29 Aug), "may give up gains after 13:55" (30 Aug); 28 Aug the retrograde-Mercury moratorium.'],
]

const SOURCES: [string, string][] = [
  ['Recording 2026-08-28 16:54', 'Telegram channel "Saptarsh Insight" — Nifty / Gold / Silver bulletins 14–28 Aug 2026, panchang + planet sheets, aspect tables, conjunction calendar, astronomical diary, eclipse note.'],
  ['Recording 2026-08-28 18:12', 'X account @sonisunil59 "MARKET ASTROLOGY" (Sunil J. Soni, Saptarsh Astrological Services, Gujarat) — Gold & Silver Premium Reports 2 Jul–10 Aug, Jupiter-in-Cancer table, Sun+Ketu analog, July conjunction and Moon-sign calendars, channel tiers.'],
  ['may.mp4 (recorded 2026-08-28)', 'X account, posts 23 Apr–18 Jun 2026 — the earlier prose-format premium reports (4, 15, 19–21, 26 May; 2–3, 8–10 Jun), the 25 May timing notice, the 7 May bearish-yog alert and its follow-ups, medium-term calls.'],
  ['April.mp4 (recorded 2026-08-28)', 'X account, posts 1–23 Apr 2026 — premium reports of 6, 8, 16, 17, 23 Apr (second confirmations of Amavasya-bullish and Vyatipata-positive; Anuradha / Mula / Pushya bullish; Venus→Bharani, Mars→Uttarabhadra), the 1 Apr Nifty "pivotal time" post.'],
  ['Nov 2025.mp4 (recorded 2026-08-28)', 'X account, posts 4 Nov 2025 – 30 Jan 2026 — premium reports of 14, 18, 19 Nov, 4 Dec, 30 Jan; the 26 Jan week note; the 6 Jan Rahu–Ketu and Jupiter-by-pada tables; the Dec-1993 stellium analog; the 21 Jan early-degree post; Nifty timing posts; his 4 Dec option fills; the 30 Jan miss.'],
  ['August 2025.mp4 (recorded 2026-08-28)', 'X account, posts 16 Jul – 30 Oct 2025 — premium reports of 11 Aug, 9–11 Sep, 23 Sep, 30 Sep, 1 Oct, 20 Oct, 27–28 Oct; the 26 Oct grand-trine post; the 9 Aug Mercury-direct reversal call; the 15 Sep Sun–Mercury Virgo ingress; the 22 Sep T&C; ten Nifty timing posts incl. two "Failed".'],
  ['April 2025.mp4 (recorded 2026-08-28)', 'X account, posts 28 Mar – 25 Jul 2025 — the earliest reports (16, 19–23, 29 May; 7–8 Jul), the 20 Apr and 2 May and 16 May week notes with IMP-marked aspects, the Apr 2025 gold-crash call, the 19 May "Nifty 3–5%" call, the Kaal Sarp post, the Pluto admission, the Jagannatha Hora horary example, natal Mercury/Saturn rules.'],
  ['Jan 2025.mp4 (recorded 2026-08-28)', 'X account, posts 1 Jan – 14 Mar 2025 — daily NIFTY reports (1 Jan; 3, 7, 17–21 Feb), Dow Jones reports with ET windows, metals reports of 7–8, 10, 28 Jan and 27 Feb, the 14 Feb five-body Pisces "make or break" note, the 14 Mar event list, his 28 Jan trade summary, the 20 Feb troll dispute.'],
  ['Nov 2024.mp4 (recorded 2026-08-28)', 'X account, posts 1 Nov – 30 Dec 2024 — the launch: free-trial Telegram channels, the first Nifty reports (4–6, 11, 27–28 Nov; 5, 23–24, 30 Dec), metals reports (4–7, 11, 13 Nov; 11–13 Dec), Dow 20 Dec, the 16 Dec week note, Mercury-retro-midpoint and Saturn-direct posts, the 12 Nov BankNifty miss, the Rs 2000/month notice.'],
  ['May 2024.mp4 (recorded 2026-08-28)', 'X account, posts 30 May – 30 Aug 2024 — before the launch: the 30 May post-election report with a colour-coded aspect list, the 4 Jun and 24 Jun admitted misses, the 23 Jun week note, Nifty/Dow reports of 7, 27–28 Jun and 15 Jul, the free-week promo, the 29 Jun combustion dispute (Lahiri), Sun 180 Pluto on budget day, the Aug bearish-yog calls, the 28 Aug retrograde-Mercury moratorium.'],
]

const CHECKLIST: string[] = [
  'Cast the panchang for the trading day at Mumbai (NSE). Write down tithi, nakshatra, yoga, karana AND the clock time each one ends.',
  'Note the Moon\'s sign and nakshatra during 09:15–15:30. If it changes inside the session, that time is your first pivot candidate.',
  'Check the karana and yoga for the inauspicious ones (Vishti, Vaidhriti, Vyatipata). They override an otherwise bullish Moon.',
  'List the day\'s exact aspects with clock times, Moon aspects first — they are the intraday timers. Label each one and keep a log of what actually happened.',
  'Mark Rahu Kaal, Yamaganda and Gulika Kaal on the session; watch whether weakness clusters in Rahu Kaal as the channel claims.',
  'Scan the ephemeris diary for the week: conjunctions, node crossings, Full/New Moon, eclipses, stations. Treat them as "watch for a change in price structure", not as a direction.',
  'Write the outlook in the bulletin\'s shape: base bias → change time → intraday windows → one instruction (e.g. "avoid short after 11:40") → overall bias. Say "follow technicals" when the sky is mixed.',
  'Next day, score yourself. The only thing that separates a method from a belief is a written hit-rate against the base rate.',
]

// ---------------------------------------------------------------- view

function SaptarshPanel({ date }: { date?: string }) {
  return (
    <>
      <SaptarshWeek date={date} />

      <SaptarshBacktest />

      <section className="panel">
        <h2>Saptarsh Insight channel — how the bulletin is built</h2>
        <p className="learn-lead">
          How a professional daily market-astrology post is built, learned
          from the <em>Saptarsh Insight</em> channel (Nifty · Gold · Silver,
          posts of 14–28 Aug 2026). Each block below is one component of
          their bulletin, what it contains, and how they read it. Their
          calls are reported as <em>their</em> practice — untested here.
        </p>

        <h3 className="gann-h3">1 · The panchang sheet</h3>
        <p className="learn-p">
          Posted every evening for the next trading day as a two-column
          table. The end-times are the point: they are the day's built-in
          pivot clock.
        </p>
        <table className="graha-table learn-table">
          <thead><tr><th>Field</th><th>What it is / how it is used</th></tr></thead>
          <tbody>
            {PANCHANG_FIELDS.map(([k, v]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">2 · The planet-position sheet</h3>
        <p className="learn-p">
          One row per body, ascendant included, cast for the session.
          Unlike the rasi chart it carries <em>motion</em> — speed,
          latitude and declination — which is what the aspect timetable
          is computed from.
        </p>
        <table className="graha-table learn-table">
          <thead><tr><th>Column</th><th>Meaning</th></tr></thead>
          <tbody>
            {POSITION_COLS.map(([k, v]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">3 · The timed aspect table</h3>
        <p className="learn-p">
          <code>Planet-1 · angle · Planet-2 · exact time · probable effect</code>.
          Almost every row is a <strong>Moon</strong> aspect, because the
          Moon completes one in a few hours — these are the intraday
          timers. Eight angles are used; the 45° / 135° family (rare in
          Indian practice) is included. Labels below are the channel's own,
          copied from the posts.
        </p>
        <table className="graha-table learn-table">
          <thead><tr><th>Angle</th><th>Name</th><th>Observed calls</th></tr></thead>
          <tbody>
            {ASPECTS.map(([deg, name, ex]) => (
              <tr key={deg}>
                <td className="learn-key mono">{deg}°</td>
                <td>{name}</td>
                <td>{ex}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Pattern to notice: Moon–Saturn and Moon–Node contacts are read
          bearish at every hard angle; Moon–Venus / Moon–Jupiter soft
          angles bullish; anything involving Mercury with Pluto/Neptune
          "volatile". The same pair flips with the angle (Moon 60 Saturn
          bullish, Moon 45/90 Saturn bearish).
        </p>

        <h3 className="gann-h3">4 · Transit table with Jaimini karakas</h3>
        <p className="learn-p">
          The richer PDF format (24 Aug) tags each planet with its
          <em> chara karaka</em> — the Jaimini role assigned by degree
          rank, highest degree = Atma karaka — then gives Degree ·
          Nakshatra · Pada · Navamsa · Interpretation (Bullish/Bearish).
        </p>
        <table className="graha-table learn-table">
          <thead><tr><th>Tag</th><th>Karaka</th><th>On 24 Aug 2026</th></tr></thead>
          <tbody>
            {KARAKAS.map(([t, k, who]) => (
              <tr key={t}><td className="learn-key mono">{t}</td><td>{k}</td><td>{who}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">5 · Writing the outlook</h3>
        <p className="learn-p">
          The prose always has the same skeleton, in this order:
        </p>
        <ol className="learn-ol">
          <li><strong>Base bias</strong> from the Moon's sign + nakshatra during trading hours ("The Moon is in Capricorn and it stays in Shravana nakshatra. This is neutral for Nifty.")</li>
          <li><strong>Change time</strong> if the Moon changes sign or star inside the session ("till 13:36 IST then enters Aquarius").</li>
          <li><strong>Yogas</strong> — bullish / bearish "yog" windows with clock times, plus any inauspicious karana/yoga that overrides.</li>
          <li><strong>Named aspects</strong> that colour the day (Sun–Mercury conjunction bullish; Mercury 180 Rahu confusing; Saturn aspect bearish).</li>
          <li><strong>One instruction</strong>: "avoid short after 11:40", "avoid carrying short", "book profit within few hours", "be careful in derivatives in this window".</li>
          <li><strong>Overall bias</strong> — or an honest "we are not confident … follow technicals" when events pile up.</li>
          <li><strong>Gold &amp; Silver</strong> get the same treatment from the same Moon, often with a different verdict (Uttarashadha: bullish for metals).</li>
        </ol>

        <h3 className="gann-h3">Observed Moon → Nifty calls (Aug 2026)</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Day</th><th>Moon sign</th><th>Nakshatra</th><th>Call</th><th>Reasoning given</th></tr></thead>
          <tbody>
            {MOON_CALLS.map(([d, sign, nak, tone, why]) => (
              <tr key={d}>
                <td className="learn-key">{d}</td><td>{sign}</td><td>{nak}</td>
                <td><Tag tone={tone} /></td><td>{why}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Eight calls are far too few to grade. Keep the table growing —
          the app's Gann tab shows what an audited rule looks like once it
          has enough rows.
        </p>

        <h3 className="gann-h3">6 · Conjunction calendar</h3>
        <p className="learn-p">
          Multi-planet stelliums by sign with entry/exit dates. The
          channel's rule: "important planetary conjunction and separation
          — major change is possible around these dates" (it flagged
          17-08 and 22-08).
        </p>
        <table className="graha-table learn-table">
          <thead><tr><th>Sign</th><th>Planets</th><th>Window</th><th>Duration</th></tr></thead>
          <tbody>
            {CONJUNCTIONS.map(([s, p, w, d]) => (
              <tr key={s + p}><td className="learn-key">{s}</td><td>{p}</td><td className="mono">{w}</td><td>{d}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">7 · Astronomical diary &amp; eclipses</h3>
        <p className="learn-p">
          A plain ephemeris events list (the kind printed in an
          almanac) is posted alongside — no interpretation, just dates.
          Around 28 Aug it read:
        </p>
        <table className="graha-table learn-table">
          <tbody>
            {DIARY.map(([t, e]) => (
              <tr key={t}><td className="learn-key mono">{t}</td><td>{e}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="learn-p">
          Their eclipse note (26 Aug) is worth copying as a habit: an
          eclipse in Aquarius / Shatabhisha is "relevant to white metals";
          the <em>immediate</em> market effect was historically negligible;
          over the following ~30 trading days their observed average was
          +1.28% Nifty / +4.60% Bank Nifty (their figures, unverified);
          a Full Moon is "a potential turning point — watch for a change in
          price structure", never an automatic direction; and a Sun–Mercury
          conjunction two hours earlier should be read together with the
          eclipse, not in isolation.
        </p>

        <h3 className="gann-h3">8 · Timing convention</h3>
        <p className="learn-p">
          Vedic day-ending clock: times after midnight but before sunrise
          are written <code>25:00, 26:00, 28:59</code> (= 01:00, 02:00,
          04:59 IST) so an event belongs to the panchang day it falls in.
          After sunrise, ordinary clock time.
        </p>
      </section>

      <section className="panel">
        <h2>From the X account — the Gold &amp; Silver Premium Report</h2>
        <p className="learn-lead">
          @sonisunil59 ("MARKET ASTROLOGY", Sunil J. Soni, Gujarat) is the
          person behind Saptarsh. Since July 2026 the account has posted the
          paid <em>Gold &amp; Silver Premium Report</em> a day late as proof of
          record. It is the metals counterpart of the Nifty bulletin and
          adds the pieces below. Three channel tiers: <em>Glimpse</em> (free:
          panchang, placements, events, market mood), <em>Insight</em> (paid:
          aspects, Moon–nakshatra, yogas, probable trend for Nifty / Dow /
          Gold / Silver), <em>Trend Triggers</em> (premium: "high-resolution
          astro timing every 4–6 hours", metals only).
        </p>

        <h3 className="gann-h3">9 · Anatomy of the premium report</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Block</th><th>Contents</th></tr></thead>
          <tbody>
            {REPORT_ANATOMY.map(([k, v]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          The week outlook above reproduces this shape: metals windows run
          03:30 → 27:30 IST with ET alongside, split at every exact aspect.
          Their windows are hand-drawn from "bullish yog / bearish yog"
          activity, which is unpublished — the app's are aspect-driven.
        </p>

        <h3 className="gann-h3">10 · Rules stated on X</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Trigger</th><th>Their reading</th><th>Where</th></tr></thead>
          <tbody>
            {X_RULES.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">11 · Moon nakshatra → gold &amp; silver (observed)</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Nakshatra</th><th>Metals call</th><th>Report date</th></tr></thead>
          <tbody>
            {METAL_NAK.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Sign-level calls also appeared next to the Moon row: Capricorn
          bullish, Aquarius / Pisces / Cancer / Sagittarius bearish, Gemini and
          Virgo neutral. Note
          Purvashadha is bullish for Nifty but bearish for metals, and
          Shravana neutral for Nifty but bearish for metals — the two
          instruments do not share one table. All of these feed the
          "observed" badges in the week outlook.
        </p>

        <h3 className="gann-h3">12 · Position rules they repeat</h3>
        <ul className="learn-ul">
          {POSITION_RULES.map((s, i) => <li key={i}>{s}</li>)}
        </ul>

        <h3 className="gann-h3">13 · Medium-term context they publish monthly</h3>
        <ul className="learn-ul">
          <li><strong>Conjunction calendar</strong> — sign, planets sharing it, from/to, duration, planet leaving, planet entering (July: Pisces Saturn+Neptune; Taurus Mars+Uranus 43 d; Cancer Mercury+Venus+Jupiter 12 d; Leo Venus+Ketu 28 d; Gemini Sun+Mercury 10 d; Cancer Sun+Jupiter 20 d). The week outlook computes the live version in its "Regime" block.</li>
          <li><strong>Moon sign-change calendar</strong> — date, weekday, from-sign → to-sign for the month ("only three planets are changing signs except Moon").</li>
          <li><strong>Jupiter transit history</strong> — for the sign Jupiter occupies, every past transit with gold % and silver % over the transit.</li>
          <li><strong>Same-sky analogs</strong> — a chart from a year with the same slow-planet placement (Sun+Ketu in Leo, Aug 2025 vs Aug 2026) with the move that followed.</li>
        </ul>

        <h3 className="gann-h3">14 · The earlier format (Apr–Jun 2026) — what it adds</h3>
        <p className="learn-p">
          Before the boxed template, the report was prose: Moon → Nakshatra →
          "Imp Aspect" → "Important Astro. Event" → interpretation → 3–4
          trading windows with GMT, later ET. It states things the template
          only implies.
        </p>
        <table className="graha-table learn-table">
          <thead><tr><th>Concept</th><th>What they wrote</th><th>Where</th></tr></thead>
          <tbody>
            {MAY_CONCEPTS.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Sixteen more labelled aspects came from these reports (Moon 0
          Saturn "strong bullish", Moon 180 Saturn bullish, Venus 0 Jupiter
          "strong bearish for the day", Moon 0 Venus / Jupiter / Neptune
          bearish for hours, Moon 0 Mars bullish, Moon 60 Rahu / Uranus
          bearish, Sun 60 Saturn bearish, Mercury 90 Saturn "high volatile",
          Mars 90 Pluto / Venus 45 Uranus volatile, Sun 120 Moon bearish). All
          are in the outlook as "observed". Pattern: with the Moon, Saturn
          is bullish at 0/60/180 and bearish at 45/90; the Sun is bearish at
          almost every angle; conjunctions to Venus and Jupiter are read
          bearish, to Mars and Pluto bullish.
        </p>

        <h3 className="gann-h3">Medium-term calls log (for grading later)</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Date</th><th>Market</th><th>Call</th></tr></thead>
          <tbody>
            {MEDIUM_TERM_LOG.map(([d, m, c]) => (
              <tr key={d + m}><td className="learn-key">{d}</td><td>{m}</td><td>{c}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          He grades himself publicly ("on spot", "exactly in line") but only
          on hits; the misses are not reposted. This log keeps the dated
          calls so they can be scored against Nifty / gold / silver closes
          both ways.
        </p>

        <h3 className="gann-h3">15 · Nov 2025 – Jan 2026 — the medium-term toolkit</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Concept</th><th>What they wrote</th><th>Where</th></tr></thead>
          <tbody>
            {NOV_CONCEPTS.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Two more Vaar-Tithi data points (Thu + 15 "bullish" 4 Dec, Fri +
          Krishna 12 "bearish" 30 Jan) agree with the classical table; a
          third showed his table distinguishes paksha — Tuesday + Shukla 14
          was bullish on 28 Jul and Tuesday + Krishna 14 bearish on 18 Nov.
          The outlook now keys the observed calls by full tithi.
        </p>

        <h3 className="gann-h3">Calls log, Nov 2025 – Jan 2026</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Date</th><th>Market</th><th>Call</th></tr></thead>
          <tbody>
            {NOV_LOG.map(([d, m, c]) => (
              <tr key={d + m}><td className="learn-key">{d}</td><td>{m}</td><td>{c}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">16 · Jul – Oct 2025 — grand trine, transition points, and the misses</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Concept</th><th>What they wrote</th><th>Where</th></tr></thead>
          <tbody>
            {AUG_CONCEPTS.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">Calls log, Jul – Oct 2025</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Date</th><th>Market</th><th>Call</th></tr></thead>
          <tbody>
            {AUG_LOG.map(([d, m, c]) => (
              <tr key={d + m}><td className="learn-key">{d}</td><td>{m}</td><td>{c}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">17 · Mar – Jul 2025 — the beginning: Kaal Sarp, Kshaya tithi, and what he leaves out</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Concept</th><th>What they wrote</th><th>Where</th></tr></thead>
          <tbody>
            {EARLY_CONCEPTS.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">Calls log, Mar – Jul 2025</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Date</th><th>Market</th><th>Call</th></tr></thead>
          <tbody>
            {EARLY_LOG.map(([d, m, c]) => (
              <tr key={d + m}><td className="learn-key">{d}</td><td>{m}</td><td>{c}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">18 · Jan – Mar 2025 — the Nifty reports</h3>
        <p className="learn-p">
          Until this batch nearly every observed nakshatra call was for
          metals. These posts carry daily NIFTY reports with the Moon's
          star read for stocks — the table the outlook's Nifty column now
          draws on.
        </p>
        <table className="graha-table learn-table">
          <thead><tr><th>Nakshatra</th><th>Nifty call</th><th>Report date</th></tr></thead>
          <tbody>
            {NIFTY_NAK.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Rohini is the clearest split: supportive for stocks, bearish for
          metals on the very same day (10 Jan 2025). Thirteen of 27 stars
          now have a Nifty reading; the rest stay extrapolated by lord.
        </p>
        <table className="graha-table learn-table">
          <thead><tr><th>Concept</th><th>What they wrote</th><th>Where</th></tr></thead>
          <tbody>
            {JAN_CONCEPTS.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">Calls log, Jan – Mar 2025</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Date</th><th>Market</th><th>Call</th></tr></thead>
          <tbody>
            {JAN_LOG.map(([d, m, c]) => (
              <tr key={d + m}><td className="learn-key">{d}</td><td>{m}</td><td>{c}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">19 · Nov – Dec 2024 — the launch</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Concept</th><th>What they wrote</th><th>Where</th></tr></thead>
          <tbody>
            {LAUNCH_CONCEPTS.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Vaar-Tithi: three more dated calls (Tue + 4 bullish, Wed + 11 and
          Fri + 13 bearish), all on days the classical tables are silent —
          stored as overrides. Vaar-Nakshatra: his "bearish" on Thursday +
          Ashwini/Bharani (12 Dec) contradicts the classical Sarvartha
          Siddhi for Thu + Ashwini, so that pair is now an observed
          override too.
        </p>

        <h3 className="gann-h3">Calls log, Nov – Dec 2024</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Date</th><th>Market</th><th>Call</th></tr></thead>
          <tbody>
            {LAUNCH_LOG.map(([d, m, c]) => (
              <tr key={d + m}><td className="learn-key">{d}</td><td>{m}</td><td>{c}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">20 · May – Oct 2024 — before the launch: the rules he learned the hard way</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Concept</th><th>What they wrote</th><th>Where</th></tr></thead>
          <tbody>
            {PRE_CONCEPTS.map(([k, v, w]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td><td>{w}</td></tr>
            ))}
          </tbody>
        </table>

        <h3 className="gann-h3">Calls log, May – Aug 2024</h3>
        <table className="graha-table learn-table">
          <thead><tr><th>Date</th><th>Market</th><th>Call</th></tr></thead>
          <tbody>
            {PRE_LOG.map(([d, m, c]) => (
              <tr key={d + m}><td className="learn-key">{d}</td><td>{m}</td><td>{c}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Three more acknowledged misses here (4 Jun, 24 Jun, 20 Aug) plus
          the 8 Aug "3% pullback" that did not come. Across ten recordings
          that is 7 explicit misses and 3 partial ones against roughly 110
          dated calls — his reposted hit rate is high because he chooses
          what to repost; the logs keep both sides.
        </p>

        <h3 className="gann-h3">Sources ingested so far</h3>
        <table className="graha-table learn-table">
          <tbody>
            {SOURCES.map(([k, v]) => (
              <tr key={k}><td className="learn-key">{k}</td><td>{v}</td></tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          Each new recording adds rows here and, where a rule is
          computable, to the week outlook. Everything is the channel's
          practice as posted — none of it has been graded against prices
          yet; the daily checklist's last step is where that starts.
        </p>
      </section>

      <section className="panel">
        <h2>Worked example — Thursday 27 Aug 2026</h2>
        <ul className="learn-ul">
          <li><strong>Panchang:</strong> Moon in Capricorn till 13:36, then Aquarius; Dhanishta all day. Vishti karana active the whole session.</li>
          <li><strong>Base bias:</strong> Dhanishta → bullish. <strong>Override:</strong> Vishti → "you have to be very careful in following bullish trend".</li>
          <li><strong>Windows:</strong> may open red; 09:30–13:30 critical, recovery attempt; 13:30–15:30 bearish yog, "we may drop hard".</li>
          <li><strong>Aspects that day:</strong> Sun 150 Pluto 01:41 bear · Moon 45 Neptune 03:11 bear · Moon 120 Venus 03:31 bull · Sun 150 Neptune 06:02 bull · Mercury 150 Pluto 12:13 vol · Mercury 150 Neptune 14:21 vol · Moon 135 Mars 16:00 bull · Moon 45 Saturn 22:31 bear · Sun 0 Mercury 22:35 bull · Moon 0 Node 23:41 bear.</li>
          <li><strong>Diary:</strong> Mercury superior conjunction 17:06, Moon at ascending node 18:46, Full Moon + lunar eclipse next morning 04:18 — hence the next day's "not confident, be careful".</li>
          <li><strong>Metals:</strong> same Moon, Dhanishta bullish for gold/silver, "no intraday bullish yogs — we may get bearish price action".</li>
        </ul>
        <p className="muted-note">
          Note how the sign change at 13:36 and the yog window at 13:30
          coincide: the change-time from the panchang sheet is what the
          intraday window is hung on.
        </p>
      </section>

      <section className="panel">
        <h2>Where each concept lives in this app</h2>
        <table className="graha-table learn-table">
          <thead><tr><th>Concept</th><th>In Astro-app</th><th></th></tr></thead>
          <tbody>
            {APP_MAP.map(([c, where, have]) => (
              <tr key={c}>
                <td>{c}</td><td>{where}</td>
                <td className={have ? 'learn-have' : 'learn-missing'}>{have ? '✓' : 'not yet'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="muted-note">
          The taught GRAHA MARKETS method (chain, prasanam gate, horai) and
          this bulletin method start from the same sky. They differ in the
          interpretive layer: chain-counting vs. Moon-nakshatra + timed
          aspects. Neither has shown an edge under audit — see the
          Prediction tab's fitted-table note.
        </p>
      </section>

      <section className="panel">
        <h2>Daily checklist for a new astrologer</h2>
        <ol className="learn-ol">
          {CHECKLIST.map((s, i) => <li key={i}>{s}</li>)}
        </ol>
        <p className="muted-note">
          Study aid reproducing an observed practice — not financial advice
          and not a signal.
        </p>
      </section>
    </>
  )
}

export default SaptarshPanel
