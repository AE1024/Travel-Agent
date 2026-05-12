from typing import List
import os
import re
from urllib.parse import quote as url_quote
from langchain.tools import tool
from agent.state import TransportOption
from serpapi import GoogleSearch

from dotenv import load_dotenv
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise EnvironmentError("SERPAPI_KEY bulunamadı. backend/.env dosyasını kontrol edin.")

last_results: List[TransportOption] = []

_MODE_TO_INT: dict[str, int] = {
    "driving": 0,
    "cycling": 1,
    "walking": 2,
    "transit": 3,
    "flight": 4,
    "best": 6,
}

_INT_TO_MODE: dict[int, str] = {v: k for k, v in _MODE_TO_INT.items()}


def _parse_formatted_duration(text: str) -> int:
    """Convert '1 hour 20 mins' or '45 mins' to total minutes."""
    hours = re.search(r"(\d+)\s*hour", text, re.IGNORECASE)
    mins  = re.search(r"(\d+)\s*min",  text, re.IGNORECASE)
    return (int(hours.group(1)) * 60 if hours else 0) + (int(mins.group(1)) if mins else 0)


def _build_maps_url(origin: str, destination: str) -> str:
    """Generate a Google Maps directions URL between two locations."""
    o = url_quote(origin, safe="")
    d = url_quote(destination, safe="")
    return f"https://www.google.com/maps/dir/{o}/{d}"


@tool("search_transport")
def search_transport(
    airport_iata: str,
    hotel_name: str,
    via: str | None = None,
    airport_city: str | None = None,
) -> str:
    """Search for airport-to-hotel transfer options (taxi, shuttle, public transport).
    airport_iata: Arrival airport IATA code (e.g. 'CDG').
    hotel_name: Name of the destination hotel.
    via: Travel mode — one of: driving, cycling, walking, transit, flight, best. Defaults to best.
    airport_city: City name for the airport (e.g. 'Paris'). Used to build a more precise start address.
    """
    global last_results
    last_results = []

    start = f"{airport_city} Airport" if airport_city else f"{airport_iata} International Airport"
    fallback_maps_url = _build_maps_url(start, hotel_name)

    params = {
        "engine": "google_maps_directions",
        "start_addr": start,
        "end_addr": hotel_name,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }
    if via:
        mode_int = _MODE_TO_INT.get(via.lower())
        if mode_int is not None:
            params["travel_mode"] = mode_int

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        last_results = [TransportOption(via="Google Maps Rotası", maps_url=fallback_maps_url)]
        return f"SerpAPI hatası: {e}"

    if "error" in results:
        last_results = [TransportOption(via="Google Maps Rotası", maps_url=fallback_maps_url)]
        return f"Arama hatası: {results['error']}"

    directions = results.get("directions", [])
    serpapi_maps_url = results.get("search_metadata", {}).get("google_maps_url")

    if not directions:
        last_results = [TransportOption(via="Google Maps Rotası", maps_url=fallback_maps_url)]
        return "Yön bulunamadı. Google Maps bağlantısı oluşturuldu."

    all_transports: List[TransportOption] = []
    for direction in directions:
        raw_mode = direction.get("travel_mode", 6)
        if isinstance(raw_mode, str):
            mode_label = raw_mode.capitalize()
        else:
            mode_label = _INT_TO_MODE.get(int(raw_mode), str(raw_mode)).capitalize()
        route = direction.get("via", "")

        formatted = direction.get("formatted_duration")
        if formatted:
            duration_minutes = _parse_formatted_duration(formatted)
        else:
            duration_minutes = round(direction.get("duration", 0) / 60)

        extensions = direction.get("extensions", {})
        if not isinstance(extensions, dict):
            extensions = {}
        cost_raw = extensions.get("fare") or direction.get("cost")
        price = float(cost_raw) if cost_raw is not None else None

        steps = [
            trip.get("title", "")
            for trip in direction.get("trips", [])
            if trip.get("title")
        ]

        maps_url = (
            direction.get("maps_url")
            or serpapi_maps_url
            or fallback_maps_url
        )

        all_transports.append(TransportOption(
            via=f"{mode_label} — {route}" if route else mode_label,
            duration_minutes=duration_minutes,
            price=price,
            steps=steps,
            maps_url=maps_url,
        ))

    transport_options = all_transports[:3]

    # Ensure every option has at least the fallback maps_url
    for t in transport_options:
        if not t.maps_url:
            t.maps_url = fallback_maps_url

    last_results = transport_options

    if not transport_options:
        last_results = [TransportOption(via="Google Maps Rotası", maps_url=fallback_maps_url)]
        return "Geçerli ulaşım seçeneği bulunamadı. Google Maps bağlantısı oluşturuldu."

    return "\n\n".join(
        f"{t.via} | {t.duration_minutes} dk"
        + (f" | ₺{t.price:.2f}" if t.price is not None else "")
        + ("\n" + "\n".join(f"  - {s}" for s in t.steps) if t.steps else "")
        for t in transport_options
    )
