// Response shape of POST /api/compute (SPEC Section 4).

export interface Lagna {
  lon: number
  sign: number
  rasi: string
  rasi_ta: string
  deg_in_sign: string
}

export interface Graha {
  name: string
  name_ta: string
  lon: number
  sign: number
  rasi: string
  rasi_ta: string
  deg_in_sign: string
  retro: boolean
}

export interface Panchang {
  vaara: { en: string; ta: string }
  thithi: { num: number; name: string; paksha: string }
  natchathiram: { num: number; name: string; name_ta: string; pada: number }
  yogam: { num: number; name: string }
  karanam: { num: number; name: string }
}

export interface RuleFinding {
  section: string
  title: string
  detail: string
  source: string
}

export interface GraphSegment {
  start: number
  end: number
  planet: string
  count: number
  bias: string
}

export interface ChainVar {
  planet: string
  count: number
}

export interface PredictionChain {
  x: ChainVar | null
  x1: ChainVar | null
  y: ChainVar | null
  y1: ChainVar | null
  first: string
  second: string
  cast_time?: string
}

export interface DayScore {
  panchang_total: number
  chain_score: number
  panchang_sign: string
  chain_sign: string
  agreement: string
  conviction: 'high' | 'medium' | 'low'
  parts: Record<string, number>
  star_lord: string
  amplified: boolean
  chidra: boolean
}

export interface Prediction {
  status: string
  summary: string[]
  note: string
  sections?: Record<string, RuleFinding[]>
  graph_segments?: GraphSegment[]
  chain?: PredictionChain
  day_score?: DayScore
}

export interface TransitRow {
  deg: string
  rasi_lord: string
  rasi_lord_ta: string
  nak_lord: string
  nak_lord_ta: string
  sub_lord: string
  sub_lord_ta: string
  time: string
  graha?: string
  graha_ta?: string
}

export interface PanchangEnd {
  num: number
  name: string
  name_ta?: string
  ends: string | null
}

export interface PlanetPositionRow {
  planet: string
  deg: string
  house: number
  retro: boolean
  rasi_lord: string
  nak_lord: string
  sub_lord: string
}

export interface PlanetPositionSheet {
  rows: PlanetPositionRow[]
  chain: { x: string; y: string }
  chain_text: string[]
  cast?: string
  day_lord: { en: string; ta: string }
}

/** One body as the author's chart prints it: abbreviation, DD.MM degree,
 *  and the star/sub lords that appear in the ring outside the grid. */
export interface ChartBody {
  name: string
  short: string
  deg: string
  retro: boolean
  star_lord: string
  sub_lord: string
  star_short: string
  sub_short: string
}

export interface ChartCell {
  sign: number
  rasi: string
  rasi_ta: string
  items: ChartBody[]
}

export interface KpDayChart {
  vaara: string
  day_lord: { en: string; ta: string }
  planet_position?: PlanetPositionSheet
  // KP-ayanamsa positions for this tab's own rasi chart — distinct from
  // the top-level Lahiri `grahas`/`lagna` the Jothidam tab draws
  grahas?: Graha[]
  lagna?: Lagna
  ayanamsa?: number
  cells?: ChartCell[]
  panchang_ends: {
    thithi: PanchangEnd
    natchathiram: PanchangEnd
    yogam: PanchangEnd
    karanam: PanchangEnd
  }
  // optional: /api/panchang-chart omits these (nothing displays them),
  // but transit.day_chart can still produce them
  moon_transits?: TransitRow[]
  planet_transits?: TransitRow[]
}

export interface ComputeResult {
  input: { date: string; time: string; tz_offset: number; lat: number; lon: number }
  ayanamsa: number
  lagna: Lagna
  grahas: Graha[]
  chart: string[][]
  panchang: Panchang
  prediction: Prediction
  kp?: KpDayChart
}

