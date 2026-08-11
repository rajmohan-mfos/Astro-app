// The "advance prediction chart" — the teacher's hand-drawn day graph
// rendered from the computed segments: green rising, red falling, with
// turn-point times, like the OPTIONS MERSAL reference chart.
import type { GraphSegment } from '../types'

const W = 720
const H = 260
const PAD_X = 48
const TOP = 28
const SESSION_START = 9.25
const SESSION_END = 15.5

// vertical drift per hour, SVG y-units (negative = up)
const SLOPES: Record<string, number> = {
  bullish: -16,
  'sideways-bullish': -7,
  sideways: 0,
  angle: 0,
  'sideways-bearish': 7,
  bearish: 16,
}

const COLORS: Record<string, string> = {
  bullish: '#57b95c',
  'sideways-bullish': '#8fbf6f',
  sideways: '#b8a24e',
  angle: '#b06fd6',
  'sideways-bearish': '#d08a5a',
  bearish: '#e05555',
}

function x(h: number): number {
  return PAD_X + ((h - SESSION_START) / (SESSION_END - SESSION_START)) * (W - 2 * PAD_X)
}

function fmt(h: number): string {
  const total = Math.round(h * 60)
  return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
}

interface Wiggle {
  points: string
  color: string
}

function buildPath(segments: GraphSegment[]) {
  // cumulative midline first, so the whole path stays in frame
  const drifts = segments.map((s) => (SLOPES[s.bias] ?? 0) * (s.end - s.start))
  let level = 0
  const levels = [0]
  for (const d of drifts) {
    level += d
    levels.push(level)
  }
  const min = Math.min(...levels)
  const max = Math.max(...levels)
  const mid = (min + max) / 2
  const base = TOP + (H - TOP - 40) / 2 - mid

  const wiggles: Wiggle[] = []
  const markers: { h: number; y: number }[] = []
  let y0 = base + levels[0]
  markers.push({ h: SESSION_START, y: y0 })

  segments.forEach((seg, i) => {
    const y1 = base + levels[i + 1]
    const slope = (y1 - y0) / (seg.end - seg.start)
    const pts: string[] = []
    const steps = Math.max(6, Math.round((seg.end - seg.start) * 6))
    for (let k = 0; k <= steps; k++) {
      const h = seg.start + ((seg.end - seg.start) * k) / steps
      const yy = y0 + slope * (h - seg.start)
      const jitter = k === 0 || k === steps
        ? 0
        : Math.sin(k * 2.7 + i) * 6 + Math.sin(k * 1.3) * 3
      pts.push(`${x(h).toFixed(1)},${(yy + jitter).toFixed(1)}`)
    }
    wiggles.push({ points: pts.join(' '), color: COLORS[seg.bias] ?? '#999' })
    markers.push({ h: seg.end, y: y1 })
    y0 = y1
  })
  return { wiggles, markers }
}

export default function PredictionGraph({ segments }: { segments: GraphSegment[] }) {
  if (!segments.length) return null
  const { wiggles, markers } = buildPath(segments)

  return (
    <div className="prediction-graph">
      <svg viewBox={`0 0 ${W} ${H}`} role="img"
        aria-label="Advance prediction chart">
        <line x1={PAD_X} y1={TOP - 12} x2={PAD_X} y2={H - 34}
          stroke="var(--line)" strokeWidth="2" />
        <line x1={PAD_X} y1={H - 34} x2={W - PAD_X} y2={H - 34}
          stroke="var(--line)" strokeWidth="1" />
        {segments.map((s, i) => (
          <rect key={i} x={x(s.start)} y={TOP - 12}
            width={x(s.end) - x(s.start)} height={H - TOP - 22}
            fill={i % 2 ? 'rgba(255,255,255,0.02)' : 'transparent'} />
        ))}
        {wiggles.map((w, i) => (
          <polyline key={i} points={w.points} fill="none" stroke={w.color}
            strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
        ))}
        {markers.map((m, i) => (
          <g key={i}>
            <circle cx={x(m.h)} cy={m.y} r="3.2" fill="var(--ink)" />
            <text x={x(m.h)} y={m.y - 10} textAnchor="middle"
              className="graph-time">{fmt(m.h)}</text>
          </g>
        ))}
        {segments.map((s, i) => (
          <text key={i} x={(x(s.start) + x(s.end)) / 2} y={H - 16}
            textAnchor="middle" className="graph-label">
            {s.planet}({s.count}) {s.bias.replace('-', ' ')}
          </text>
        ))}
      </svg>
    </div>
  )
}
