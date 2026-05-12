import { useState } from 'react'

const CABIN_OPTIONS = [
  { value: 'ekonomi', label: 'Ekonomi' },
  { value: 'business', label: 'Business' },
  { value: 'first class', label: 'First Class' },
]

export default function SeedForm({ onSubmit }) {
  const [form, setForm] = useState({
    origin: '', destination: '', date: '', adults: 1, children: 0,
    cabin: 'ekonomi', budget: '', airlineMin: '', airlineMax: '', preferredAirline: '',
  })
  const [showOptional, setShowOptional] = useState(false)
  const set = (k, v) => setForm(p => ({ ...p, [k]: v }))

  const handleSubmit = (e) => {
    e.preventDefault()
    const parts = [
      `${form.origin}'dan ${form.destination}'a`,
      form.date,
      `${form.adults} yetişkin`,
    ]
    if (form.children > 0)         parts.push(`${form.children} çocuk`)
    if (form.cabin !== 'ekonomi')  parts.push(form.cabin + ' sınıfı')
    if (form.budget)               parts.push(`maksimum ${form.budget} TRY bütçe`)
    if (form.airlineMin)           parts.push(`en erken kalkış ${form.airlineMin}`)
    if (form.airlineMax)           parts.push(`en geç kalkış ${form.airlineMax}`)
    if (form.preferredAirline)     parts.push(`tercih edilen havayolu ${form.preferredAirline}`)
    onSubmit(parts.join(', ') + ' uçuşu ara', {
      origin: form.origin, destination: form.destination,
      date: form.date, adults: form.adults, children: form.children,
    })
  }

  return (
    <form className="form-card" onSubmit={handleSubmit}>
      {/* Zorunlu alanlar */}
      <div className="form-grid form-grid-2">
        <div className="form-field">
          <label className="form-label">Nereden</label>
          <input className="form-input" placeholder="İstanbul" value={form.origin}
            onChange={e => set('origin', e.target.value)} required />
        </div>
        <div className="form-field">
          <label className="form-label">Nereye</label>
          <input className="form-input" placeholder="Paris" value={form.destination}
            onChange={e => set('destination', e.target.value)} required />
        </div>
      </div>

      <div className="form-grid form-grid-2" style={{ marginTop: 20 }}>
        <div className="form-field">
          <label className="form-label">Gidiş Tarihi</label>
          <input className="form-input" type="date" value={form.date}
            onChange={e => set('date', e.target.value)} required />
        </div>
        <div className="form-field">
          <label className="form-label">Kabin Sınıfı</label>
          <select className="form-input" value={form.cabin} onChange={e => set('cabin', e.target.value)}>
            {CABIN_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
      </div>

      <div className="form-grid form-grid-2" style={{ marginTop: 20 }}>
        <div className="form-field">
          <label className="form-label">Yetişkin</label>
          <div className="passenger-stepper">
            <button type="button" className="stepper-btn" disabled={form.adults <= 1}
              onClick={() => set('adults', form.adults - 1)}>−</button>
            <span className="stepper-value">{form.adults}</span>
            <button type="button" className="stepper-btn" disabled={form.adults >= 9}
              onClick={() => set('adults', form.adults + 1)}>+</button>
          </div>
        </div>
        <div className="form-field">
          <label className="form-label">Çocuk</label>
          <div className="passenger-stepper">
            <button type="button" className="stepper-btn" disabled={form.children <= 0}
              onClick={() => set('children', form.children - 1)}>−</button>
            <span className="stepper-value">{form.children}</span>
            <button type="button" className="stepper-btn" disabled={form.children >= 8}
              onClick={() => set('children', form.children + 1)}>+</button>
          </div>
        </div>
      </div>

      {/* Opsiyonel alanlar */}
      <div style={{ marginTop: 24, borderTop: '1px solid var(--color-chalk)', paddingTop: 20 }}>
        <button type="button" className="optional-toggle"
          onClick={() => setShowOptional(v => !v)}>
          {showOptional ? '▲ Opsiyonel filtreleri gizle' : '▼ Opsiyonel filtreler (bütçe, saat, havayolu)'}
        </button>

        {showOptional && (
          <div className="optional-panel">
            <div className="form-grid form-grid-3">
              <div className="form-field">
                <label className="form-label">Maks Bütçe (TRY)</label>
                <input className="form-input" type="number" placeholder="örn. 10000"
                  value={form.budget} onChange={e => set('budget', e.target.value)} />
              </div>
              <div className="form-field">
                <label className="form-label">En Erken Kalkış</label>
                <input className="form-input" type="time" value={form.airlineMin}
                  onChange={e => set('airlineMin', e.target.value)} />
              </div>
              <div className="form-field">
                <label className="form-label">En Geç Kalkış</label>
                <input className="form-input" type="time" value={form.airlineMax}
                  onChange={e => set('airlineMax', e.target.value)} />
              </div>
            </div>
            <div className="form-field" style={{ marginTop: 16 }}>
              <label className="form-label">Tercih Edilen Havayolu</label>
              <input className="form-input" placeholder="örn. Turkish Airlines"
                value={form.preferredAirline} onChange={e => set('preferredAirline', e.target.value)} />
            </div>
          </div>
        )}
      </div>

      <div className="form-actions">
        <button className="btn-primary" type="submit">Uçuş Ara →</button>
      </div>
    </form>
  )
}
