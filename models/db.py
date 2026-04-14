from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class VehiculeDB(SQLModel, table=True):
    __tablename__ = "vehicules"
    
    id: int | None = Field(default=None, primary_key=True)
    immatriculation: str = Field(max_length=15, unique=True, index=True)
    marque: str = Field(max_length=100)
    modele: str = Field(max_length=100)
    heure_entree: datetime = Field(default_factory=datetime.now)
    
    place_id: int | None = Field(default=None, foreign_key="places.id")
    place: "PlaceDB" = Relationship(back_populates="vehicule")


class PlaceDB(SQLModel, table=True):
    __tablename__ = "places"
    
    id: int | None = Field(default=None, primary_key=True)
    numero: int = Field(unique=True, index=True)
    etu: bool = Field(default=False, sa_column_kwargs={"name": "etu"})
    
    vehicule: Optional[VehiculeDB] = Relationship(back_populates="place")