export default function HotelCards({ hotels, nights, onSelect }) {
  if (!hotels?.length) {
    return <p style={{ color: 'var(--color-gravel)', padding: '40px 0' }}>Otel bulunamadı.</p>
  }
  return (
    <div className="results-list">
      {hotels.map((h, i) => {
        const perNight = h.price_per_night ?? 0
        const total    = h.hotel_total ?? Math.round(perNight * nights)
        const stars    = h.stars ? '★'.repeat(h.stars) : null
        const bookUrl  = h.platform_links?.['Booking.com']
        return (
          <div key={i} className="card result-card">
            <div className="rc-airline">
              {stars && <span className="rc-stars">{stars}</span>}
              {!stars && <span className="rc-fn">Otel</span>}
            </div>
            <div className="rc-body">
              <div className="hc-info">
                <p className="hc-name">{h.name}</p>
                {h.rating != null && (
                  <p className="rc-sub" style={{ color: 'var(--color-slate)', fontSize: 12 }}>
                    Puan: <strong>{h.rating}</strong> / 10
                  </p>
                )}
                {h.venue_distance_km != null && (
                  <p className="rc-sub">📍 Toplantı yerine {h.venue_distance_km} km</p>
                )}
                {h.airport_distance_km != null && (
                  <p className="rc-sub">✈ Havalimanına {h.airport_distance_km} km</p>
                )}
                {h.amenities?.length > 0 && (
                  <p className="rc-sub">{h.amenities.slice(0, 4).join(' · ')}</p>
                )}
                {bookUrl && (
                  <div style={{ marginTop: 10 }}>
                    <a href={bookUrl} target="_blank" rel="noopener noreferrer"
                      className="platform-book-btn"
                      style={{ background: '#003580' }}>
                      Booking.com
                    </a>
                  </div>
                )}
              </div>
              <div className="rc-action">
                <div style={{ textAlign: 'right' }}>
                  <span className="rc-price">₺{Number(perNight).toLocaleString('tr-TR')}/gece</span>
                  {total > 0 && (
                    <p style={{ fontSize: 12, color: 'var(--color-gravel)', marginTop: 2 }}>
                      Toplam ₺{Number(total).toLocaleString('tr-TR')} · {nights} gece
                    </p>
                  )}
                </div>
                <button className="btn-primary" style={{ height: 36, padding: '0 20px', fontSize: 13 }}
                  onClick={() => onSelect(h)}>
                  Seç →
                </button>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
