// The KP tab: the author's panchang chart (OPTIONS MERSAL format) plus
// the day tables — panchang with end times, சந்திர பெயர்ச்சி / பிற
// கிரகங்கள் transits, and the KP planet-position sheet.
import type { ComputeResult, TransitRow } from '../types'
import AuthorPanchangChart from './AuthorPanchangChart'
import PlanetPosition from './PlanetPosition'
import PanchangTiles from './PanchangTiles'

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

  return (
    <div className="kp-view">
      <section className="panel">
        <h2>பஞ்சாங்க அட்டவணை — panchang chart</h2>
        <AuthorPanchangChart result={result} />
      </section>

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
