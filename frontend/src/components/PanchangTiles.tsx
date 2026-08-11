import type { Panchang } from '../types'

export default function PanchangTiles({ panchang }: { panchang: Panchang }) {
  const { vaara, thithi, natchathiram, yogam, karanam } = panchang

  return (
    <div className="tiles">
      <div className="tile">
        <div className="tile-label">Vaara</div>
        <div className="tile-main">{vaara.ta}</div>
        <div className="tile-sub">{vaara.en}</div>
      </div>
      <div className="tile">
        <div className="tile-label">Thithi</div>
        <div className="tile-main">{thithi.name}</div>
        <div className="tile-sub">{thithi.paksha} · #{thithi.num}</div>
      </div>
      <div className="tile">
        <div className="tile-label">Natchathiram</div>
        <div className="tile-main">{natchathiram.name_ta}</div>
        <div className="tile-sub">
          {natchathiram.name} · pada {natchathiram.pada}
        </div>
      </div>
      <div className="tile">
        <div className="tile-label">Yogam</div>
        <div className="tile-main">{yogam.name}</div>
        <div className="tile-sub">#{yogam.num}</div>
      </div>
      <div className="tile">
        <div className="tile-label">Karanam</div>
        <div className="tile-main">{karanam.name}</div>
        <div className="tile-sub">#{karanam.num}</div>
      </div>
    </div>
  )
}
