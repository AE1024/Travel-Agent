import os
import math
import requests
from datetime import datetime
from typing import List
from urllib.parse import quote_plus
from langchain.tools import tool
from agent.state import HotelOption
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise EnvironmentError("SERPAPI_KEY bulunamadı. backend/.env dosyasını kontrol edin.")

last_results: List[HotelOption] = []

AMENITY_CODES = {
    "free_breakfast": 1,
    "free_parking": 2,
    "free_wifi": 3,
    "air_conditioning": 4,
    "pool": 5,
    "hot_tub": 6,
    "gym": 11,
    "outdoor_pool": 12,
    "indoor_pool": 13,
    "restaurant": 14,
    "kid_friendly": 15,
    "spa": 16,
    "airport_shuttle": 19,
    "bar": 20,
    "beach_access": 22,
}

TOP_PLATFORMS = {
    "Booking.com": lambda name, cin, cout, adults: (
        f"https://www.booking.com/search.html?ss={quote_plus(name)}"
        f"&checkin={cin}&checkout={cout}&group_adults={adults}&no_rooms=1"
    ),
    "Hotels.com": lambda name, cin, cout, adults: (
        f"https://www.hotels.com/search.do?q-destination={quote_plus(name)}"
        f"&q-check-in={cin}&q-check-out={cout}&q-rooms=1&q-room-0-adults={adults}"
    ),
    "Expedia": lambda name, cin, cout, adults: (
        f"https://www.expedia.com/Hotel-Search?destination={quote_plus(name)}"
        f"&startDate={cin}&endDate={cout}&adults={adults}"
    ),
}

PLATFORM_ALIASES = {
    "booking":  "Booking.com",
    "hotels":   "Hotels.com",
    "expedia":  "Expedia",
}


