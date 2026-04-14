from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from models import VehiculeCreate, Place, MessageResponse
from storage import ParkingStorage
from services import ParkingService, ServiceError

app = FastAPI(title="API Parking")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = ParkingStorage()
service = ParkingService(storage)

@app.post("/init", response_model=MessageResponse)
def init(nombre: int):
    return service.init_parking(nombre)

@app.post("/garer", response_model=Place)
def garer(v: VehiculeCreate):
    try:
        return service.garer(v.immatriculation, v.marque, v.modele)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sortir/{imm}", response_model=MessageResponse)
def sortir(imm: str):
    try:
        return service.sortir(imm)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parking")
def parking():
    return service.tous()

@app.get("/vehicule/{imm}", response_model=Place)
def rechercher(imm: str):
    try:
        return service.rechercher(imm)
    except ServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/place/{numero}", response_model=MessageResponse)
def supprimer(numero: int):
    try:
        return service.supprimer_place(numero)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))