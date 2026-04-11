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
        data = {"places": []}
        for i in range(1, nombre + 1):
            data["places"].append({
                "numero": i,
                "occupee": False,
                "vehicule": None
            })
        self.storage.ecrire(data)
        return {"message": "Parking initialise"}

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

        data = self.storage.lire()

        for p in data["places"]:
            if p["vehicule"] and p["vehicule"]["immatriculation"] == imm:
                raise ServiceError("Vehicule deja present.")

        for p in data["places"]:
            if not p["occupee"]:
                p["occupee"] = True
                p["vehicule"] = {
                    "immatriculation": imm,
                    "marque": m,
                    "modele": mod,
                    "heure_entree": datetime.now().isoformat()
                }
                self.storage.ecrire(data)
                return p

        raise ServiceError("Parking plein.")

    def sortir(self, raw_imm):
        imm, _ = valider_immatriculation(raw_imm)
        data = self.storage.lire()

        for p in data["places"]:
            if p["vehicule"] and p["vehicule"]["immatriculation"] == imm:
                heure = datetime.fromisoformat(p["vehicule"]["heure_entree"])
                duree = datetime.now() - heure
                prix = round((duree.total_seconds() / 3600) * 500)

                p["occupee"] = False
                p["vehicule"] = None
                self.storage.ecrire(data)

                return {"message": f"Sortie OK. Prix: {prix} FCFA"}

        raise ServiceError("Vehicule introuvable.")

    def tous(self):
        return self.storage.lire()

    def rechercher(self, raw_imm):
        imm, _ = valider_immatriculation(raw_imm)
        data = self.storage.lire()

        for p in data["places"]:
            if p["vehicule"] and p["vehicule"]["immatriculation"] == imm:
                return p

        raise ServiceError("Vehicule introuvable.")

    def supprimer_place(self, numero: int):
        data = self.storage.lire()

        for p in data["places"]:
            if p["numero"] == numero:
                if p["occupee"]:
                    raise ServiceError("Place occupee.")
                data["places"].remove(p)
                self.storage.ecrire(data)
                return {"message": "Place supprimee"}

        raise ServiceError("Place introuvable.")
