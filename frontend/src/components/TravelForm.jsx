import { useState, useEffect } from 'react'

const IATA_CITIES = {
  IST:'İstanbul',SAW:'İstanbul',ESB:'Ankara',ADB:'İzmir',AYT:'Antalya',
  DLM:'Dalaman',BJV:'Bodrum',TZX:'Trabzon',GZT:'Gaziantep',
  LHR:'London',LGW:'London',STN:'London',CDG:'Paris',ORY:'Paris',
  FRA:'Frankfurt',MUC:'Münih',BER:'Berlin',HAM:'Hamburg',DUS:'Düsseldorf',
  STR:'Stuttgart',CGN:'Köln',AMS:'Amsterdam',BRU:'Brüksel',
  CPH:'Kopenhag',ARN:'Stockholm',OSL:'Oslo',HEL:'Helsinki',
  MAD:'Madrid',BCN:'Barselona',LIS:'Lizbon',OPO:'Porto',
  FCO:'Roma',MXP:'Milano',VCE:'Venedik',NAP:'Napoli',
  VIE:'Viyana',ZRH:'Zürih',GVA:'Cenevre',DUB:'Dublin',
  WAW:'Varşova',PRG:'Prag',BUD:'Budapeşte',ATH:'Atina',
  DXB:'Dubai',AUH:'Abu Dabi',DOH:'Doha',CAI:'Kahire',TLV:'Tel Aviv',
  JFK:'New York',LAX:'Los Angeles',SFO:'San Francisco',ORD:'Chicago',
  ATL:'Atlanta',MIA:'Miami',BOS:'Boston',SEA:'Seattle',LAS:'Las Vegas',
  YYZ:'Toronto',NRT:'Tokyo',ICN:'Seul',PEK:'Pekin',PVG:'Şangay',
  HKG:'Hong Kong',SIN:'Singapur',BKK:'Bangkok',KUL:'Kuala Lumpur',
  DEL:'Yeni Delhi',BOM:'Mumbai',SYD:'Sidney',MEL:'Melbourne',
}

const CITY_IATA = {
  'istanbul':'IST','i̇stanbul':'IST','ankara':'ESB','izmir':'ADB','i̇zmir':'ADB',
  'antalya':'AYT','dalaman':'DLM','bodrum':'BJV','trabzon':'TZX','gaziantep':'GZT',
  'london':'LHR','londra':'LHR','paris':'CDG',
  'frankfurt':'FRA','munich':'MUC','münchen':'MUC','munih':'MUC','münih':'MUC','berlin':'BER',
  'hamburg':'HAM','dusseldorf':'DUS','düsseldorf':'DUS','stuttgart':'STR','cologne':'CGN','köln':'CGN','koln':'CGN',
  'amsterdam':'AMS','brussels':'BRU','brüksel':'BRU','copenhagen':'CPH','kopenhag':'CPH',
  'stockholm':'ARN','oslo':'OSL','helsinki':'HEL',
  'madrid':'MAD','barcelona':'BCN','barselona':'BCN','lisbon':'LIS','lizbon':'LIS','porto':'OPO',
  'rome':'FCO','roma':'FCO','milan':'MXP','milano':'MXP','venice':'VCE','venedik':'VCE','naples':'NAP','napoli':'NAP',
  'vienna':'VIE','viyana':'VIE','wien':'VIE','zurich':'ZRH','zürih':'ZRH','zürich':'ZRH',
  'geneva':'GVA','cenevre':'GVA','dublin':'DUB',
  'warsaw':'WAW','varşova':'WAW','prague':'PRG','prag':'PRG','budapest':'BUD','budapeşte':'BUD','athens':'ATH','atina':'ATH',
  'dubai':'DXB','doha':'DOH','cairo':'CAI','kahire':'CAI',
  'new york':'JFK','los angeles':'LAX','san francisco':'SFO',
  'chicago':'ORD','atlanta':'ATL','miami':'MIA','boston':'BOS','seattle':'SEA',
  'las vegas':'LAS','toronto':'YYZ',
  'tokyo':'NRT','seoul':'ICN','seul':'ICN','beijing':'PEK','pekin':'PEK','shanghai':'PVG','şangay':'PVG',
  'hong kong':'HKG','singapore':'SIN','singapur':'SIN','bangkok':'BKK','kuala lumpur':'KUL',
  'new delhi':'DEL','yeni delhi':'DEL','mumbai':'BOM','sydney':'SYD','sidney':'SYD','melbourne':'MEL',
}

