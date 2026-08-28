// "New concepts" — a study tab for a new astrologer.
//
// Source: a screen recording (28 Aug 2026) scrolling through the
// "Saptarsh Insight" Telegram channel, a daily market-astrology bulletin
// for Nifty, Gold and Silver. The recording had no narration, so every
// concept below is read off the posts themselves (14–28 Aug 2026). The
// channel's interpretations are reported as THEIR practice — nothing
// here has been backtested by this app, and the app's own 5-year audit
// of the taught GRAHA MARKETS method found no edge. Study material.

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
  ['Rahu Kaal / Yamaganda / Gulika / Abhijit windows', 'Horai timeline covers the hour-lords; the three kaal windows are not shown yet', false],
  ['Timed planet-to-planet aspect table', 'Not in the app — the taught method uses the chain (X/X1/Y/Y1) instead of aspects', false],
  ['Jaimini chara karakas', 'Not in the app', false],
  ['Moon nakshatra → base bias', 'Prediction tab → day score (panchang tally) is the taught-method analogue', true],
  ['Conjunction calendar / astronomical diary', 'Gann cosmogram tab lists dated events with their audited hit-rate', true],
  ['Volatility band (no astrology)', '/vol in the Telegram bot', true],
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

function NewConceptsPanel() {
  return (
    <>
      <section className="panel">
        <h2>New concepts — the daily bulletin method</h2>
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

export default NewConceptsPanel
