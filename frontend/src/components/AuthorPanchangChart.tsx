import type { ChartCell, ComputeResult } from '../types'

/** The author's panchang chart (OPTIONS MERSAL format).
 *
 *  A South-Indian 4×4 grid with an extra ring OUTSIDE it: for every body
 *  in a cell, its sub lord and star lord, with the star lord nearest the
 *  grid. Decoded from the reference chart dated 06-01-2022 and confirmed
 *  on 11 of 12 bodies (only Rahu's sub differs, mean vs true node).
 *
 *  Grid geometry: 8 tracks each way. Tracks 1–2 and 7–8 are the label
 *  ring; 3–6 are the chart itself.
 *
 *      1  2 | 3  4  5  6 | 7  8      1,2 = sub,star  (left)
 *            ┌───────────┐            7,8 = star,sub  (right)
 *      sub star           star sub    rows likewise top/bottom
 */

// sign -> [gridRow, gridCol] inside the 4×4 chart (1-indexed within it)
const CELL: Record<number, [number, number]> = {
  11: [1, 1], 0: [1, 2], 1: [1, 3], 2: [1, 4],
  10: [2, 1], 3: [2, 4],
  9: [3, 1], 4: [3, 4],
  8: [4, 1], 7: [4, 2], 6: [4, 3], 5: [4, 4],
}

// which outside edge each cell's label ring hangs off. Corners use the
// left/right edge, as the reference chart does.
type Edge = 'left' | 'right' | 'top' | 'bottom'
const EDGE: Record<number, Edge> = {
  11: 'left', 10: 'left', 9: 'left', 8: 'left',
  2: 'right', 3: 'right', 4: 'right', 5: 'right',
  0: 'top', 1: 'top',
  7: 'bottom', 6: 'bottom',
}

const RASIS_TA = ['மேஷம்', 'ரிஷபம்', 'மிதுனம்', 'கடகம்', 'சிம்மம்', 'கன்னி',
  'துலாம்', 'விருச்சிகம்', 'தனுசு', 'மகரம்', 'கும்பம்', 'மீனம்']

/** Label ring for one cell: one line per body, sub lord then star lord. */
function Ring({ cell, edge }: { cell: ChartCell; edge: Edge }) {
  const [row, col] = CELL[cell.sign]
  const vertical = edge === 'top' || edge === 'bottom'
  // outer track then inner track, where "inner" is nearest the grid
  const [subTrack, starTrack] =
    edge === 'left' ? [1, 2]
      : edge === 'right' ? [8, 7]
        : edge === 'top' ? [1, 2]
          : [8, 7]

  const place = (track: number) => vertical
    ? { gridRow: track, gridColumn: col + 2 }
    : { gridRow: row + 2, gridColumn: track }

  // The ring is a table aligned ROW BY ROW with the cell beside it: one
  // line per body, same order, same line height, and a spacer matching
  // the cell's rasi label so line 1 of the ring sits on line 1 of the
  // cell. The reference chart aligns them exactly this way.
  const list = (key: 'sub_short' | 'star_short') => (
    <div className={`ring-cell${vertical ? ' ring-vertical' : ''}`}
      style={place(key === 'sub_short' ? subTrack : starTrack)}>
      {!vertical && <div className="ring-spacer" aria-hidden="true" />}
      {cell.items.map((it, i) => (
        <div key={i} className="ring-lord">{it[key]}</div>
      ))}
    </div>
  )

  if (cell.items.length === 0) return null
  return <>{list('sub_short')}{list('star_short')}</>
}

export default function AuthorPanchangChart({ result }: { result: ComputeResult }) {
  const cells = result.kp?.cells
  if (!cells) return null
  const weekday = result.panchang.vaara.en.toUpperCase()
  const [y, m, d] = result.input.date.split('-')

  return (
    <div className="author-chart-wrap">
      <div className="author-chart">
        {cells.map((cell) => {
          const [row, col] = CELL[cell.sign]
          return (
            <div key={cell.sign} className="author-cell"
              style={{ gridRow: row + 2, gridColumn: col + 2 }}>
              <div className="author-rasi">{RASIS_TA[cell.sign]}</div>
              {cell.items.map((it, i) => (
                <div key={i} className="author-body">
                  <span className={it.retro ? 'token-retro' : undefined}>
                    {it.short}{it.retro ? '(R)' : ''}
                  </span>
                  <span className="author-deg">{it.deg}</span>
                </div>
              ))}
            </div>
          )
        })}

        {cells.map((cell) => (
          <Ring key={`r${cell.sign}`} cell={cell} edge={EDGE[cell.sign]} />
        ))}

        {/* Three nested frames, as the reference draws them:
              container border | sub column | FRAME B | star column | grid
            Frame B sits BETWEEN the two lord columns — that is the line
            separating e.g. "Ven" from "Mer" — so it spans tracks 2..7,
            leaving the outer sub column outside it. */}
        <div className="author-frame" aria-hidden="true"
          style={{ gridRow: '2 / 8', gridColumn: '2 / 8' }} />
        <div className="author-frame author-frame-inner" aria-hidden="true"
          style={{ gridRow: '3 / 7', gridColumn: '3 / 7' }} />

        <div className="author-center"
          style={{ gridRow: '4 / 6', gridColumn: '4 / 6' }}>
          <div className="author-date">{d}-{m}-{y}</div>
          <div className="author-weekday">{weekday}</div>
          <div className="author-time">
            {result.input.time} · KP
            {result.kp?.ayanamsa != null && ` ${result.kp.ayanamsa}°`}
          </div>
        </div>
      </div>
      <p className="muted-note">
        Author's format: each body's <strong>star lord</strong> sits just
        outside its cell and its <strong>sub lord</strong> one track further
        out. Includes the lagna and the outer planets (Uranus, Neptune,
        Pluto), which the nine-graha jothidam chart omits. Degrees are
        DD.MM — 26.36 is 26°36′, not 26.6°. Positions are{' '}
        <strong>Lahiri</strong>, matching the reference chart: solving the
        ayanamsa from its own printed degrees gives Lahiri to 0.3′ and KP
        to 5.5′. The transit tables below stay KP, which is what their
        timings reproduce on.
      </p>
    </div>
  )
}