const AIRLINE_OPTIONS = [
  { value: '', label: 'Fark etmez' },
  { value: 'TK',  label: 'Turkish Airlines (THY)' },
  { value: 'PC',  label: 'Pegasus' },
  { value: 'XQ',  label: 'SunExpress' },
  { value: 'XC',  label: 'Corendon' },
  { value: 'LH',  label: 'Lufthansa' },
  { value: 'KL',  label: 'KLM' },
  { value: 'AF',  label: 'Air France' },
  { value: 'BA',  label: 'British Airways' },
  { value: 'U2',  label: 'easyJet' },
  { value: 'FR',  label: 'Ryanair' },
  { value: 'W6',  label: 'Wizz Air' },
  { value: 'LX',  label: 'Swiss' },
  { value: 'OS',  label: 'Austrian Airlines' },
  { value: 'AY',  label: 'Finnair' },
  { value: 'SK',  label: 'SAS' },
  { value: 'EK',  label: 'Emirates' },
  { value: 'QR',  label: 'Qatar Airways' },
  { value: 'EY',  label: 'Etihad' },
]

const AMENITY_OPTIONS = [
  { key: 'free_wifi',      label: 'Ücretsiz Wi-Fi' },
  { key: 'free_breakfast', label: 'Ücretsiz Kahvaltı' },
  { key: 'free_parking',   label: 'Ücretsiz Otopark' },
  { key: 'pool',           label: 'Havuz' },
  { key: 'gym',            label: 'Spor Salonu' },
  { key: 'spa',            label: 'Spa' },
  { key: 'restaurant',     label: 'Restoran' },
  { key: 'airport_shuttle',label: 'Havalimanı Servisi' },
]

function resolveInput(text) {
  if (!text || !text.trim()) return null
  const up = text.trim().toUpperCase()
  const lo = text.trim().toLowerCase()
  if (IATA_CITIES[up]) return `${IATA_CITIES[up]} (${up})`
  if (CITY_IATA[lo]) { const iata = CITY_IATA[lo]; return `${IATA_CITIES[iata] || text} (${iata})` }
  // Türkçe karakter normalize
  const norm = lo.replace(/ı/g,'i').replace(/ş/g,'s').replace(/ğ/g,'g')
    .replace(/ü/g,'u').replace(/ö/g,'o').replace(/ç/g,'c')
  if (CITY_IATA[norm]) { const iata = CITY_IATA[norm]; return `${IATA_CITIES[iata] || text} (${iata})` }
  for (const [city, iata] of Object.entries(CITY_IATA)) {
    if (city.includes(lo) || lo.includes(city)) {
      return `${IATA_CITIES[iata] || city} (${iata})`
    }
  }
  return null
}

function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return debounced
}

function LocationPreview({ value }) {
  const dv = useDebounce(value)
  const preview = resolveInput(dv)
  if (!preview) return <div className="loc-preview" />
  return <div className="loc-preview">✓ {preview}</div>
}

const TODAY = new Date().toISOString().split('T')[0]

const INITIAL = {
  origin: '', destination: '',
  departure_date: '',
  passengers: 1, travel_class: 1,
  max_flight_budget: '', preferred_airline: '',
  dep_time_min: '', dep_time_max: '',
  check_in: '', check_out: '',
  min_stars: '', max_hotel_budget: '',
  amenities: [],
  near_meeting_venue: false,
  meeting_venue: '',
}

