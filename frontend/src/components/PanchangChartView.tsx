// The KP tab: the author's panchang chart (OPTIONS MERSAL format), the
// panchang with end times, and the KP planet-position sheet.
//
// The two transit tables (சந்திர பெயர்ச்சி / பிற கிரகங்கள்) were removed
// at the user's request. The backend can still compute them — see
// transit.day_chart's include_transits — but nothing displays or reads
// them, so /api/panchang-chart no longer asks for them.
import type { ComputeResult } from '../types'
import AuthorPanchangChart from './AuthorPanchangChart'
import PlanetPosition from './PlanetPosition'
import PanchangTiles from './PanchangTiles'

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