def _get_airport_coords(airport_iata: str) -> tuple[float, float] | None:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{airport_iata} international airport", "format": "json", "limit": 1}
    headers = {"User-Agent": "TravelAgent/1.0"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


def _distance_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return round(2 * R * math.asin(math.sqrt(a)), 2)


def _build_platform_links(name: str, cin: str, cout: str, adults: int, prices_list: list) -> dict[str, str]:
    serpapi_links: dict[str, str] = {}
    for p in prices_list:
        src = p.get("source", "").lower().replace(".", "").replace(" ", "")
        lnk = p.get("link", "")
        if not lnk:
            continue
        for alias, canonical in PLATFORM_ALIASES.items():
            if alias in src:
                serpapi_links[canonical] = lnk
                break

    result: dict[str, str] = {}
    for platform, builder in TOP_PLATFORMS.items():
        result[platform] = serpapi_links.get(platform) or builder(name, cin, cout, adults)
    return result


def _extract_price(rate_dict: dict) -> float:
    v = rate_dict.get("extracted_lowest")
    if v is not None and float(v) > 0:
        return float(v)
    v = rate_dict.get("extracted_before_taxes_fees")
    if v is not None and float(v) > 0:
        return float(v)
    return 0.0


@tool("search_hotels")
def search_hotels(
    destination_city: str,
    check_in_date: str,
    check_out_date: str,
    airport_iata: str | None = None,
    adults: int = 1,
    children: int = 0,
    children_ages: list[int] | None = None,
    max_budget: float | None = None,
    currency: str = "TRY",
    min_stars: int | None = None,
    near_airport: bool = False,
    hotel_name: str | None = None,
    amenities: list[str] | None = None,
    sort_by: str | None = None,
) -> str:
    """Search for available hotels across Booking.com and Airbnb.
    airport_iata: Destination airport IATA code (e.g. 'LHR'). Used to calculate distance.
    sort_by: 'price' (lowest first) or 'rating' (highest rated first).
    """

    global last_results
    last_results = []

    try:
        cin  = datetime.strptime(check_in_date,  "%Y-%m-%d")
        cout = datetime.strptime(check_out_date, "%Y-%m-%d")
        if cout <= cin:
            return f"Hata: check_out_date ({check_out_date}), check_in_date ({check_in_date}) tarihinden sonra olmalı."
    except ValueError as e:
        return f"Geçersiz tarih formatı: {e}"

    nights = (cout - cin).days

    airport_coords: tuple[float, float] | None = None
    if airport_iata:
        airport_coords = _get_airport_coords(airport_iata.upper())

    query = hotel_name if hotel_name else destination_city
    if near_airport and not hotel_name:
        query = f"{destination_city} near airport"

    params: dict = {
        "engine": "google_hotels",
        "q": query,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": adults,
        "currency": currency,
        "hl": "tr",
        "api_key": SERPAPI_KEY,
    }

    if children > 0:
        ages = children_ages if children_ages and len(children_ages) == children else [5] * children
        params["children"] = children
        params["children_ages"] = ",".join(str(a) for a in ages)

    if max_budget:
        params["max_price"] = int(max_budget)
    if min_stars:
        params["hotel_class"] = min_stars
    if sort_by == "price":
        params["sort_by"] = 3
    elif sort_by == "rating":
        params["sort_by"] = 8

    if amenities:
        codes = [AMENITY_CODES[a] for a in amenities if a in AMENITY_CODES]
        if codes:
            params["amenities"] = ",".join(str(c) for c in codes)

    print(f"[HOTELS] q={query!r} in={check_in_date} out={check_out_date} adults={adults} sort={sort_by}")

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        return f"SerpAPI hatası: {e}"

    if "error" in results:
        print(f"[HOTELS] SerpAPI error: {results['error']}")
        return f"Arama hatası: {results['error']}"

    properties = results.get("properties", [])
    status = results.get("search_metadata", {}).get("status", "")
    print(f"[HOTELS] {destination_city} → {len(properties)} sonuç (status={status})")

    all_hotels: List[HotelOption] = []

    for h in properties:
        price = _extract_price(h.get("rate_per_night", {}))
        prices_list = h.get("prices", [])
        if price == 0.0:
            for p in prices_list:
                price = _extract_price(p.get("rate_per_night", {}))
                if price:
                    break

        hotel_class_raw = h.get("hotel_class")
        try:
            stars = int(hotel_class_raw) if hotel_class_raw else None
        except (ValueError, TypeError):
            stars = None

        gps = h.get("gps_coordinates", {})
        lat = float(gps.get("latitude", 0.0))
        lon = float(gps.get("longitude", 0.0))

        airport_duration = None
        for place in h.get("nearby_places", []):
            if "airport" in place.get("name", "").lower():
                transports = place.get("transportations", [])
                if transports:
                    airport_duration = transports[0].get("duration")
                break

        airport_distance_km = None
        if airport_coords and lat and lon:
            airport_distance_km = _distance_km(lat, lon, airport_coords[0], airport_coords[1])

        hotel_name_str = h.get("name", "")
        platform_links = _build_platform_links(
            hotel_name_str, check_in_date, check_out_date, adults, prices_list
        )

        all_hotels.append(HotelOption(
            name=hotel_name_str,
            price_per_night=price,
            currency=currency,
            stars=stars,
            platform="Booking.com",
            booking_url=platform_links.get("Booking.com"),
            latitude=lat,
            longitude=lon,
            amenities=h.get("amenities", []),
            airport_distance_km=airport_distance_km,
            airport_duration=airport_duration,
            platform_links=platform_links,
        ))

    if amenities and "free_breakfast" in amenities:
        def _has_free_breakfast(h: HotelOption) -> bool:
            for a in h.amenities:
                a_lower = a.lower()
                if "breakfast" in a_lower and "$" not in a and "(" not in a:
                    return True
            return False
        all_hotels = [h for h in all_hotels if _has_free_breakfast(h)]

    if near_airport and airport_coords:
        all_hotels.sort(key=lambda h: h.airport_distance_km or 9999)

    priced   = [h for h in all_hotels if h.price_per_night > 0]
    unpriced = [h for h in all_hotels if h.price_per_night == 0]
    top = (priced + unpriced)[:10]

    print(f"[HOTELS] fiyatlı={len(priced)} fiyatsız={len(unpriced)} → top={len(top)}")
    last_results = top

    if not top:
        return f"{destination_city} için {check_in_date} – {check_out_date} arasında uygun otel bulunamadı."

    lines = [f"📍 {destination_city} | {check_in_date} → {check_out_date} ({nights} gece) | {adults} yetişkin\n"]
    for i, h in enumerate(top, 1):
        stars_str   = f"{h.stars}⭐" if h.stars else ""
        total_price = round(h.price_per_night * nights) if h.price_per_night else 0
        total_str   = f" | Toplam: {total_price} {currency}" if total_price else ""
        amenities_line = f"\n   ✨ {' · '.join(h.amenities[:4])}" if h.amenities else ""
        dist_str = f"\n   ✈ Havalimanına {h.airport_distance_km} km" if h.airport_distance_km else ""
        lines.append(
            f"{i}. {h.name} {stars_str}\n"
            f"   💰 {h.price_per_night} {currency}/gece{total_str}"
            f"{amenities_line}{dist_str}"
        )

    return "\n".join(lines)
