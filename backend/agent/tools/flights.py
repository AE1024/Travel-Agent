from datetime import datetime, timedelta
from typing import List, Union
import os
from langchain.tools import tool
from agent.state import FlightOption
from serpapi import GoogleSearch

from dotenv import load_dotenv
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise EnvironmentError("SERPAPI_KEY bulunamadı. backend/.env dosyasını kontrol edin.")

last_results: List[FlightOption] = []

CITY_FIXER = {
    # --- TÜRKİYE ---
    "istanbul": "IST",
    "sabiha gökçen": "SAW",
    "ankara": "ESB",
    "izmir": "ADB",
    "antalya": "AYT",
    "adana": "ADA",
    "trabzon": "TZX",
    "dalaman": "DLM",
    "bodrum": "BJV",
    "gaziantep": "GZT",
    "kayseri": "ASR",
    "samsun": "SZF",
    "van": "VAN",
    "erzurum": "ERZ",
    "diyarbakır": "DIY",
    "konya": "KYA",

    # --- AVRUPA ---
    "london": "LHR",
    "londra": "LHR",
    "paris": "CDG",
    "berlin": "BER",
    "amsterdam": "AMS",
    "madrid": "MAD",
    "barcelona": "BCN",
    "rome": "FCO",
    "roma": "FCO",
    "milan": "MXP",
    "milano": "MXP",
    "frankfurt": "FRA",
    "munich": "MUC",
    "münih": "MUC",
    "vienna": "VIE",
    "viyana": "VIE",
    "zurich": "ZRH",
    "zürih": "ZRH",
    "brussels": "BRU",
    "brüksel": "BRU",
    "prague": "PRG",
    "prag": "PRG",
    "athens": "ATH",
    "atina": "ATH",
    "lisbon": "LIS",
    "lizbon": "LIS",
    "warsaw": "WAW",
    "varşova": "WAW",
    "budapest": "BUD",
    "budapeşte": "BUD",
    "thessaloniki": "SKG",
    "selanik": "SKG",
    "bucharest": "OTP",
    "bükreş": "OTP",
    "sofia": "SOF",
    "sofya": "SOF",
    "belgrade": "BEG",
    "belgrad": "BEG",
    "zagreb": "ZAG",
    "krakow": "KRK",
    "lyon": "LYS",
    "marseille": "MRS",
    "marsilya": "MRS",
    "nice": "NCE",
    "nis": "NCE",
    "seville": "SVQ",
    "sevilla": "SVQ",
    "sevilya": "SVQ",
    "valencia": "VLC",
    "valensiya": "VLC",
    "malaga": "AGP",
    "málaga": "AGP",
    "manchester": "MAN",
    "edinburgh": "EDI",
    "dortmund": "DTM",

    # --- AMERİKA ---
    "new york": "JFK",
    "los angeles": "LAX",
    "chicago": "ORD",
    "miami": "MIA",
    "san francisco": "SFO",
    "washington": "IAD",
    "toronto": "YYZ",
    "vancouver": "YVR",
    "mexico city": "MEX",
    "sao paulo": "GRU",
    "buenos aires": "EZE",

    # --- ASYA & PASİFİK ---
    "tokyo": "NRT",
    "seoul": "ICN",
    "seul": "ICN",
    "beijing": "PEK",
    "pekin": "PEK",
    "shanghai": "PVG",
    "şanghay": "PVG",
    "hong kong": "HKG",
    "singapore": "SIN",
    "singapur": "SIN",
    "bangkok": "BKK",
    "phuket": "HKT",
    "bali": "DPS",
    "sydney": "SYD",
    "melbourne": "MEL",

    # --- ORTA DOĞU & AFRİKA ---
    "dubai": "DXB",
    "doha": "DOH",
    "abu dhabi": "AUH",
    "riyadh": "RUH",
    "riyad": "RUH",
    "jeddah": "JED",
    "cidde": "JED",
    "cairo": "CAI",
    "kahire": "CAI",
    "tel aviv": "TLV",
    "casablanca": "CMN",
    "kazablanka": "CMN",
    "johannesburg": "JNB",
    "cape town": "CPT"
}

def get_iata_code(city_name: str):
    # Gelen ismi küçük harfe çevir ve Türkçe karakterleri normalize etmeye çalış
    city_name = city_name.lower().strip()
    
    return CITY_FIXER.get(city_name, city_name.upper())

