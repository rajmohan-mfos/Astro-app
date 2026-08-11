import type { ComputeResult } from '../types'

// SPEC 5.6 — fixed-sign layout, sign index → [row, col] (1-based)
const CELL: Record<number, [number, number]> = {
  11: [1, 1], 0: [1, 2], 1: [1, 3], 2: [1, 4],
  10: [2, 1], 3: [2, 4],
  9: [3, 1], 4: [3, 4],
  8: [4, 1], 7: [4, 2], 6: [4, 3], 5: [4, 4],
}

const RASIS_TA = ['மேஷம்', 'ரிஷபம்', 'மிதுனம்', 'கடகம்', 'சிம்மம்', 'கன்னி',
  'துலாம்', 'விருச்சிகம்', 'தனுசு', 'மகரம்', 'கும்பம்', 'மீனம்']

function tokenClass(token: string): string | undefined {
  if (token === 'La') return 'token-lagna'
  if (token.endsWith('(R)')) return 'token-retro'
  return undefined
}

export default function SouthIndianChart({ result }: { result: ComputeResult }) {
  return (
    <div className="chart-wrap">
      <div className="chart-grid">
        {Array.from({ length: 12 }, (_, sign) => {
          const [row, col] = CELL[sign]
          return (
            <div key={sign} className="chart-cell"
              style={{ gridRow: row, gridColumn: col }}>
              <div className="rasi-name">{RASIS_TA[sign]}</div>
              <div className="tokens">
                {result.chart[sign].map((t) => (
                  <span key={t} className={tokenClass(t)}>{t}</span>
                ))}
              </div>
            </div>
          )
        })}
        <div className="chart-center">
          <div className="center-rasi">{result.lagna.rasi_ta} லக்னம்</div>
          <div className="center-deg">{result.lagna.deg_in_sign}</div>
          <div className="center-when">
            {result.input.date} · {result.input.time}
          </div>
        </div>
      </div>
    </div>
  )
}
