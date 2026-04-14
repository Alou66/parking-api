from pydantic import BaseModel, Field
from typing import Optional

class VehiculeBase(BaseModel):
    immatriculation: str = Field(..., example="DK-1234-AB")
    marque: str = Field(..., example="Toyota")
    modele: str = Field(..., example="Corolla")

class VehiculeCreate(VehiculeBase):
    pass

class Vehicule(VehiculeBase):
    heure_entree: str

class Place(BaseModel):
    numero: int
    etu: bool
    vehicule: Optional[Vehicule] = None

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str