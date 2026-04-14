from typing import List, Optional
from datetime import datetime
from storage import ParkingStorage, StorageError
from validation import valider_immatriculation, valider_texte

class ServiceError(Exception):
    pass

class ParkingService:

    def __init__(self, storage: ParkingStorage):
        self.storage = storage

    def init_parking(self, nombre: int):
        return self.storage.initiale(nombre)

    def garer(self, raw_imm, marque, modele):
        imm, err = valider_immatriculation(raw_imm)
        if imm is None:
            raise ServiceError(err)

        m, err_m = valider_texte(marque, "Marque")
        if m is None:
            raise ServiceError(err_m)

        mod, err_mod = valider_texte(modele, "Modele")
        if mod is None:
            raise ServiceError(err_mod)

        if self.storage.vehicule_existe(imm):
            raise ServiceError("Vehicule deja present.")

        place_libre = self.storage.trouver_place_libre()
        if not place_libre:
            raise ServiceError("Parking plein.")

        return self.storage.garer(place_libre["numero"], imm, m, mod)

    def sortir(self, raw_imm):
        imm, _ = valider_immatriculation(raw_imm)
        
        place_info = self.storage.trouver_place_par_imm(imm)
        if not place_info:
            raise ServiceError("Vehicule introuvable.")
        
        vehicule = self.storage.trouver_vehicule(imm)
        if not vehicule:
            raise ServiceError("Vehicule introuvable.")
        
        heure = datetime.fromisoformat(vehicule["heure_entree"])
        duree = datetime.now() - heure
        prix = round((duree.total_seconds() / 3600) * 500)

        self.storage.liberer(place_info["numero"])

        return {"message": f"Sortie OK. Prix: {prix} FCFA"}

    def tous(self):
        return self.storage.lire()

    def rechercher(self, raw_imm):
        imm, _ = valider_immatriculation(raw_imm)
        
        place_info = self.storage.trouver_place_par_imm(imm)
        if not place_info:
            raise ServiceError("Vehicule introuvable.")
        
        data = self.storage.lire()
        for p in data["places"]:
            if p["vehicule"] and p["vehicule"]["immatriculation"] == imm:
                return p

        raise ServiceError("Vehicule introuvable.")

    def supprimer_place(self, numero: int):
        place_info = self.storage.trouver_place_par_numero(numero)
        if not place_info:
            raise ServiceError("Place introuvable.")
        
        if place_info["etu"]:
            raise ServiceError("Place occupee.")
        
        self.storage.supprimer_place(numero)
        return {"message": "Place supprimee"}