export default function TravelForm({ onSubmit }) {
  const [f, setF] = useState(INITIAL)
  const [checkInLinked, setCheckInLinked] = useState(true)
  const [error, setError] = useState('')

  function set(field, value) {
    setF(prev => ({ ...prev, [field]: value }))
  }

  function toggleAmenity(key) {
    setF(prev => ({
      ...prev,
      amenities: prev.amenities.includes(key)
        ? prev.amenities.filter(a => a !== key)
        : [...prev.amenities, key],
    }))
  }

  function handleDepDateChange(e) {
    const val = e.target.value
    set('departure_date', val)
    if (checkInLinked) set('check_in', val)
  }

  function handleCheckInChange(e) {
    setCheckInLinked(false)
    set('check_in', e.target.value)
  }

  function clearTimeRange() {
    set('dep_time_min', '')
    set('dep_time_max', '')
  }

  function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (!f.origin.trim() || !f.destination.trim())
      return setError('Kalkış ve varış noktasını girin.')
    if (!f.departure_date) return setError('Kalkış tarihini seçin.')
    if (!f.check_in || !f.check_out) return setError('Konaklama tarihlerini seçin.')
    if (f.check_out <= f.check_in) return setError('Çıkış tarihi girişten sonra olmalı.')
    if (f.near_meeting_venue && !f.meeting_venue.trim())
      return setError('"Toplantı yerine yakın" seçiliyken toplantı yeri girilmeli.')

    const payload = {
      origin:             f.origin.trim(),
      destination:        f.destination.trim(),
      departure_date:     f.departure_date,
      passengers:         Number(f.passengers) || 1,
      travel_class:       Number(f.travel_class) || 1,
      check_in:           f.check_in,
      check_out:          f.check_out,
      near_meeting_venue: f.near_meeting_venue,
    }
    if (f.max_flight_budget)    payload.max_flight_budget = Number(f.max_flight_budget)
    if (f.preferred_airline.trim()) payload.preferred_airline = f.preferred_airline.trim()
    if (f.dep_time_min)         payload.departure_time_min = f.dep_time_min
    if (f.dep_time_max)         payload.departure_time_max = f.dep_time_max
    if (f.min_stars)            payload.min_stars = Number(f.min_stars)
    if (f.max_hotel_budget)     payload.max_hotel_budget = Number(f.max_hotel_budget)
    if (f.amenities.length)     payload.amenities = f.amenities
    if (f.meeting_venue.trim()) payload.meeting_venue = f.meeting_venue.trim()

    onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="card form-card">

        {/* ── Uçuş ─────────────────────────────────────── */}
        <div className="form-section">
          <p className="form-section-label">✈ Uçuş Bilgileri</p>

          <div className="form-grid">
            <div className="form-field">
              <label>Kalkış *</label>
              <input value={f.origin} onChange={e => set('origin', e.target.value)}
                placeholder="İstanbul, IST…" />
              <LocationPreview value={f.origin} />
            </div>
            <div className="form-field">
              <label>Varış *</label>
              <input value={f.destination} onChange={e => set('destination', e.target.value)}
                placeholder="Münih, MUC…" />
              <LocationPreview value={f.destination} />
            </div>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>Kalkış Tarihi *</label>
              <input type="date" min={TODAY} value={f.departure_date}
                onChange={handleDepDateChange} />
            </div>
            <div className="form-field">
              <label>Yolcu Sayısı</label>
              <select value={f.passengers} onChange={e => set('passengers', e.target.value)}>
                {[1,2,3,4,5,6].map(n => <option key={n} value={n}>{n} Yolcu</option>)}
              </select>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>Kabin Sınıfı</label>
              <select value={f.travel_class} onChange={e => set('travel_class', e.target.value)}>
                <option value={1}>Economy</option>
                <option value={2}>Premium Economy</option>
                <option value={3}>Business</option>
                <option value={4}>First</option>
              </select>
            </div>
            <div className="form-field">
              <label>Tercih Edilen Havayolu</label>
              <select value={f.preferred_airline} onChange={e => set('preferred_airline', e.target.value)}>
                {AIRLINE_OPTIONS.map(a => (
                  <option key={a.value} value={a.value}>{a.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>Maks. Uçuş Bütçesi (₺)</label>
              <input type="number" min={0} value={f.max_flight_budget}
                onChange={e => set('max_flight_budget', e.target.value)}
                placeholder="Opsiyonel" />
            </div>
            <div className="form-field">
              <label>Kalkış Saati Aralığı</label>
              <div className="time-range-row">
                <input type="time" value={f.dep_time_min}
                  onChange={e => set('dep_time_min', e.target.value)} style={{ flex: 1 }} />
                <span style={{ fontSize: 12, color: 'var(--color-gravel)', flexShrink: 0 }}>–</span>
                <input type="time" value={f.dep_time_max}
                  onChange={e => set('dep_time_max', e.target.value)} style={{ flex: 1 }} />
                {(f.dep_time_min || f.dep_time_max) && (
                  <button type="button" className="time-clear-btn" onClick={clearTimeRange}>×</button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ── Konaklama ─────────────────────────────────── */}
        <div className="form-section">
          <p className="form-section-label">🏨 Konaklama Bilgileri</p>

          <div className="form-grid">
            <div className="form-field">
              <label>Giriş Tarihi *</label>
              <input type="date" min={TODAY} value={f.check_in}
                onChange={handleCheckInChange} />
              {checkInLinked && f.departure_date && (
                <span className="input-hint">Kalkış tarihiyle eşit — değiştirmek için düzenleyin</span>
              )}
            </div>
            <div className="form-field">
              <label>Çıkış Tarihi *</label>
              <input type="date" min={f.check_in || TODAY} value={f.check_out}
                onChange={e => set('check_out', e.target.value)} />
            </div>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>Minimum Yıldız</label>
              <select value={f.min_stars} onChange={e => set('min_stars', e.target.value)}>
                <option value="">Fark etmez</option>
                <option value={3}>3 Yıldız ve üstü</option>
                <option value={4}>4 Yıldız ve üstü</option>
                <option value={5}>5 Yıldız</option>
              </select>
            </div>
            <div className="form-field">
              <label>Maks. Otel Bütçesi (₺/gece)</label>
              <input type="number" min={0} value={f.max_hotel_budget}
                onChange={e => set('max_hotel_budget', e.target.value)}
                placeholder="Opsiyonel" />
            </div>
          </div>

          {/* Amenities */}
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 10 }}>Otel Olanakları</label>
            <div className="amenity-grid">
              {AMENITY_OPTIONS.map(({ key, label }) => (
                <label key={key} className={`amenity-chip${f.amenities.includes(key) ? ' selected' : ''}`}>
                  <input type="checkbox" checked={f.amenities.includes(key)}
                    onChange={() => toggleAmenity(key)} style={{ display: 'none' }} />
                  {label}
                </label>
              ))}
            </div>
          </div>

          <label className="checkbox-row">
            <input type="checkbox" checked={f.near_meeting_venue}
              onChange={e => set('near_meeting_venue', e.target.checked)} />
            <span>Toplantı / etkinlik yerine yakın otel seç</span>
          </label>
        </div>

        {/* ── Toplantı / Etkinlik ───────────────────────── */}
        <div className="form-section" style={{ marginBottom: 8 }}>
          <p className="form-section-label">📍 Toplantı / Etkinlik (Opsiyonel)</p>
          <div className="form-field">
            <label>Toplantı Yeri</label>
            <input value={f.meeting_venue} onChange={e => set('meeting_venue', e.target.value)}
              placeholder="Ör: Messe München, ICC Berlin, Marriott…" />
            <span className="input-hint">
              "Toplantı yerine yakın" seçiliyse bu alan zorunludur.
            </span>
          </div>
        </div>

      </div>

      {error && (
        <div className="error-state" style={{
          flexDirection: 'row', gap: 8, padding: '12px 16px',
          borderRadius: 10, marginTop: 16, fontSize: 13,
        }}>
          ⚠ {error}
        </div>
      )}

      <div className="form-actions" style={{ marginTop: 20 }}>
        <button type="submit" className="btn-primary">Paketleri Ara →</button>
      </div>
    </form>
  )
}
