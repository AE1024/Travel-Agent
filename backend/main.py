import asyncio
import math
import os
import requests as _requests
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import agent.tools.flights as flights_tool
import agent.tools.hotels as hotels_tool


IATA_TO_CITY: dict[str, str] = {
    # Türkiye
    "IST": "Istanbul", "SAW": "Istanbul", "ESB": "Ankara", "ADB": "Izmir",
    "AYT": "Antalya", "DLM": "Dalaman", "BJV": "Bodrum", "ASR": "Kayseri",
    "TZX": "Trabzon", "GZT": "Gaziantep", "VAN": "Van", "ERZ": "Erzurum",
    "SZF": "Samsun", "KYA": "Konya", "MLX": "Malatya", "EZS": "Elazig",
    "DIY": "Diyarbakir", "SFQ": "Sanliurfa", "KSY": "Kars",
    # Avrupa — İngiltere
    "LHR": "London", "LGW": "London", "STN": "London", "LTN": "London",
    "EDI": "Edinburgh", "MAN": "Manchester", "BHX": "Birmingham",
    "BRS": "Bristol", "LBA": "Leeds",
    # Fransa
    "CDG": "Paris", "ORY": "Paris", "LYS": "Lyon", "MRS": "Marseille",
    "TLS": "Toulouse", "NCE": "Nice", "NTE": "Nantes",
    # Almanya
    "FRA": "Frankfurt", "MUC": "Munich", "BER": "Berlin", "HAM": "Hamburg",
    "DUS": "Dusseldorf", "STR": "Stuttgart", "CGN": "Cologne", "NUE": "Nuremberg",
    # Benelux & İskandinav
    "AMS": "Amsterdam", "BRU": "Brussels", "LUX": "Luxembourg",
    "CPH": "Copenhagen", "ARN": "Stockholm", "OSL": "Oslo", "HEL": "Helsinki",
    "GOT": "Gothenburg", "BGO": "Bergen",
    # İberya
    "MAD": "Madrid", "BCN": "Barcelona", "AGP": "Malaga", "ALC": "Alicante",
    "VLC": "Valencia", "SVQ": "Seville", "BIO": "Bilbao",
    "PMI": "Palma de Mallorca", "IBZ": "Ibiza", "LIS": "Lisbon", "OPO": "Porto",
    # İtalya
    "FCO": "Rome", "CIA": "Rome", "MXP": "Milan", "LIN": "Milan",
    "NAP": "Naples", "VCE": "Venice", "BLQ": "Bologna", "PSA": "Pisa",
    "CTA": "Catania", "PMO": "Palermo",
    # Diğer Avrupa
    "VIE": "Vienna", "ZRH": "Zurich", "GVA": "Geneva", "BSL": "Basel",
    "DUB": "Dublin", "WAW": "Warsaw", "KRK": "Krakow", "PRG": "Prague",
    "BUD": "Budapest", "SOF": "Sofia", "OTP": "Bucharest", "KBP": "Kyiv",
    "ATH": "Athens", "SKG": "Thessaloniki", "HER": "Heraklion",
    "ZAG": "Zagreb", "SPU": "Split", "DBV": "Dubrovnik",
    "BEG": "Belgrade", "TGD": "Podgorica", "SKP": "Skopje", "TIA": "Tirana",
    "SVO": "Moscow", "LED": "Saint Petersburg", "VKO": "Moscow",
    # Orta Doğu
    "DXB": "Dubai", "AUH": "Abu Dhabi", "DOH": "Doha", "KWI": "Kuwait City",
    "RUH": "Riyadh", "JED": "Jeddah", "MCT": "Muscat", "BAH": "Bahrain",
    "CAI": "Cairo", "TLV": "Tel Aviv", "AMM": "Amman", "BEY": "Beirut",
    # Afrika
    "JNB": "Johannesburg", "CPT": "Cape Town", "NBO": "Nairobi",
    "ADD": "Addis Ababa", "LOS": "Lagos", "ACC": "Accra", "CMN": "Casablanca",
    # Kuzey Amerika
    "JFK": "New York", "EWR": "New York", "LGA": "New York",
    "LAX": "Los Angeles", "SFO": "San Francisco", "SJC": "San Jose",
    "ORD": "Chicago", "MDW": "Chicago", "ATL": "Atlanta",
    "DFW": "Dallas", "IAH": "Houston", "HOU": "Houston",
    "MIA": "Miami", "FLL": "Fort Lauderdale", "BOS": "Boston",
    "SEA": "Seattle", "DEN": "Denver", "LAS": "Las Vegas",
    "PHX": "Phoenix", "MCO": "Orlando", "TPA": "Tampa",
    "YYZ": "Toronto", "YVR": "Vancouver", "YUL": "Montreal",
    "MEX": "Mexico City", "CUN": "Cancun", "GDL": "Guadalajara",
    # Güney Amerika
    "GRU": "Sao Paulo", "GIG": "Rio de Janeiro", "EZE": "Buenos Aires",
    "BOG": "Bogota", "SCL": "Santiago", "LIM": "Lima", "UIO": "Quito",
    # Asya
    "NRT": "Tokyo", "HND": "Tokyo", "KIX": "Osaka", "ITM": "Osaka",
    "ICN": "Seoul", "GMP": "Seoul",
    "PEK": "Beijing", "PKX": "Beijing", "PVG": "Shanghai", "SHA": "Shanghai",
    "CAN": "Guangzhou", "SZX": "Shenzhen",
    "HKG": "Hong Kong", "TPE": "Taipei",
    "SIN": "Singapore", "KUL": "Kuala Lumpur", "BKK": "Bangkok",
    "DMK": "Bangkok", "CGK": "Jakarta", "DPS": "Bali",
    "MNL": "Manila", "SGN": "Ho Chi Minh City", "HAN": "Hanoi",
    "REP": "Siem Reap", "PNH": "Phnom Penh", "RGN": "Yangon",
    "DEL": "New Delhi", "BOM": "Mumbai", "BLR": "Bangalore",
    "MAA": "Chennai", "HYD": "Hyderabad", "CCU": "Kolkata",
    # Avustralya & Pasifik
    "SYD": "Sydney", "MEL": "Melbourne", "BNE": "Brisbane",
    "PER": "Perth", "ADL": "Adelaide", "CBR": "Canberra",
    "AKL": "Auckland", "CHC": "Christchurch", "NAN": "Fiji",
}

