// Author-style KP day chart (panchang.png reference): rasi chart with
// degrees, சந்திர பெயர்ச்சி (Moon sub-lord ends), பிற கிரகங்கள் transits,
// and the பஞ்ச அங்கங்கள் block with end times.
import type { ComputeResult, TransitRow } from '../types'
import PlanetPosition from './PlanetPosition'
import PanchangTiles from './PanchangTiles'

const CELL: Record<number, [number, number]> = {
  11: [1, 1], 0: [1, 2], 1: [1, 3], 2: [1, 4],
  10: [2, 1], 3: [2, 4],
  9: [3, 1], 4: [3, 4],
  8: [4, 1], 7: [4, 2], 6: [4, 3], 5: [4, 4],
}

const RASIS_TA = ['மேஷம்', 'ரிஷபம்', 'மிதுனம்', 'கடகம்', 'சிம்மம்', 'கன்னி',
  'துலாம்', 'விருச்சிகம்', 'தனுசு', 'மகரம்', 'கும்பம்', 'மீனம்']

const SHORT_TA: Record<string, string> = {
  Sun: 'சூரி', Moon: 'சந்', Mars: 'செவ்', Mercury: 'புத', Jupiter: 'குரு',
  Venus: 'சுக்', Saturn: 'சனி', Rahu: 'ராகு', Ketu: 'கேது',
}

function LordTable({ rows, withGraha }: { rows: TransitRow[]; withGraha?: boolean }) {
  if (rows.length === 0) {
    return <div className="muted-note">இன்று மாற்றம் இல்லை (no changes today)</div>
  }
  return (
    <table className="graha-table transit-table">
      <thead>
        <tr>
          {withGraha && <th>கிரகம்</th>}
          <th>பா.க.வி</th>
          <th>ராசி</th>
          <th>நட்ச</th>
          <th>உப</th>
          <th>மணி</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i}>
            {withGraha && <td>{r.graha_ta}</td>}
            <td className="mono">{r.deg}</td>
            <td>{r.rasi_lord_ta}</td>
            <td>{r.nak_lord_ta}</td>
            <td>{r.sub_lord_ta}</td>
            <td className="mono">{r.time}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function PanchangChartView({ result }: { result: ComputeResult }) {
  const kp = result.kp
  if (!kp) return null
  const ends = kp.panchang_ends

  // KP positions for this tab's chart, falling back to the top-level
  // Lahiri set only if an older backend did not send them
  const grahas = kp.grahas ?? result.grahas
  const lagna = kp.lagna ?? result.lagna

  const cellGrahas: { ta: string; deg: string; retro: boolean }[][] =
    Array.from({ length: 12 }, () => [])
  for (const g of grahas) {
    cellGrahas[g.sign].push({ ta: SHORT_TA[g.name], deg: g.deg_in_sign, retro: g.retro })
  }

  return (
    <div className="kp-view">
      <div className="chart-wrap">
        <div className="chart-grid kp-grid">
          {Array.from({ length: 12 }, (_, sign) => {
            const [row, col] = CELL[sign]
            return (
              <div key={sign} className="chart-cell"
                style={{ gridRow: row, gridColumn: col }}>
                <div className="rasi-name">{RASIS_TA[sign]}</div>
                <div className="kp-cell-grahas">
                  {sign === lagna.sign && (
                    <div className="token-lagna">லக் {lagna.deg_in_sign}</div>
                  )}
                  {cellGrahas[sign].map((g, i) => (
                    <div key={i} className={g.retro ? 'token-retro' : undefined}>
                      {g.ta} {g.deg}
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
          <div className="chart-center">
            <div className="center-rasi">{result.input.date}</div>
            <div className="center-deg">கிழமை · {result.panchang.vaara.ta}</div>
            <div className="center-deg">அதிபதி · {kp.day_lord.ta}</div>
            <div className="center-when">{result.input.time} · tz {result.input.tz_offset}</div>
          </div>
        </div>
        <p className="muted-note">
          KP (Krishnamurti) ayanamsa
          {kp.ayanamsa != null && ` ${kp.ayanamsa}°`} — these positions
          differ slightly from the Jothidam tab, which is Lahiri per the
          spec. Same sky, two zodiacs 0.097° apart.
        </p>
      </div>

      <section className="panel">
        <h2>பஞ்ச அங்கங்கள் — panchang with end times</h2>
        <PanchangTiles panchang={result.panchang} ends={ends}
          dayLord={kp.day_lord} />
        <p className="muted-note">
          The five elements shown once, with end times. Names, paksha and
          element numbers are from the chart's own moment; end times are
          for the elements running at local midnight, KP (Krishnamurti)
          ayanamsa — matching the author's chart format. Hours past 24:00
          fall after midnight. Thithi and karanam are identical under both
          ayanamsas (they come from the Moon−Sun elongation, so the
          ayanamsa cancels); natchathiram and yogam can differ.
        </p>
      </section>

      <section className="panel">
        <h2>சந்திர பெயர்ச்சி — Moon sub-lord periods (end points)</h2>
        <LordTable rows={kp.moon_transits} />
      </section>

      <section className="panel">
        <h2>பிற கிரகங்களின் பெயர்ச்சி — other graha transits</h2>
        <LordTable rows={kp.planet_transits} withGraha />
      </section>

      {kp.planet_position && (
        <section className="panel">
          <h2>
            Planet position (KP) — {result.input.date} · {result.input.time}
          </h2>
          <PlanetPosition sheet={kp.planet_position} />
        </section>
      )}
    </div>
  )
}
