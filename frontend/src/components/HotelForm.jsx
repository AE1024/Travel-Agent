import { useState } from 'react'

const AMENITY_OPTIONS = [
  { value: 'free_wifi',      label: 'WiFi' },
  { value: 'pool',           label: 'Havuz' },
  { value: 'spa',            label: 'Spa' },
  { value: 'gym',            label: 'Spor Salonu' },
  { value: 'free_breakfast', label: 'Kahvaltı' },
  { value: 'free_parking',   label: 'Otopark' },
]

export default function HotelForm({ flight, searchParams, onSubmit }) {
  const adults   = searchParams?.adults   ?? 1
  const children = searchParams?.children ?? 0

  const [nights,      setNights]      = useState(3)
  const [stars,       setStars]       = useState('')
  const [budget,      setBudget]      = useState('')
  const [sortBy,      setSortBy]      = useState('')
  const [amenities,   setAmenities]   = useState([])
  const [nearAirport, setNearAirport] = useState(false)
  const [showOptional, setShowOptional] = useState(false)

  const toggleAmenity = (val) =>
    setAmenities(prev => prev.includes(val) ? prev.filter(a => a !== val) : [...prev, val])

  const handleSubmit = (e) => {
    e.preventDefault()
    const parts = [`${nights} gece`]
    if (adults > 1 || children > 0) {
      parts.push(`${adults} yetişkin${children > 0 ? `, ${children} çocuk` : ''}`)
    }
    if (stars)      parts.push(`minimum ${stars} yıldız`)
    if (budget)     parts.push(`gecelik maksimum ${budget} TRY`)
    if (sortBy)     parts.push(sortBy === 'price' ? 'fiyata göre sırala' : 'puana göre sırala')
    if (nearAirport) parts.push('havalimanına yakın otel')
    if (amenities.length > 0) {
      const labels = amenities.map(v => AMENITY_OPTIONS.find(o => o.value === v)?.label ?? v)
      parts.push(labels.join(', ') + ' olsun')
    }
    onSubmit(parts.join(', ') + ' otel ara', { nights })
  }

  return (
    <form className="form-card" onSubmit={handleSubmit}>
      {flight && (
        <div className="flight-summary-banner" style={{ marginBottom: 24 }}>
          <span>✈ {flight.airline} {flight.flight_no}</span>
          <div className="banner-sep" />
          <span>{flight.origin} → {flight.destination}</span>
          <div className="banner-sep" />
          <span>{String(flight.departure_time).slice(0, 10)}</span>
        </div>
      )}

      <div className="form-grid form-grid-2">
        <div className="form-field">
          <label className="form-label">Gece Sayısı</label>
          <div className="passenger-stepper">
            <button type="button" className="stepper-btn" disabled={nights <= 1}
              onClick={() => setNights(n => n - 1)}>−</button>
            <span className="stepper-value">{nights}</span>
            <button type="button" className="stepper-btn" disabled={nights >= 30}
              onClick={() => setNights(n => n + 1)}>+</button>
          </div>
        </div>
        <div className="form-field">
          <label className="form-label">Yolcu</label>
          <div className="form-input" style={{ display: 'flex', alignItems: 'center',
            color: 'var(--color-gravel)', fontSize: 14, cursor: 'default' }}>
            {adults} yetişkin{children > 0 ? `, ${children} çocuk` : ''}
            <span style={{ fontSize: 11, marginLeft: 8, opacity: 0.6 }}>(uçuştan)</span>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 24, borderTop: '1px solid var(--color-chalk)', paddingTop: 20 }}>
        <button type="button" className="optional-toggle"
          onClick={() => setShowOptional(v => !v)}>
          {showOptional ? '▲ Opsiyonel filtreleri gizle' : '▼ Opsiyonel filtreler (yıldız, bütçe, sıralama)'}
        </button>

        {showOptional && (
          <div className="optional-panel">
            <div className="form-grid form-grid-3">
              <div className="form-field">
                <label className="form-label">Min Yıldız</label>
                <select className="form-input" value={stars} onChange={e => setStars(e.target.value)}>
                  <option value="">Fark etmez</option>
                  <option value="3">3 yıldız ve üzeri</option>
                  <option value="4">4 yıldız ve üzeri</option>
                  <option value="5">5 yıldız</option>
                </select>
              </div>
              <div className="form-field">
                <label className="form-label">Maks Bütçe (TRY/gece)</label>
                <input className="form-input" type="number" placeholder="örn. 3000"
                  value={budget} onChange={e => setBudget(e.target.value)} />
              </div>
              <div className="form-field">
                <label className="form-label">Sıralama</label>
                <select className="form-input" value={sortBy} onChange={e => setSortBy(e.target.value)}>
                  <option value="">Varsayılan</option>
                  <option value="price">Fiyat (düşük → yüksek)</option>
                  <option value="rating">Puan (yüksek → düşük)</option>
                </select>
              </div>
            </div>

            <div className="form-field" style={{ marginTop: 16 }}>
              <label className="form-label">Özellikler</label>
              <div className="toggle-group" style={{ flexWrap: 'wrap', marginTop: 6 }}>
                {AMENITY_OPTIONS.map(o => (
                  <button key={o.value} type="button"
                    className={`toggle-pill${amenities.includes(o.value) ? ' active' : ''}`}
                    onClick={() => toggleAmenity(o.value)}>
                    {o.label}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginTop: 16 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8,
                fontSize: 13, color: 'var(--color-obsidian)', cursor: 'pointer' }}>
                <input type="checkbox" checked={nearAirport}
                  onChange={e => setNearAirport(e.target.checked)} />
                Havalimanına yakın otel
              </label>
            </div>
          </div>
        )}
      </div>

      <div className="form-actions">
        <button className="btn-primary" type="submit">Otel Ara →</button>
      </div>
    </form>
  )
}
