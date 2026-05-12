const AIRPORT_NAMES = {
  IST:'İstanbul Atatürk Havalimanı', SAW:'İstanbul Sabiha Gökçen Havalimanı',
  ESB:'Ankara Esenboğa Havalimanı', ADB:'İzmir Adnan Menderes Havalimanı',
  AYT:'Antalya Havalimanı', TZX:'Trabzon Havalimanı', GZT:'Gaziantep Havalimanı',
  LHR:'London Heathrow Airport', LGW:'London Gatwick Airport',
  CDG:'Paris Charles de Gaulle Airport', ORY:'Paris Orly Airport',
  FRA:'Frankfurt Airport', MUC:'Munich Airport', BER:'Berlin Brandenburg Airport',
  HAM:'Hamburg Airport', DUS:'Düsseldorf Airport', STR:'Stuttgart Airport',
  CGN:'Cologne Bonn Airport', AMS:'Amsterdam Schiphol Airport',
  BRU:'Brussels Airport', CPH:'Copenhagen Airport', ARN:'Stockholm Arlanda Airport',
  OSL:'Oslo Airport', HEL:'Helsinki Airport',
  MAD:'Madrid Barajas Airport', BCN:'Barcelona El Prat Airport',
  LIS:'Lisbon Airport', FCO:'Rome Fiumicino Airport', CIA:'Rome Ciampino Airport',
  MXP:'Milan Malpensa Airport', VCE:'Venice Marco Polo Airport',
  VIE:'Vienna Airport', ZRH:'Zurich Airport', GVA:'Geneva Airport',
  DUB:'Dublin Airport', WAW:'Warsaw Chopin Airport', PRG:'Prague Airport',
  BUD:'Budapest Airport', ATH:'Athens Airport',
  DXB:'Dubai International Airport', AUH:'Abu Dhabi Airport', DOH:'Doha Hamad Airport',
  JFK:'New York JFK Airport', LAX:'Los Angeles Airport', SFO:'San Francisco Airport',
  ORD:'Chicago O\'Hare Airport', NRT:'Tokyo Narita Airport', ICN:'Seoul Incheon Airport',
  SIN:'Singapore Changi Airport', BKK:'Bangkok Suvarnabhumi Airport',
  SYD:'Sydney Airport', MEL:'Melbourne Airport',
}

const TRANSPORT_OPTIONS = [
  { mode: 'driving', label: 'Taksi / Araç',    icon: '🚕' },
  { mode: 'transit', label: 'Toplu Taşıma',    icon: '🚇' },
  { mode: 'walking', label: 'Yürüyerek',       icon: '🚶' },
]

function mapsUrl(origin, destLat, destLon, hotelName, destCity, mode) {
  const org = encodeURIComponent(origin)
  const dst = (destLat && destLon)
    ? `${destLat},${destLon}`
    : encodeURIComponent(`${hotelName}, ${destCity}`)
  return `https://www.google.com/maps/dir/?api=1&origin=${org}&destination=${dst}&travelmode=${mode}`
}

export default function SummaryCard({ flight, hotel, hotelNights = 1, destCity = '', onRestart }) {
  const flightCost    = flight?.price ?? 0
  const hotelPerNight = hotel?.price_per_night ?? 0
  // Önce backend'in hesapladığı hotel_total'i kullan, yoksa hesapla
  const hotelCost     = hotel?.hotel_total || Math.round(hotelPerNight * hotelNights)
  const total         = flightCost + hotelCost

  const hotelLinks    = hotel?.platform_links || {}
  const arrAirport    = flight?.destination ?? ''
  const airportName   = AIRPORT_NAMES[arrAirport] || `${arrAirport} Havalimanı`

  return (
    <div className="summary-container">
      <div className="summary-card card">
        <p className="eyebrow">Rezervasyon Özeti</p>
        <h2 className="section-heading" style={{ marginBottom: 32 }}>Seçimleriniz hazır.</h2>

        <div className="summary-blocks" style={{ gridTemplateColumns: '1fr auto 1fr' }}>
          {/* Uçuş */}
          <div className="summary-block">
            <p className="label-small">✈ Uçuş</p>
            <p className="summary-value">{flight?.airline ?? '—'}</p>
            <p className="summary-sub">{flight?.flight_no} · {flight?.origin} → {flight?.destination}</p>
            <p className="summary-sub">
              {String(flight?.departure_time ?? '').slice(-5)} → {String(flight?.arrival_time ?? '').slice(-5)}
            </p>
            <p className="summary-sub">
              {flight?.stops === 0 ? 'Direkt' : `${flight?.stops} aktarma`}
            </p>
            <p className="summary-price">₺{Number(flightCost).toLocaleString('tr-TR')}</p>
            {flight?.booking_url && (
              <a href={flight.booking_url} target="_blank" rel="noopener noreferrer" className="summary-link">
                Uçuş Rezervasyonu →
              </a>
            )}
          </div>

          <div className="summary-divider" />

          {/* Otel */}
          <div className="summary-block">
            <p className="label-small">🏨 Otel</p>
            <p className="summary-value">{hotel?.name ?? '—'}</p>
            {hotel?.stars > 0 && (
              <p className="summary-sub" style={{ color: '#c9a227', letterSpacing: 1 }}>
                {'★'.repeat(hotel.stars)}
              </p>
            )}
            {hotel?.venue_distance_km != null && (
              <p className="summary-sub">📍 Toplantı yerine {hotel.venue_distance_km} km</p>
            )}
            {hotel?.airport_distance_km != null && (
              <p className="summary-sub">✈ Havalimanına {hotel.airport_distance_km} km</p>
            )}
            <p className="summary-price">₺{Number(hotelCost).toLocaleString('tr-TR')} toplam</p>
            <p style={{ fontSize: 12, color: 'var(--color-gravel)', marginTop: 2 }}>
              ₺{Number(hotelPerNight).toLocaleString('tr-TR')}/gece · {hotelNights} gece
            </p>
            {Object.keys(hotelLinks).length > 0 && (
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 10 }}>
                {Object.entries(hotelLinks).map(([platform, url]) => url && (
                  <a key={platform} href={url} target="_blank" rel="noopener noreferrer"
                    className="platform-book-btn" style={{ background: '#003580', fontSize: 11 }}>
                    {platform}
                  </a>
                ))}
              </div>
            )}
          </div>
        </div>

        {total > 0 && (
          <div className="summary-total">
            <span>Toplam tahmini tutar</span>
            <span className="total-amount">₺{total.toLocaleString('tr-TR')}</span>
          </div>
        )}

        {/* Ulaşım */}
        {arrAirport && hotel?.name && (
          <div className="transport-section">
            <p className="label-small" style={{ marginBottom: 12 }}>
              🗺 Havalimanından Otele Ulaşım
            </p>
            <p className="transport-route-label">
              {airportName} → {hotel.name}
            </p>
            <div className="transport-options">
              {TRANSPORT_OPTIONS.map(({ mode, label, icon }) => (
                <a key={mode}
                  href={mapsUrl(airportName, hotel.latitude, hotel.longitude, hotel.name, destCity, mode)}
                  target="_blank" rel="noopener noreferrer"
                  className="transport-btn">
                  <span className="transport-icon">{icon}</span>
                  <span>{label}</span>
                  <span className="transport-arrow">→</span>
                </a>
              ))}
            </div>
          </div>
        )}

        <button className="btn-primary" onClick={onRestart} style={{ marginTop: 28 }}>
          Yeni Arama
        </button>
      </div>
    </div>
  )
}
