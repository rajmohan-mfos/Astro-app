// The author's PLANET POSITION sheet: full sidereal degrees (KP), KP
// Placidus house, sign/star/sub lords, the ruling chain box and day lord.
import type { PlanetPositionSheet } from '../types'

const ABBREV: Record<string, string> = {
  Sun: 'Sun', Moon: 'Moo', Mars: 'Mar', Mercury: 'Mer', Jupiter: 'Jup',
  Venus: 'Ven', Saturn: 'Sat', Rahu: 'Rah', Ketu: 'Ket',
}

export default function PlanetPosition({ sheet }: { sheet: PlanetPositionSheet }) {
  return (
    <div className="planet-position">
      <table className="graha-table transit-table">
        <thead>
          <tr>
            <th>Planet</th>
            <th>Deg : Mn : Se</th>
            <th>House</th>
            <th>Sign-L</th>
            <th>Star-L</th>
            <th>Sub-L</th>
          </tr>
        </thead>
        <tbody>
          {sheet.rows.map((r) => (
            <tr key={r.planet}>
              <td className={r.planet === 'Lag' ? 'token-lagna' : undefined}>
                {r.planet}
                {r.retro && <span className="token-retro">#</span>}
              </td>
              <td className="mono">{r.deg}</td>
              <td className="mono">{String(r.house).padStart(2, '0')}</td>
              <td>{ABBREV[r.rasi_lord] ?? r.rasi_lord}</td>
              <td>{ABBREV[r.nak_lord] ?? r.nak_lord}</td>
              <td>{ABBREV[r.sub_lord] ?? r.sub_lord}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="chain-box">
        {sheet.chain_text.map((line, i) => (
          <div key={i} className="chain-line">{line}</div>
        ))}
        <div className="chain-daylord">
          Day Lord: {sheet.day_lord.en} · {sheet.day_lord.ta}
          {sheet.cast && <> · chain cast at {sheet.cast}</>}
        </div>
      </div>
    </div>
  )
}
