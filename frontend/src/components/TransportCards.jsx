const MODE_META = {
  driving:  { icon: '🚗', label: 'Araçla'          },
  transit:  { icon: '🚇', label: 'Toplu Taşıma'    },
  walking:  { icon: '🚶', label: 'Yürüyerek'        },
  cycling:  { icon: '🚲', label: 'Bisikletle'       },
  flight:   { icon: '✈️', label: 'Uçuşla'           },
  best:     { icon: '🗺️', label: 'Önerilen Rota'    },
  rota:     { icon: '🗺️', label: 'Rota'             },
}

function getMeta(via = '') {
  const lower = via.toLowerCase()
  for (const [key, val] of Object.entries(MODE_META)) {
    if (lower.startsWith(key)) return val
  }
  // "Driving — Via A1" → eşleşme bulamazsa ilk kelime
  const first = lower.split(/[\s—-]/)[0]
  return MODE_META[first] || { icon: '🗺️', label: via.split(' — ')[0] || 'Rota' }
}

function formatDur(mins) {
  if (!mins || mins <= 0) return null
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return h > 0 ? `${h} sa ${m} dk` : `${m} dk`
}

export default function TransportCards({ options, onSelect, origin, destination }) {
  // Maksimum 3 seçenek, düzgün data olanları öne al
  const sorted = [...options]
    .sort((a, b) => (b.duration_minutes || 0) - (a.duration_minutes || 0) === 0
      ? 0 : (b.maps_url ? 1 : -1))
    .slice(0, 3)

  // Eğer hiç seçenek yoksa en azından 3 fallback oluştur
  const cards = sorted.length > 0 ? sorted : [
    { via: 'Driving', duration_minutes: 0, maps_url: buildMapsUrl(origin, destination, 'driving') },
    { via: 'Transit', duration_minutes: 0, maps_url: buildMapsUrl(origin, destination, 'transit') },
    { via: 'Walking', duration_minutes: 0, maps_url: buildMapsUrl(origin, destination, 'walking') },
  ]

  return (
    <div className="transport-grid">
      {cards.map((t, i) => {
        const { icon, label } = getMeta(t.via || '')
        const dur = formatDur(Number(t.duration_minutes) || 0)
        // "Driving — Via A1" → detay kısmı
        const routeDetail = (t.via || '').includes(' — ')
          ? (t.via || '').split(' — ').slice(1).join(' — ')
          : ''

        return (
          <div key={i} className="transport-card-new">
            <div className="tc-header">
              <span className="tc-icon">{icon}</span>
              <div className="tc-title-block">
                <p className="tc-mode">{label}</p>
                {routeDetail && <p className="tc-route-detail">{routeDetail}</p>}
              </div>
              {dur && <span className="tc-duration">{dur}</span>}
            </div>

            {(origin || destination) && (
              <p className="tc-route">
                {origin && <span>{origin}</span>}
                {origin && destination && <span className="tc-arrow"> → </span>}
                {destination && <span>{destination}</span>}
              </p>
            )}

            {t.steps?.length > 0 && (
              <ul className="tc-steps">
                {t.steps.slice(0, 3).map((s, j) => <li key={j}>{s}</li>)}
              </ul>
            )}

            <div className="tc-actions">
              {t.maps_url ? (
                <a
                  href={t.maps_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="tc-maps-btn"
                  onClick={e => e.stopPropagation()}
                >
                  🗺️ Google Maps'te Gör →
                </a>
              ) : (
                <a
                  href={buildMapsUrl(origin, destination, (t.via || '').split(' ')[0].toLowerCase())}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="tc-maps-btn"
                  onClick={e => e.stopPropagation()}
                >
                  🗺️ Google Maps'te Gör →
                </a>
              )}
              <button className="tc-select-btn" onClick={() => onSelect(t)}>
                Bu Rotayı Seç →
              </button>
            </div>

            {t.price != null && (
              <p className="tc-price">₺{Number(t.price).toLocaleString('tr-TR')}</p>
            )}
          </div>
        )
      })}
    </div>
  )
}

function buildMapsUrl(origin = '', destination = '', mode = '') {
  const o = encodeURIComponent(origin)
  const d = encodeURIComponent(destination)
  const modeMap = { driving: 'driving', transit: 'transit', walking: 'walking', cycling: 'bicycling' }
  const m = modeMap[mode] || 'driving'
  return `https://www.google.com/maps/dir/?api=1&origin=${o}&destination=${d}&travelmode=${m}`
}