AIRLINE_FIXER = {
    "turkish airlines": "TK",
    "thy": "TK",
    "türk hava yolları": "TK",
    "pegasus": "PC",
    "flypgs": "PC",
    "sunexpress": "XQ",
    "anadolujet": "VF",
    "ajet": "VF",
    "lufthansa": "LH",
    "british airways": "BA",
    "emirates": "EK",
    "qatar": "QR",
    "air france": "AF",
    "corendon": "XC",
    "corendon airlines": "XC"
}

def get_airline_code(airline_name: str | None):
    if not airline_name:
        return None
    name = airline_name.lower().strip()
    # Sözlükte varsa kodu döndür, yoksa (zaten kodsa) orijinali döndür (ilk 2 karakter)
    return AIRLINE_FIXER.get(name, airline_name[:2].upper())

@tool("search_flights")
def search_flights(
    origin: str,
    destination: str,
    outbound_date: str,
    outbound_date_end: str | None = None,
    departure_time_min: str | None = None,
    departure_time_max: str | None = None,
    adults: int = 1,
    children: int = 0,
    preferred_airline: str | None = None,
    max_budget: float | None = None,
    travel_class: int = 1,
    currency: str = "TRY"
) -> str:
    """
    Performs flight search.
    IMPORTANT: The 'origin' and 'destination' fields MUST be 3-digit IATA codes (e.g., 'IST', 'LHR').
    If the user provides a city name (e.g., 'Istanbul', 'London'), first determine the main airport IATA code for that city and then call this tool.
    If you dont find IATA code based on user input find IATA code with your general information   
    """
    global last_results
    last_results = []

    origin = get_iata_code(origin)
    destination = get_iata_code(destination)

    if outbound_date_end:
        start = datetime.strptime(outbound_date, "%Y-%m-%d")
        end = datetime.strptime(outbound_date_end, "%Y-%m-%d")
        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
    else:
        dates = [outbound_date]

    all_flights: List[FlightOption] = []

    for date in dates:
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": date,
            "type": 2,
            "adults": adults,
            "children": children,
            "travel_class": travel_class,
            "currency": currency,
            "hl": "tr",
            "api_key": SERPAPI_KEY
        }

        if preferred_airline:
            params["include_airlines"] = preferred_airline

        if max_budget:
            params["max_price"] = max_budget

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
        except Exception as e:
            return f"SerpAPI hatası: {e}"

        if "error" in results:
            print(f"[FLIGHTS] SerpAPI error: {results['error']}")
            return f"Arama hatası: {results['error']}"

        status = results.get("search_metadata", {}).get("status", "")
        print(f"[FLIGHTS] {origin}→{destination} status={status} best={len(results.get('best_flights',[]))} other={len(results.get('other_flights',[]))}")

        # Hiç sonuç yoksa Google Flights bazen search_metadata içinde bilgi verir
        if not results.get("best_flights") and not results.get("other_flights"):
            if status and status != "Success":
                return f"API hatası (status: {status}): {origin} → {destination}"

        for group in ["best_flights", "other_flights"]:
            for flight_data in results.get(group, []):
                legs = flight_data.get("flights", [])
                if not legs:
                    continue
                first_leg = legs[0]
                last_leg = legs[-1]
                all_flights.append(FlightOption(
                    airline=first_leg.get("airline", ""),
                    flight_no=first_leg.get("flight_number", ""),
                    departure_time=first_leg["departure_airport"]["time"],
                    arrival_time=last_leg["arrival_airport"]["time"],
                    duration=str(flight_data.get("total_duration", "")),
                    stops=len(legs) - 1,
                    price=float(flight_data.get("price", 0)),
                    currency=currency,
                    origin=first_leg["departure_airport"]["id"],
                    destination=last_leg["arrival_airport"]["id"],
                    arrival_airport=last_leg["arrival_airport"]["name"],
                    offer_id=flight_data.get("booking_token"),
                    booking_url=flight_data.get("booking_request", {}).get("url")
                ))

    if preferred_airline:
        iata = preferred_airline.upper()
        all_flights = [f for f in all_flights if f.flight_no.upper().startswith(iata)]

    if departure_time_min or departure_time_max:
        filtered = []
        for flight in all_flights:
            t = flight.departure_time if isinstance(flight.departure_time, str) else flight.departure_time[0]
            t = t[-5:]
            if departure_time_min and t < departure_time_min:
                continue
            if departure_time_max and t > departure_time_max:
                continue
            filtered.append(flight)
        all_flights = filtered

    top = all_flights[:10]

    last_results = top

    if not top:
        return f"'{origin}' → '{destination}' için {outbound_date} tarihinde uçuş bulunamadı."

    AIRLINE_URLS = {

        "Turkish Airlines": "https://www.turkishairlines.com",
        "Pegasus": "https://www.flypgs.com",
        "SunExpress": "https://www.sunexpress.com",
        "Corendon Airlines": "https://www.corendonairlines.com",
        "Freebird Airlines": "https://www.freebirdairlines.com",
        "AJet": "https://www.ajet.com",
        "Tailwind Airlines": "https://www.tailwind.com.tr",
        "Air Anka": "https://www.airanka.com.tr",
        "Southwind Airlines": "https://www.southwindairlines.com",
        "British Airways": "https://www.britishairways.com",
        "Lufthansa": "https://www.lufthansa.com",
        "Air France": "https://www.airfrance.com",
        "KLM": "https://www.klm.com",
        "EasyJet": "https://www.easyjet.com",
        "Wizz Air": "https://wizzair.com",
        "Ryanair": "https://www.ryanair.com",
        "Air Serbia": "https://www.airserbia.com",
        "LOT Polish Airlines": "https://www.lot.com",
        "SAS Scandinavian Airlines": "https://www.flysas.com",
        "Finnair": "https://www.finnair.com",
        "Iberia": "https://www.iberia.com",
        "TAP Air Portugal": "https://www.flytap.com",
        "ITA Airways": "https://www.ita-airways.com",
        "Austrian Airlines": "https://www.austrian.com",
        "Swiss International Air Lines": "https://www.swiss.com",
        "Aegean Airlines": "https://www.aegeanair.com",
        "Norwegian Air": "https://www.norwegian.com",
        "Brussels Airlines": "https://www.brusselsairlines.com",
        "Air Baltic": "https://www.airbaltic.com",
        "Qatar Airways": "https://www.qatarairways.com",
        "Emirates": "https://www.emirates.com",
        "Singapore Airlines": "https://www.singaporeair.com",
        "Cathay Pacific": "https://www.cathaypacific.com",
        "IndiGo": "https://www.goindigo.in",
        "China Southern Airlines": "https://www.csair.com",
        "Air China": "https://www.airchina.com",
        "China Eastern Airlines": "https://www.ceair.com",
        "Japan Airlines": "https://www.jal.co.jp",
        "American Airlines": "https://www.aa.com",
        "Delta Air Lines": "https://www.delta.com",
        "United Airlines": "https://www.united.com",
        "Southwest Airlines": "https://www.southwest.com",
        "Qantas": "https://www.qantas.com",
        "LATAM Airlines": "https://www.latamairlines.com",
        "Air Canada": "https://www.aircanada.com",
    }

    # booking_url yoksa Google Flights arama linki oluştur (pre-filled)
    for f in top:
        if not f.booking_url:
            date_str = str(f.departure_time)[:10]
            pax = f"p:{adults}"
            if children > 0:
                pax += f",{children}"
            f.booking_url = (
                f"https://www.google.com/flights#flt={f.origin}.{f.destination}.{date_str}"
                f";c:{currency};e:1;sd:1;t:f"
            )

    lines = [f"Gidiş Tarihi: {outbound_date} | {origin} → {destination} | {adults} yetişkin\n"]
    for i, f in enumerate(top, 1):
        stops_str = "Direkt" if f.stops == 0 else f"{f.stops} aktarma"
        link = f.booking_url or ""
        link_str = f"\n   🔗 Rezervasyon: {link}" if link else ""
        lines.append(
            f"{i}. {f.airline} {f.flight_no} | "
            f"Tarih: {outbound_date} | "
            f"Kalkış: {f.departure_time} → Varış: {f.arrival_time} | "
            f"Süre: {f.duration} dk | {stops_str} | "
            f"Fiyat: {f.price} {f.currency}"
            f"{link_str}"
        )
    return "\n".join(lines)
