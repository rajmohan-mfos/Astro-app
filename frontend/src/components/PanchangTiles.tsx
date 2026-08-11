import type { Panchang, PanchangEnd } from '../types'

type Ends = {
  thithi: PanchangEnd
  natchathiram: PanchangEnd
  yogam: PanchangEnd
  karanam: PanchangEnd
}

/** The five panchang elements, shown ONCE.
 *
 *  This used to render twice — a names-only version in the Jothidam tab
 *  and a with-end-times version in the KP tab — and neither was a superset
 *  of the other (the tiles carried paksha, element numbers and the pada;
 *  the KP block carried end times and the day lord). They are merged here
 *  so every field survives in a single block.
 */
export default function PanchangTiles({ panchang, ends, dayLord }: {
  panchang: Panchang
  ends?: Ends
  dayLord?: { en: string; ta: string }
}) {
  const { vaara, thithi, natchathiram, yogam, karanam } = panchang
  const at = (e?: PanchangEnd) =>
    ends && e ? <div className="tile-ends">ends {e.ends ?? '—'}</div> : null

  return (
    <div className="tiles">
      <div className="tile">
        <div className="tile-label">Vaara · வாரம்</div>
        <div className="tile-main">{vaara.ta}</div>
        <div className="tile-sub">{vaara.en}</div>
        {dayLord && <div className="tile-ends">அதிபதி {dayLord.ta}</div>}
      </div>
      <div className="tile">
        <div className="tile-label">Thithi · திதி</div>
        <div className="tile-main">{thithi.name}</div>
        <div className="tile-sub">{thithi.paksha} · #{thithi.num}</div>
        {at(ends?.thithi)}
      </div>
      <div className="tile">
        <div className="tile-label">Natchathiram · நட்சத்திரம்</div>
        <div className="tile-main">{natchathiram.name_ta}</div>
        <div className="tile-sub">
          {natchathiram.name} · pada {natchathiram.pada}
        </div>
        {at(ends?.natchathiram)}
      </div>
      <div className="tile">
        <div className="tile-label">Yogam · யோகம்</div>
        <div className="tile-main">{yogam.name}</div>
        <div className="tile-sub">#{yogam.num}</div>
        {at(ends?.yogam)}
      </div>
      <div className="tile">
        <div className="tile-label">Karanam · கரணம்</div>
        <div className="tile-main">{karanam.name}</div>
        <div className="tile-sub">#{karanam.num}</div>
        {at(ends?.karanam)}
      </div>
    </div>
  )
}