# Şehir adı / yaygın isim → IATA kodu (Türkçe ve İngilizce varyantlar dahil)
CITY_TO_IATA: dict[str, str] = {
    # Türkiye
    "istanbul": "IST", "i̇stanbul": "IST", "istanbull": "IST",
    "ankara": "ESB", "izmir": "ADB", "i̇zmir": "ADB",
    "antalya": "AYT", "dalaman": "DLM", "bodrum": "BJV",
    "kayseri": "ASR", "trabzon": "TZX", "gaziantep": "GZT",
    "van": "VAN", "erzurum": "ERZ", "samsun": "SZF", "konya": "KYA",
    "malatya": "MLX", "diyarbakir": "DIY", "diyarbakır": "DIY",
    # UK
    "london": "LHR", "londra": "LHR", "london heathrow": "LHR",
    "london gatwick": "LGW", "london stansted": "STN",
    "edinburgh": "EDI", "manchester": "MAN", "birmingham": "BHX",
    "bristol": "BRS",
    # Fransa
    "paris": "CDG", "paris cdg": "CDG", "paris orly": "ORY",
    "lyon": "LYS", "marseille": "MRS", "marsilya": "MRS",
    "toulouse": "TLS", "nice": "NCE", "nantes": "NTE",
    # Almanya
    "frankfurt": "FRA", "munich": "MUC", "münchen": "MUC", "munih": "MUC", "münih": "MUC",
    "berlin": "BER", "hamburg": "HAM", "dusseldorf": "DUS", "düsseldorf": "DUS",
    "stuttgart": "STR", "cologne": "CGN", "koln": "CGN", "köln": "CGN",
    "nuremberg": "NUE", "nürnberg": "NUE",
    # Benelux & İskandinavya
    "amsterdam": "AMS", "brussels": "BRU", "brüksel": "BRU", "bruxelles": "BRU",
    "luxembourg": "LUX", "lüksemburg": "LUX",
    "copenhagen": "CPH", "kopenhag": "CPH", "kobenhavn": "CPH", "københavn": "CPH",
    "stockholm": "ARN", "oslo": "OSL", "helsinki": "HEL",
    "gothenburg": "GOT", "goteborg": "GOT", "göteborg": "GOT",
    "bergen": "BGO",
    # İberya
    "madrid": "MAD", "barcelona": "BCN", "barselona": "BCN",
    "malaga": "AGP", "malaga": "AGP", "alicante": "ALC",
    "valencia": "VLC", "valensiya": "VLC", "seville": "SVQ", "sevilla": "SVQ",
    "bilbao": "BIO", "palma": "PMI", "palma de mallorca": "PMI",
    "ibiza": "IBZ", "i̇biza": "IBZ",
    "lisbon": "LIS", "lizbon": "LIS", "lisboa": "LIS",
    "porto": "OPO",
    # İtalya
    "rome": "FCO", "roma": "FCO", "rom": "FCO",
    "milan": "MXP", "milano": "MXP",
    "naples": "NAP", "napoli": "NAP",
    "venice": "VCE", "venedik": "VCE", "venezia": "VCE",
    "bologna": "BLQ", "pisa": "PSA", "catania": "CTA", "palermo": "PMO",
    # Diğer Avrupa
    "vienna": "VIE", "viyana": "VIE", "wien": "VIE",
    "zurich": "ZRH", "zürih": "ZRH", "zürich": "ZRH",
    "geneva": "GVA", "cenevre": "GVA", "geneve": "GVA", "genf": "GVA",
    "basel": "BSL",
    "dublin": "DUB",
    "warsaw": "WAW", "varşova": "WAW", "varsova": "WAW",
    "krakow": "KRK", "kraków": "KRK", "krakof": "KRK",
    "prague": "PRG", "prag": "PRG", "praha": "PRG",
    "budapest": "BUD", "budapeşte": "BUD",
    "sofia": "SOF", "sofya": "SOF",
    "bucharest": "OTP", "bükreş": "OTP",
    "kyiv": "KBP", "kiev": "KBP",
    "athens": "ATH", "atina": "ATH", "athina": "ATH",
    "thessaloniki": "SKG", "selanik": "SKG",
    "heraklion": "HER", "iraklion": "HER",
    "zagreb": "ZAG", "split": "SPU", "dubrovnik": "DBV",
    "belgrade": "BEG", "belgrad": "BEG", "beograd": "BEG",
    "moscow": "SVO", "moskova": "SVO", "moskow": "SVO",
    "saint petersburg": "LED", "st petersburg": "LED", "st. petersburg": "LED",
    # Orta Doğu
    "dubai": "DXB",
    "abu dhabi": "AUH", "abu dabi": "AUH",
    "doha": "DOH",
    "kuwait": "KWI", "kuveyt": "KWI",
    "riyadh": "RUH", "riyad": "RUH",
    "jeddah": "JED", "cidde": "JED",
    "muscat": "MCT", "maskat": "MCT",
    "bahrain": "BAH", "bahreyn": "BAH",
    "cairo": "CAI", "kahire": "CAI",
    "tel aviv": "TLV", "tel avıv": "TLV",
    "amman": "AMM",
    "beirut": "BEY", "beyrut": "BEY",
    # Afrika
    "johannesburg": "JNB", "jo'burg": "JNB",
    "cape town": "CPT",
    "nairobi": "NBO",
    "addis ababa": "ADD", "addis abeba": "ADD",
    "lagos": "LOS", "accra": "ACC",
    "casablanca": "CMN", "kazablanka": "CMN",
    # Kuzey Amerika
    "new york": "JFK", "newyork": "JFK", "new york city": "JFK",
    "los angeles": "LAX", "la": "LAX",
    "san francisco": "SFO", "sf": "SFO",
    "chicago": "ORD",
    "atlanta": "ATL",
    "dallas": "DFW",
    "houston": "IAH",
    "miami": "MIA",
    "boston": "BOS",
    "seattle": "SEA",
    "denver": "DEN",
    "las vegas": "LAS", "vegas": "LAS",
    "phoenix": "PHX",
    "orlando": "MCO",
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL", "montréal": "YUL",
    "mexico city": "MEX", "meksiko": "MEX",
    "cancun": "CUN", "cancún": "CUN",
    "sao paulo": "GRU", "são paulo": "GRU",
    "rio de janeiro": "GIG", "rio": "GIG",
    "buenos aires": "EZE",
    "bogota": "BOG", "bogotá": "BOG",
    "santiago": "SCL", "lima": "LIM",
    # Asya
    "tokyo": "NRT", "tokio": "NRT",
    "osaka": "KIX",
    "seoul": "ICN", "seul": "ICN",
    "beijing": "PEK", "pekin": "PEK",
    "shanghai": "PVG", "şangay": "PVG",
    "guangzhou": "CAN", "kanton": "CAN",
    "shenzhen": "SZX",
    "hong kong": "HKG", "hongkong": "HKG",
    "taipei": "TPE",
    "singapore": "SIN", "singapur": "SIN",
    "kuala lumpur": "KUL", "kl": "KUL",
    "bangkok": "BKK",
    "jakarta": "CGK", "cakarta": "CGK",
    "bali": "DPS", "denpasar": "DPS",
    "manila": "MNL",
    "ho chi minh": "SGN", "saigon": "SGN",
    "hanoi": "HAN",
    "new delhi": "DEL", "delhi": "DEL", "yeni delhi": "DEL",
    "mumbai": "BOM", "bombay": "BOM",
    "bangalore": "BLR", "bengaluru": "BLR",
    "chennai": "MAA", "madras": "MAA",
    "hyderabad": "HYD",
    "kolkata": "CCU", "calcutta": "CCU",
    # Avustralya & Pasifik
    "sydney": "SYD", "sidney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",
    "adelaide": "ADL",
    "auckland": "AKL",
    "christchurch": "CHC",
}


