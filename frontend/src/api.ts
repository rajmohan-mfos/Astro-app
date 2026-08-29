import type {
  CanTradeResult, ComputeRequest, ComputeResult, GannCalendarResult,
  PrasanamResult, SaptarshWeekResult, VolatilityResult,
} from './types'

/** Cosmogram aspect calendar around a date (tropical Gann layer). */
export async function gannCalendar(
  date?: string,
): Promise<GannCalendarResult> {
  const qs = date ? `?date=${date}` : ''
  const res = await fetch(`/api/gann-calendar${qs}`)
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}

/** Cast the taught KP horary chart from a seed number 1–249. */
export async function prasanam(
  req: ComputeRequest, number: number,
): Promise<PrasanamResult> {
  const res = await fetch('/api/prasanam', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...req, number }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export async function canTrade(
  birth: ComputeRequest,
  on: { year: number; month: number; day: number; tz_offset: number },
): Promise<CanTradeResult> {
  const res = await fetch('/api/can-trade', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ birth, ...on }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}

// /api/panchang-chart = /api/compute plus the KP day-chart tables (`kp`)
export async function compute(req: ComputeRequest): Promise<ComputeResult> {
  const res = await fetch('/api/panchang-chart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export async function health(): Promise<{ ok: boolean }> {
  const res = await fetch('/api/health')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

/** Saptarsh Insight–style Nifty/Gold/Silver outlook, one entry per day. */
export async function saptarshWeek(
  date?: string, days = 7,
): Promise<SaptarshWeekResult> {
  const qs = `?days=${days}${date ? `&date=${date}` : ''}`
  const res = await fetch(`/api/saptarsh-week${qs}`)
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}

/** The volatility model alone — session width, ~60% OOS, no direction. */
export async function volatility(): Promise<VolatilityResult> {
  const res = await fetch('/api/volatility')
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}
