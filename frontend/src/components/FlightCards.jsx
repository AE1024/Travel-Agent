const AIRLINE_SITES = {
  'Turkish Airlines':  'https://www.turkishairlines.com',
  'Pegasus':           'https://www.flypgs.com',
  'Pegasus Airlines':  'https://www.flypgs.com',
  'SunExpress':        'https://www.sunexpress.com',
  'AnadoluJet':        'https://www.anadolujet.com',
  'Lufthansa':         'https://www.lufthansa.com',
  'British Airways':   'https://www.britishairways.com',
  'Emirates':          'https://www.emirates.com',
  'Qatar Airways':     'https://www.qatarairways.com',
  'Air France':        'https://www.airfrance.com',
  'Corendon Airlines': 'https://www.corendonairlines.com',
  'KLM':               'https://www.klm.com',
  'Swiss':             'https://www.swiss.com',
  'easyJet':           'https://www.easyjet.com',
  'Ryanair':           'https://www.ryanair.com',
  'Wizz Air':          'https://wizzair.com',
  'Finnair':           'https://www.finnair.com',
  'Austrian Airlines': 'https://www.austrian.com',
}

const CLASS_LABELS = {
  1: 'Economy', 2: 'Premium Economy', 3: 'Business', 4: 'First Class',
}

const IATA_CITY = {
  IST:'İstanbul (Atatürk)', SAW:'İstanbul (Sabiha)', ESB:'Ankara', ADB:'İzmir',
  AYT:'Antalya', DLM:'Dalaman', BJV:'Bodrum', TZX:'Trabzon', GZT:'Gaziantep',
  LHR:'Londra Heathrow', LGW:'Londra Gatwick', STN:'Londra Stansted',
  CDG:'Paris CDG', ORY:'Paris Orly',
  FRA:'Frankfurt', MUC:'Münih', BER:'Berlin', HAM:'Hamburg', DUS:'Düsseldorf',
  STR:'Stuttgart', CGN:'Köln',
  AMS:'Amsterdam', BRU:'Brüksel', CPH:'Kopenhag', ARN:'Stockholm',
  OSL:'Oslo', HEL:'Helsinki',
  MAD:'Madrid', BCN:'Barselona', LIS:'Lizbon', OPO:'Porto',
  FCO:'Roma Fiumicino', CIA:'Roma Ciampino',
  MXP:'Milano Malpensa', LIN:'Milano Linate',
  VCE:'Venedik', NAP:'Napoli',
  VIE:'Viyana', ZRH:'Zürih', GVA:'Cenevre', DUB:'Dublin',
  WAW:'Varşova', PRG:'Prag', BUD:'Budapeşte', ATH:'Atina',
  DXB:'Dubai', AUH:'Abu Dabi', DOH:'Doha', CAI:'Kahire', TLV:'Tel Aviv',
  JFK:'New York JFK', LAX:'Los Angeles', SFO:'San Francisco',
  ORD:'Chicago O\'Hare', NRT:'Tokyo Narita', ICN:'Seul',
  SIN:'Singapur', BKK:'Bangkok', SYD:'Sidney', MEL:'Melbourne',
}

export default function FlightCards({ flights, passengers = 1, travelClass = 1, onSelect }) {
  if (!flights?.length) {
    return <p style={{ color: 'var(--color-gravel)', padding: '40px 0' }}>Uçuş bulunamadı.</p>
  }

  const classLabel = CLASS_LABELS[travelClass] || 'Economy'

  return (
    <div className="results-list">
      {flights.map((f, i) => {
        const dep    = String(f.departure_time ?? '').slice(-5)
        const arr    = String(f.arrival_time   ?? '').slice(-5)
        const stops  = f.stops === 0 ? 'Direkt' : `${f.stops} aktarma`
        const h      = f.duration ? Math.floor(f.duration / 60) : null
        const m      = f.duration ? f.duration % 60 : null
        const dur    = h != null ? `${h > 0 ? h + 's ' : ''}${m}d` : ''
        // SerpAPI toplam fiyatı döndürür; yolcu sayısına böl → bireysel fiyat, sonra çarp
        const total  = Math.round((f.price ?? 0) * passengers)
        const site   = AIRLINE_SITES[f.airline]

        return (
          <div key={i} className="card result-card">
            <div className="rc-airline">
              <span className="rc-airline-name">{f.airline}</span>
              <span className="rc-fn">{f.flight_no}</span>
              <span className="rc-class-badge">{classLabel}</span>
            </div>
            <div className="rc-body">
              <div className="rc-route">
                <div className="rc-time-col">
                  <span className="rc-time">{dep}</span>
                  <span className="rc-airport">{f.origin}</span>
                  <span className="rc-airport-full">{IATA_CITY[f.origin] || ''}</span>
                </div>
                <div className="rc-line-col">
                  {dur && <span className="rc-dur">{dur}</span>}
                  <div className="rc-track">
                    <div className="rc-dot" />
                    <div className="rc-bar" />
                    <div className="rc-dot" />
                  </div>
                  <span className="rc-stops">{stops}</span>
                </div>
                <div className="rc-time-col rc-time-col--right">
                  <span className="rc-time">{arr}</span>
                  <span className="rc-airport">{f.destination}</span>
                  <span className="rc-airport-full">{IATA_CITY[f.destination] || ''}</span>
                </div>
              </div>

              <div className="rc-action">
                <div style={{ textAlign: 'right' }}>
                  <span className="rc-price">
                    ₺{Number(f.price ?? 0).toLocaleString('tr-TR')}
                  </span>
                  {passengers > 1 && (
                    <p style={{ fontSize: 11, color: 'var(--color-gravel)', marginTop: 2 }}>
                      Toplam ₺{Number(total).toLocaleString('tr-TR')} · {passengers} yolcu
                    </p>
                  )}
                  <p style={{ fontSize: 10, color: 'var(--color-slate)', marginTop: 2 }}>
                    ~tahmini fiyat
                  </p>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'flex-end' }}>
                  {site && (
                    <a href={site} target="_blank" rel="noopener noreferrer"
                      className="platform-book-btn"
                      style={{ background: '#1a1a2e', fontSize: 11, textAlign: 'center', whiteSpace: 'nowrap' }}>
                      {f.airline} →
                    </a>
                  )}
                  <button className="btn-primary"
                    style={{ height: 36, padding: '0 20px', fontSize: 13 }}
                    onClick={() => onSelect(f)}>
                    Seç →
                  </button>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