def resolve_location(raw: str) -> tuple[str, str]:
    """
    Kullanıcının girdiği metinden (IATA kodu veya şehir adı) (iata, şehir_adı) döner.
    Önce IATA kodu olarak dener, bulamazsa şehir adı olarak arar.
    """
    text = raw.strip()
    upper = text.upper()
    lower = text.lower()

    # 2-4 harf büyük → önce bilinen IATA kodlarına bak
    if len(upper) <= 4 and upper.isalpha():
        if upper in IATA_TO_CITY:
            return upper, IATA_TO_CITY[upper]
        # IATA listesinde yok → şehir adı olarak dene (ROMA, OSLO, LIMA vb.)
        if lower in CITY_TO_IATA:
            iata = CITY_TO_IATA[lower]
            return iata, IATA_TO_CITY.get(iata, text)
        # Son çare: as-is döndür
        return upper, upper

    # Şehir adı tam eşleşme
    if lower in CITY_TO_IATA:
        iata = CITY_TO_IATA[lower]
        return iata, IATA_TO_CITY.get(iata, text)

    # Türkçe karakter normalize (ı→i, İ→i vb)
    normalized = (lower
        .replace("ı", "i").replace("i̇", "i").replace("ş", "s")
        .replace("ğ", "g").replace("ü", "u").replace("ö", "o")
        .replace("ç", "c").replace("â", "a").replace("î", "i").replace("û", "u"))
    if normalized in CITY_TO_IATA:
        iata = CITY_TO_IATA[normalized]
        return iata, IATA_TO_CITY.get(iata, text)

    # Kısmi eşleşme — şehir ismi girilen metnin içinde mi?
    for city_key, iata in CITY_TO_IATA.items():
        if city_key in lower or lower in city_key:
            return iata, IATA_TO_CITY.get(iata, text)

    # Hiçbir şey bulunamadı — büyük harf ile as-is döndür
    return upper, text


