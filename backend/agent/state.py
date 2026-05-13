from typing import Union, List
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
    rating: float | None = None
    airport_distance_km: float | None = None
    airport_duration: str | None = None
    platform_links: dict[str, str] = {}

class TransportOption(BaseModel):
    via: str
    duration_minutes: int = 0
    price: float | None = None
    steps: list[str] = []
    maps_url: str | None = None

