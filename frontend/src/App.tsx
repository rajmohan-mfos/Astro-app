import { useEffect, useState } from 'react'
import { compute } from './api'
import type { ComputeRequest, ComputeResult } from './types'
import InputPanel from './components/InputPanel'
import PanchangTiles from './components/PanchangTiles'
import SouthIndianChart from './components/SouthIndianChart'
import GrahaTable from './components/GrahaTable'
import PredictionPanel from './components/PredictionPanel'
import PanchangChartView from './components/PanchangChartView'
import ProfilePanel from './components/ProfilePanel'
import PredictionGraph from './components/PredictionGraph'
import PlanetPosition from './components/PlanetPosition'
import ChainVariables from './components/ChainVariables'

const DEFAULT_REQUEST: ComputeRequest = {
  year: 1990, month: 1, day: 1, hour: 12, minute: 0,
  tz_offset: 5.5, lat: 13.0827, lon: 80.2707, // Chennai
}

function chartAsText(r: ComputeResult): string {
  const pan = r.panchang
  const chain = r.prediction.chain
  const lines = [
    `Astro-app — ${r.input.date} ${r.input.time} (tz ${r.input.tz_offset})`,
    `Lagna: ${r.lagna.rasi} ${r.lagna.deg_in_sign}  ·  Ayanamsa ${r.ayanamsa}`,
    ``,
    ...r.grahas.map((g) =>
      `${g.name.padEnd(8)} ${g.rasi.padEnd(10)} ${g.deg_in_sign}${g.retro ? ' (R)' : ''}`),
    ``,
    `Vaara: ${pan.vaara.en} · Thithi: ${pan.thithi.paksha} ${pan.thithi.name}` +
    ` · Natchathiram: ${pan.natchathiram.name} pada ${pan.natchathiram.pada}` +
    ` · Yogam: ${pan.yogam.name} · Karanam: ${pan.karanam.name}`,
  ]
  if (chain) {
    lines.push('', `X: ${chain.x?.planet}(${chain.x?.count})` +
      (chain.x1 ? `  X1: ${chain.x1.planet}(${chain.x1.count})` : '') +
      `  Y: ${chain.y?.planet}(${chain.y?.count})` +
      (chain.y1 ? `  Y1: ${chain.y1.planet}(${chain.y1.count})` : '') +
      `  → ${chain.first} / ${chain.second}`)
  }
  for (const s of r.prediction.graph_segments ?? []) {
    const f = (h: number) =>
      `${String(Math.floor(h)).padStart(2, '0')}:${String(Math.round((h % 1) * 60)).padStart(2, '0')}`
    lines.push(`${f(s.start)}–${f(s.end)}  ${s.planet}(${s.count})  ${s.bias}`)
  }
  return lines.join('\n')
}

function App() {
  const [result, setResult] = useState<ComputeResult | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<'jothidam' | 'panchang'>('jothidam')

  const run = (req: ComputeRequest) => {
    setBusy(true)
    setError(null)
    compute(req)
      .then(setResult)
      .catch((e: Error) => setError(e.message))
      .finally(() => setBusy(false))
  }

  useEffect(() => {
    run(DEFAULT_REQUEST)
  }, [])

  return (
    <div className="app">
      <header>
        <h1>Astro-app — Jothidam</h1>
        <p>Sidereal (Lahiri) rasi chart &amp; panchang</p>
      </header>

      <div className="columns">
        <div className="left-col">
          <InputPanel onCompute={run} busy={busy} error={error} />
          <ProfilePanel
            chartDate={result ? {
              year: Number(result.input.date.slice(0, 4)),
              month: Number(result.input.date.slice(5, 7)),
              day: Number(result.input.date.slice(8, 10)),
              tz_offset: result.input.tz_offset,
            } : null}
          />
        </div>

        <div className="output-col">
          <div className="view-tabs">
            <button className={view === 'jothidam' ? 'tab active' : 'tab'}
              onClick={() => setView('jothidam')}>Jothidam</button>
            <button className={view === 'panchang' ? 'tab active' : 'tab'}
              onClick={() => setView('panchang')}>Panchang chart (KP)</button>
          </div>

          {!result && !error && <div className="loading">Computing…</div>}
          {result && view === 'jothidam' && (
            <>
              <section className="panel">
                <h2>Panchang</h2>
                <PanchangTiles panchang={result.panchang} />
              </section>

              {result.kp?.planet_position && (
                <section className="panel">
                  <h2>Planet position (KP) — {result.input.date} · {result.input.time}</h2>
                  <PlanetPosition sheet={result.kp.planet_position} />
                </section>
              )}

              {result.prediction.graph_segments &&
                result.prediction.graph_segments.length > 0 && (
                <section className="panel">
                  <h2>Advance prediction chart — {result.input.date}</h2>
                  {result.prediction.chain && (
                    <ChainVariables chain={result.prediction.chain} />
                  )}
                  <PredictionGraph
                    segments={result.prediction.graph_segments} />
                  <p className="muted-note">
                    Study aid drawn from the taught rules — not financial
                    advice. Confirm with prasanam before any entry.
                  </p>
                </section>
              )}

              <section className="panel">
                <h2>
                  Rasi chart
                  <button className="link-btn" onClick={() =>
                    navigator.clipboard.writeText(chartAsText(result))}>
                    copy chart as text
                  </button>
                </h2>
                <SouthIndianChart result={result} />
              </section>

              <section className="panel">
                <h2>Grahas</h2>
                <GrahaTable grahas={result.grahas} lagna={result.lagna} />
              </section>

              <section className="panel">
                <h2>
                  Prediction
                  <span className="status-chip">{result.prediction.status}</span>
                </h2>
                <PredictionPanel prediction={result.prediction} />
              </section>
            </>
          )}
          {result && view === 'panchang' && <PanchangChartView result={result} />}
        </div>
      </div>
    </div>
  )
}

export default App