app = FastAPI(title="TravelAgent API")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


_AIRLINE_TO_IATA: dict[str, str] = {
    "turkish airlines": "TK", "thy": "TK", "türk hava yolları": "TK",
    "pegasus": "PC", "flypgs": "PC",
    "sunexpress": "XQ",
    "anadolujet": "VF", "ajet": "VF",
    "lufthansa": "LH",
    "british airways": "BA",
    "emirates": "EK",
    "qatar": "QR", "qatar airways": "QR",
    "air france": "AF",
    "corendon": "XC", "corendon airlines": "XC",
}

def resolve_airline(name: str | None) -> str | None:
    if not name:
        return None
    resolved = _AIRLINE_TO_IATA.get(name.lower().strip())
    return resolved or name  # bilinmiyorsa as-is gönder


def _nominatim_coords(query: str) -> tuple[float, float] | None:
    """Nominatim ile bir adres/yer adının koordinatlarını döner."""
    try:
        resp = _requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": "TravelAgent/1.0"},
            timeout=5,
        )
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return round(2 * R * math.asin(math.sqrt(a)), 2)


class PackageSearchRequest(BaseModel):
    # Uçuş (zorunlu)
    origin: str
    destination: str
    departure_date: str
    # Uçuş (opsiyonel)
    passengers: int = 1
    travel_class: int = 1  # 1=economy 2=premium_eco 3=business 4=first
    max_flight_budget: Optional[float] = None
    preferred_airline: Optional[str] = None
    departure_time_min: Optional[str] = None  # "HH:MM"
    departure_time_max: Optional[str] = None  # "HH:MM"
    # Konaklama (zorunlu)
    check_in: str
    check_out: str
    # Konaklama (opsiyonel)
    min_stars: Optional[int] = None
    max_hotel_budget: Optional[float] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    amenities: Optional[List[str]] = None
    near_meeting_venue: bool = False
    # Toplantı/Etkinlik (opsiyonel)
    meeting_venue: Optional[str] = None


