from pydantic import BaseModel


class Car(BaseModel):
    id: str
    name: str
    price: float
    deal_type: str
    link: str
    image: list[str]
    mileage: float
    car_metadata: str
    domain: str
    fuel_type: str
    boite_de_vitesse: str
    parent_car_id: int
    updated_at: str


class Filter(BaseModel):
    make: str
    model: str
    version: str
    color: str
    mileage: float
    fuel_type: str
