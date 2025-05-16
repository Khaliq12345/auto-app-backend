from pydantic import BaseModel
from typing import Optional


class Car(BaseModel):
    id: str
    name: Optional[str]
    price: Optional[float]
    deal_type: Optional[str]
    link: Optional[str]
    image: Optional[str]
    mileage: Optional[float]
    car_metadata: Optional[str]
    domain: Optional[str]
    fuel_type: Optional[str]
    boite_de_vitesse: Optional[str]
    parent_car_id: Optional[int]
    updated_at: Optional[str]
    matching_percentage: Optional[float]
    matching_percentage_reason: Optional[str]


class Filter(BaseModel):
    make: str
    model: str
    version: str
    color: str
    mileage: float
    fuel_type: str
    year_from: int
    year_to: int


class Match(BaseModel):
    matching_percentage: float
    matching_percentage_reason: Optional[str]
