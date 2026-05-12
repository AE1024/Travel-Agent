const PLATFORM_COLORS = {
  'Booking.com': '#003580',
}

function FlightRow({ flight }) {
  const stops = flight?.stops === 0 ? 'Direkt' : `${flight?.stops} aktarma`
  const dep = String(flight?.departure_time ?? '').slice(-5)
  const arr = String(flight?.arrival_time ?? '').slice(-5)
  return (
    <div className="pkg-col">
      <p className="label-small">✈ Uçuş</p>
      <p className="pkg-name">{flight?.airline ?? '—'}</p>
      <p className="pkg-sub">{flight?.flight_no} · {flight?.origin} → {flight?.destination}</p>
      <p className="pkg-sub">{dep} → {arr} · {stops}</p>
      <p className="pkg-price">₺{Number(flight?.price ?? 0).toLocaleString('tr-TR')}</p>
    </div>
  )
}

function HotelRow({ hotel, nights }) {
  const perNight = hotel?.price_per_night ?? 0
  const links = hotel?.platform_links || {}
  const stars = hotel?.stars ? '★'.repeat(hotel.stars) : ''
  return (
    <div className="pkg-col">
      <p className="label-small">🏨 Otel</p>
      <p className="pkg-name">{hotel?.name ?? '—'}</p>
      {stars && <p className="pkg-sub" style={{ color: '#f5a623', letterSpacing: 1 }}>{stars}</p>}
      {hotel?.venue_distance_km != null && (
        <p className="pkg-sub">Toplantı yerine {hotel.venue_distance_km} km</p>
      )}
      {hotel?.airport_distance_km != null && (
        <p className="pkg-sub">Havalimanına {hotel.airport_distance_km} km</p>
      )}
      <p className="pkg-price">₺{Number(perNight).toLocaleString('tr-TR')}/gece</p>
      {Object.keys(links).length > 0 && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 8 }}>
          {Object.entries(links).map(([platform, url]) => (
            <a key={platform} href={url} target="_blank" rel="noopener noreferrer"
              className="platform-book-btn"
              style={{ background: PLATFORM_COLORS[platform] || '#333' }}>
              {platform}
            </a>
          ))}
        </div>
      )}
    </div>
  )
}

export default function PackageCards({ packages, onSelect }) {
  if (!packages?.length) {
    return <p style={{ color: 'var(--color-gravel)', padding: '40px 0' }}>Paket bulunamadı.</p>
  }
  return (
    <div className="packages-list">
      {packages.map((pkg, i) => (
        <div key={i} className="card package-card">
          <p className="package-rank">#{i + 1} Paket</p>
          <div className="package-body">
            <FlightRow flight={pkg.flight} />
            <div className="pkg-divider" />
            <HotelRow hotel={pkg.hotel} nights={pkg.nights ?? 1} />
          </div>
          <div className="pkg-footer">
            <div className="pkg-total">
              Toplam tahmini &nbsp;
              <strong>₺{Number(pkg.total_price ?? 0).toLocaleString('tr-TR')}</strong>
              <span style={{ fontSize: 12, marginLeft: 6, color: 'var(--color-gravel)' }}>
                ({pkg.nights} gece)
              </span>
            </div>
            <button className="btn-primary" style={{ height: 38, fontSize: 13 }}
              onClick={() => onSelect(pkg)}>
              Bu Paketi Seç →
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
