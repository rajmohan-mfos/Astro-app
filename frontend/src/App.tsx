import { useEffect, useState } from 'react'
import { compute } from './api'
import type { ComputeRequest, ComputeResult } from './types'
import InputPanel from './components/InputPanel'
import SouthIndianChart from './components/SouthIndianChart'
import GrahaTable from './components/GrahaTable'
import PredictionPanel from './components/PredictionPanel'
import PanchangChartView from './components/PanchangChartView'
import ProfilePanel from './components/ProfilePanel'
import PredictionGraph from './components/PredictionGraph'
import ChainVariables from './components/ChainVariables'
import DayScoreBar from './components/DayScoreBar'
import GannCosmogram from './components/GannCosmogram'
import SaptarshPanel from './components/SaptarshPanel'

// Opens on today at 09:00 — just before the 09:15 open, and the moment
// the author's own reference charts are cast at.
//
// This does NOT move the prediction. graph.cast_chart always recasts the
// chain at sunrise whatever time is shown, so the intraday/weekly/
// long-term calls are unchanged. What it moves is everything cast at the
// displayed moment: the rasi chart, the panchang chart, the KP
// planet-position sheet and the no-number prasanam reading.
const NOW = new Date()
const DEFAULT_REQUEST: ComputeRequest = {
  year: NOW.getFullYear(), month: NOW.getMonth() + 1, day: NOW.getDate(),
  hour: 9, minute: 0,
  // Mumbai — the NSE's own location, so the market chart is cast where
  // the market is. Sunrise there is ~30 min later than Chennai, which
  // moves the sunrise-cast chain; see RULES-SOURCES.md.
  tz_offset: 5.5, lat: 19.076, lon: 72.8777,
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
  // Three non-overlapping views. Prediction is the default because it is
  // what the app is opened for; the rasi chart and graha table used to
  // sit underneath it, which meant they appeared below EVERY prediction
  // sub-tab. They now have one home of their own.
  const [view, setView] =
    useState<'prediction' | 'jothidam' | 'panchang' | 'gann' | 'learn'>('prediction')

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
            <button className={view === 'prediction' ? 'tab active' : 'tab'}
              onClick={() => setView('prediction')}>Prediction</button>
            <button className={view === 'jothidam' ? 'tab active' : 'tab'}
              onClick={() => setView('jothidam')}>Rasi chart (Lahiri)</button>
            <button className={view === 'panchang' ? 'tab active' : 'tab'}
              onClick={() => setView('panchang')}>Panchang chart (KP)</button>
            <button className={view === 'gann' ? 'tab active' : 'tab'}
              onClick={() => setView('gann')}>Gann cosmogram</button>
            <button className={view === 'learn' ? 'tab active' : 'tab'}
              onClick={() => setView('learn')}>Saptarsh Insight</button>
          </div>

          {!result && !error && <div className="loading">Computing…</div>}
          {result && view === 'prediction' && (
            <>
              {result.prediction.graph_segments &&
                result.prediction.graph_segments.length > 0 && (
                <section className="panel">
                  <h2>Advance prediction chart — {result.input.date}</h2>
                  {result.prediction.day_score && (
                    <DayScoreBar score={result.prediction.day_score} />
                  )}
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
                  Prediction
                  <span className="status-chip">{result.prediction.status}</span>
                </h2>
                <PredictionPanel prediction={result.prediction}
                  request={{
                    year: Number(result.input.date.slice(0, 4)),
                    month: Number(result.input.date.slice(5, 7)),
                    day: Number(result.input.date.slice(8, 10)),
                    hour: Number(result.input.time.slice(0, 2)),
                    minute: Number(result.input.time.slice(3, 5)),
                    tz_offset: result.input.tz_offset,
                    lat: result.input.lat, lon: result.input.lon,
                  }} />
              </section>
            </>
          )}

          {result && view === 'jothidam' && (
            <>
              <section className="panel">
                <h2>
                  Rasi chart
                  <button className="link-btn" onClick={() =>
                    navigator.clipboard.writeText(chartAsText(result))}>
                    copy chart as text
                  </button>
                </h2>
                <SouthIndianChart result={result} />
                <p className="muted-note">
                  Sidereal Lahiri, ayanamsa {result.ayanamsa}° — the SPEC §5
                  display chart. The Panchang (KP) tab shows the same sky on
                  the KP ayanamsa, ~6′ apart.
                </p>
              </section>

              <section className="panel">
                <h2>Grahas</h2>
                <GrahaTable grahas={result.grahas} lagna={result.lagna} />
              </section>
            </>
          )}

          {result && view === 'panchang' && <PanchangChartView result={result} />}

          {/* Independent of `result` — the calendar only needs a date,
              so it works even while the compute call is in flight */}
          {view === 'gann' && <GannCosmogram date={result?.input.date} />}

          {/* Week outlook needs only a date; the study notes are static */}
          {view === 'learn' && <SaptarshPanel date={result?.input.date} />}
        </div>
      </div>
    </div>
  )
}

export default App
