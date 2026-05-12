from typing import TypedDict , List, Union
from pydantic import BaseModel, Field
 

class FlightOption(BaseModel):
    airline: str
    flight_no: str
    departure_time: Union[str, List[str]]
    arrival_time: str
    duration: str | None = None     
    stops: int = 0                 
    price: float
    currency: str
    origin: str
    destination: str
    arrival_airport: str
    offer_id: str | None = None     
    booking_url: str | None = None

class HotelOption(BaseModel):
    name: str
    price_per_night: float
    currency: str
    stars: int | None = None
    distance_km: float = 0.0
    platform: str | None = None
    booking_url: str | None = None
    latitude: float = 0.0
    longitude: float = 0.0
    amenities: list[str] = []
    airport_distance_km: float | None = None
    airport_duration: str | None = None
    platform_links: dict[str, str] = {}

class TransportOption(BaseModel):
    via: str
    duration_minutes: int = 0
    price: float | None = None
    steps: list[str] = []
    maps_url: str | None = None

class TravelPackage(BaseModel):
    flight: FlightOption       
    hotel: HotelOption          
    transport: TransportOption  
    total_price: float

# ── LangGraph state ──────────────────────────────────

class TravelState(TypedDict):
    # kullanıcıdan gelenler
    origin_city: str
    destination_city: str
    travel_date: str
    travel_date_end: str | None
    person_count: int
    flight_budget: float | None
    hotel_budget: float | None
    time_range: tuple[str, str] | None
    preferred_airline: str | None
    purpose: str                       
    venue_name: str | None

    # agent'ın doldurduğu alanlar
    place_coords: tuple[float, float] | None
    flight_options: list[FlightOption] | None  
    hotels: list[HotelOption] | None 
    transports: list[TransportOption] | None  
    selected_flight: FlightOption | None
    selected_hotel: HotelOption | None        
    selected_transport: TransportOption | None
    packages: list[TravelPackage] | None
    current_step: str