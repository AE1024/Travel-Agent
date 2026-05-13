import { useState } from 'react'
import TravelForm  from './components/TravelForm'
import FlightCards from './components/FlightCards'
import HotelCards  from './components/HotelCards'
import SummaryCard from './components/SummaryCard'
import './App.css'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const STEPS    = ['Arama', 'Uçuşlar', 'Oteller', 'Özet']
const phaseStep = {
  form:            0,
  loading_flights: 0,
  flights:         1,
  loading_hotels:  1,
  hotels:          2,
  done:            3,
}

export default function App() {
  const [phase,          setPhase]          = useState('form')
  const [formParams,     setFormParams]     = useState(null)
  const [flights,        setFlights]        = useState([])
  const [hotels,         setHotels]         = useState([])
  const [selectedFlight, setSelectedFlight] = useState(null)
  const [nights,         setNights]         = useState(3)
  const [destCity,       setDestCity]       = useState('')
  const [error,          setError]          = useState(null)

  const currentStep = phaseStep[phase] ?? 0

  /* ── 1. Form gönderildi → uçuş ara ── */
  async function handleSearch(params) {
    setError(null)
    setFormParams(params)
    setPhase('loading_flights')
    try {
      const cin  = new Date(params.check_in)
      const cout = new Date(params.check_out)
      setNights(Math.max(1, Math.round((cout - cin) / 86400000)))
    } catch { setNights(3) }

    try {
      const res  = await fetch(`${API}/search-flights`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(params),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Sunucu hatası')
      setFlights(data.flights ?? [])
      setDestCity(data.destination_city ?? '')
      setPhase('flights')
    } catch (e) {
      setError(e.message)
      setPhase('form')
    }
  }

  /* ── 2. Uçuş seçildi → otel ara ── */
  async function handleFlightSelect(flight) {
    setSelectedFlight(flight)
    setError(null)
    setPhase('loading_hotels')
    try {
      const res  = await fetch(`${API}/search-hotels`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(formParams),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Sunucu hatası')
      setHotels(data.hotels ?? [])
      setNights(data.nights ?? nights)
      setPhase('hotels')
    } catch (e) {
      setError(e.message)
      setPhase('flights')
    }
  }

  /* ── 3. Otel seçildi → özet ── */
  function handleHotelSelect(hotel) {
    setPhase('done')
    setHotels(h => h.map(x => ({ ...x, _selected: x === hotel })))
    // selected hotel doğrudan SummaryCard'a geçiyoruz
    setSelectedHotel(hotel)
  }

  /* helper — selectedHotel state */
  const [selectedHotel, setSelectedHotel] = useState(null)

  function handleRestart() {
    setPhase('form')
    setFormParams(null)
    setFlights([])
    setHotels([])
    setSelectedFlight(null)
    setSelectedHotel(null)
    setError(null)
  }

  const isLoading = phase === 'loading_flights' || phase === 'loading_hotels'

  return (
    <div className="app-shell">
      <nav className="navbar">
        <span className="navbar-logo">TravelAgent</span>
        {phase !== 'form' && !isLoading && (
          <button className="btn-ghost" style={{ marginLeft: 'auto', fontSize: 13 }}
            onClick={handleRestart}>
            Yeni Arama
          </button>
        )}
      </nav>

      <main className="app-main">

        {/* Adım göstergesi */}
        {phase !== 'form' && (
          <div className="step-indicator" style={{ marginBottom: 40 }}>
            {STEPS.map((label, i) => (
              <div key={i} className="step-item">
                <div className={`step-dot${i < currentStep ? ' done' : i === currentStep ? ' active' : ''}`}>
                  {i < currentStep ? '✓' : i + 1}
                </div>
                <span className={`step-label${i < currentStep ? ' done' : i === currentStep ? ' active' : ''}`}>
                  {label}
                </span>
                {i < STEPS.length - 1 && <div className="step-connector" />}
              </div>
            ))}
          </div>
        )}

        {/* Hata */}
        {error && (
          <div className="error-state" style={{
            flexDirection: 'row', gap: 8, padding: '12px 18px',
            borderRadius: 8, marginBottom: 24, fontSize: 13,
          }}>
            ⚠ {error}
          </div>
        )}

        {/* Form */}
        {phase === 'form' && (
          <>
            <div className="page-header">
              <p className="eyebrow">AI Destekli Seyahat Planlayıcı</p>
              <h1 className="display-heading">Seyahatinizi planlayın.</h1>
            </div>
            <TravelForm onSubmit={handleSearch} />
          </>
        )}

        {/* Yükleniyor */}
        {phase === 'loading_flights' && (
          <div className="loading-state">
            <div className="spinner" />
            <p>Uçuşlar aranıyor…</p>
          </div>
        )}
        {phase === 'loading_hotels' && (
          <div className="loading-state">
            <div className="spinner" />
            <p>Oteller aranıyor{formParams?.meeting_venue ? ', toplantı yerine yakınlık hesaplanıyor' : ''}…</p>
          </div>
        )}

        {/* Uçuş seçimi */}
        {phase === 'flights' && (
          <>
            <div className="results-header">
              <p className="section-heading">Uçuş Seçin</p>
              <p className="eyebrow" style={{ marginTop: 6 }}>
                {destCity} · {formParams?.departure_date} · {formParams?.passengers} yolcu
              </p>
            </div>
            <FlightCards
              flights={flights}
              passengers={formParams?.passengers ?? 1}
              travelClass={formParams?.travel_class ?? 1}
              onSelect={handleFlightSelect}
            />
            <div className="form-actions" style={{ borderTop: '1px solid var(--color-chalk)', paddingTop: 20, marginTop: 8 }}>
              <button className="btn-ghost" onClick={handleRestart}>← Yeni Arama</button>
            </div>
          </>
        )}

        {/* Otel seçimi */}
        {phase === 'hotels' && (
          <>
            <div className="results-header">
              {/* Seçilen uçuş özeti */}
              <div className="selected-flight-bar">
                <span className="label-small">✈ Seçilen Uçuş</span>
                <span className="sfb-name">{selectedFlight?.airline} {selectedFlight?.flight_no}</span>
                <span className="sfb-detail">
                  {String(selectedFlight?.departure_time ?? '').slice(-5)} → {String(selectedFlight?.arrival_time ?? '').slice(-5)}
                  &nbsp;·&nbsp;
                  {selectedFlight?.stops === 0 ? 'Direkt' : `${selectedFlight?.stops} aktarma`}
                </span>
                <span className="sfb-price">₺{Number(selectedFlight?.price ?? 0).toLocaleString('tr-TR')}</span>
                <button className="btn-ghost" style={{ marginLeft: 'auto', height: 32, fontSize: 12, padding: '0 14px' }}
                  onClick={() => setPhase('flights')}>
                  Değiştir
                </button>
              </div>
              <p className="section-heading" style={{ marginTop: 24 }}>Otel Seçin</p>
              <p className="eyebrow" style={{ marginTop: 6 }}>
                {destCity} · {formParams?.check_in} → {formParams?.check_out} · {nights} gece
                {formParams?.meeting_venue ? ` · ${formParams.meeting_venue}` : ''}
              </p>
            </div>
            <HotelCards hotels={hotels} nights={nights} onSelect={handleHotelSelect} />
            <div className="form-actions" style={{ borderTop: '1px solid var(--color-chalk)', paddingTop: 20, marginTop: 8 }}>
              <button className="btn-ghost" onClick={() => setPhase('flights')}>← Uçuşa Dön</button>
            </div>
          </>
        )}

        {/* Özet */}
        {phase === 'done' && selectedFlight && selectedHotel && (
          <SummaryCard
            flight={selectedFlight}
            hotel={selectedHotel}
            hotelNights={nights}
            destCity={destCity}
            onRestart={handleRestart}
          />
        )}

      </main>

      <footer style={{
        textAlign: 'center',
        padding: '20px',
        fontSize: 12,
        color: 'var(--color-slate)',
        borderTop: '1px solid var(--color-chalk)',
      }}>
        © {new Date().getFullYear()} Anıl Elmaz
      </footer>
    </div>
  )
}