export interface CanTradeResult {
  birth_rasi: { en: string; ta: string }
  transit_rasi: { en: string; ta: string }
  count: number
  verdict: 'AVOID' | 'FAVOURABLE' | 'OK'
  note: string
  cast: string          // sunrise HH:MM — the moment the chart is cast
  rasi_until: string
  source: string
}

export interface ComputeRequest {
  year: number
  month: number
  day: number
  hour: number
  minute: number
  tz_offset: number
  lat: number
  lon: number
}

export interface PrasanamSeed {
  number: number
  start: number
  end: number
  asc: number
  rasi: string
  nakshatra: string
  star_lord: string
  sub_lord: string
}

export interface PrasanamResult {
  number: number
  seed: PrasanamSeed
  findings: RuleFinding[]
  note: string
}

// GET /api/gann-calendar — the tropical Gann cosmogram layer

export interface GannEvent {
  date: string
  end_date: string | null
  rule_id: string
  title: string
  kind: 'transit' | 'natal' | 'natal-cross' | 'station' | 'pattern'
  angle: number | null
  detail: string
  direction: string
  // bullish/bearish = his fixed-direction calls; reversal = flips the
  // prior trend, so it has no fixed direction (rendered amber, not
  // green/red)
  bias: 'bullish' | 'bearish' | 'reversal'
  timing: string
  verdict: 'paper-trade' | 'lean' | 'null' | 'rare' | 'calendar-trap'
  evidence: string
  source: string
  retro: string[]
  excluded: boolean
  market_note: string | null
}

export interface GannCalendarResult {
  center: string
  start: string
  end: string
  radix: { date: string; positions: Record<string, number> }
  base_rates: Record<string, string>
  events: GannEvent[]
  note: string
}

// ---- Saptarsh Insight–style week outlook (/api/saptarsh-week) ----
export type SaptarshTone = 'bull' | 'bear' | 'vol' | 'neutral'
export type SaptarshSource = 'observed' | 'extrapolated'

export interface SaptarshAspect {
  time: string
  et: string
  a: string
  angle: number
  b: string
  name: string
  tone: SaptarshTone
  source: SaptarshSource
  in_session: boolean
}

export interface SaptarshCall {
  tone: SaptarshTone
  source: SaptarshSource
  why: string[]
  caution: string[]
  text: string
}

export interface SaptarshDay {
  date: string
  weekday: string
  closed: string | null
  moon: {
    sign: string
    sign_en: string
    nakshatra: string
    pada: number
    sign_change: { time: string; to: string } | null
    nakshatra_change: { time: string; to: string } | null
  }
  panchang: {
    tithi: string
    tithi_num: number
    tithi_ends: string | null
    nakshatra_ends: string | null
    yoga: string
    yoga_ends: string | null
    karanas: { name: string; ends: string | null }[]
    vaar_tithi: { names: string[]; tone: SaptarshTone; source: 'classical' } | null
  }
  kaal: {
    sunrise: string
    sunset: string
    rahu_kaal: [string, string]
    yamaganda: [string, string]
    gulika_kaal: [string, string]
    abhijit: [string, string]
  }
  aspects: SaptarshAspect[]
  eclipse: string | null
  flags: string[]
  calls: Record<'nifty' | 'gold' | 'silver', SaptarshCall>
  windows: { start: string; end: string; tone: SaptarshTone; driver: string }[]
  metal_windows: {
    start: string; end: string; start_et: string; end_et: string
    tone: SaptarshTone; driver: string
  }[]
}

export interface SaptarshRegime {
  as_of: string
  jupiter: { sign: string; sign_en: string; entry: string; exit: string; nakshatra: string }
  sun_ketu_same_sign: boolean
  conjunctions: {
    sign: string; sign_en: string; planets: string[]; until: string
    members: { planet: string; entry: string; exit: string }[]
  }[]
  notes: string[]
  jupiter_cancer_history: {
    entry: string; exit: string; days: number; gold_pct: number; silver_pct: number
  }[]
}

export interface SaptarshWeekResult {
  start: string
  end: string
  days: SaptarshDay[]
  regime: SaptarshRegime
  note: string
}