@app.post("/search-flights")
async def endpoint_search_flights(req: PackageSearchRequest):
    origin_iata, origin_city           = resolve_location(req.origin)
    destination_iata, destination_city = resolve_location(req.destination)

    flight_params = {
        "origin":        origin_iata,
        "destination":   destination_iata,
        "outbound_date": req.departure_date,
        "adults":        req.passengers,
        "travel_class":  req.travel_class,
    }
    if req.max_flight_budget:
        flight_params["max_budget"] = req.max_flight_budget
    if req.preferred_airline:
        flight_params["preferred_airline"] = resolve_airline(req.preferred_airline)
    if req.departure_time_min:
        flight_params["departure_time_min"] = req.departure_time_min
    if req.departure_time_max:
        flight_params["departure_time_max"] = req.departure_time_max

    await asyncio.to_thread(flights_tool.search_flights.invoke, flight_params)
    results = list(flights_tool.last_results)

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"{origin_iata}→{destination_iata} için {req.departure_date} tarihinde uçuş bulunamadı.",
        )

    return {
        "flights":          [f.model_dump() for f in results[:8]],
        "origin_city":      origin_city,
        "destination_city": destination_city,
        "destination_iata": destination_iata,
    }


@app.post("/search-hotels")
async def endpoint_search_hotels(req: PackageSearchRequest):
    destination_iata, destination_city = resolve_location(req.destination)

    try:
        nights = max(1, (
            datetime.strptime(req.check_out, "%Y-%m-%d") -
            datetime.strptime(req.check_in,  "%Y-%m-%d")
        ).days)
    except ValueError:
        nights = 1

    venue_coords: tuple[float, float] | None = None
    if req.meeting_venue and req.near_meeting_venue:
        venue_coords = await asyncio.to_thread(
            _nominatim_coords, f"{req.meeting_venue}, {destination_city}"
        )

    hotel_params = {
        "destination_city": destination_city,
        "check_in_date":    req.check_in,
        "check_out_date":   req.check_out,
        "airport_iata":     destination_iata,
        "adults":           req.passengers,
        "sort_by":          "rating",
    }
    if req.max_hotel_budget:
        hotel_params["max_budget"] = req.max_hotel_budget
    if req.min_stars:
        hotel_params["min_stars"] = req.min_stars
    if req.min_rating and req.max_rating:
        hotel_params["min_rating"] = req.min_rating
        hotel_params["max_rating"] = req.max_rating
    if req.amenities:
        hotel_params["amenities"] = req.amenities

    await asyncio.to_thread(hotels_tool.search_hotels.invoke, hotel_params)
    all_results = list(hotels_tool.last_results)

    # 0 TL / fiyatsız otelleri çıkar
    hotel_results = [h for h in all_results if h.price_per_night and h.price_per_night > 0]

    if not hotel_results:
        raise HTTPException(
            status_code=404,
            detail=f"{destination_city} için {req.check_in}–{req.check_out} arasında fiyatlı otel bulunamadı.",
        )

    def enrich(h) -> dict:
        d = h.model_dump()
        booking_url = d.get("platform_links", {}).get("Booking.com") or d.get("booking_url")
        d["platform_links"] = {"Booking.com": booking_url} if booking_url else {}
        if venue_coords and d.get("latitude") and d.get("longitude"):
            d["venue_distance_km"] = _haversine_km(
                d["latitude"], d["longitude"], venue_coords[0], venue_coords[1]
            )
        else:
            d["venue_distance_km"] = None
        d["hotel_total"] = round((d.get("price_per_night") or 0) * nights, 2)
        d["nights"] = nights
        return d

    hotels_enriched = [enrich(h) for h in hotel_results]

    if venue_coords:
        hotels_enriched.sort(
            key=lambda h: h["venue_distance_km"] if h["venue_distance_km"] is not None else 9999
        )

    return {
        "hotels":           hotels_enriched[:8],
        "destination_city": destination_city,
        "nights":           nights,
    }
