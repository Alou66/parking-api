"""
storage.py - Couche d'accès aux données PostgreSQL

Remplace le stockage JSON par PostgreSQL tout en gardant
la même interface pour services.py (DIP - Dependency Inversion)
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Session, SQLModel, create_engine, select, col

from models.db import PlaceDB, VehiculeDB
from config import get_settings


class StorageError(Exception):
    """Exception personnalisée pour les erreurs de stockage"""
    pass


class ParkingStorage:
    """
    Classe de stockage PostgreSQL.
    
    Interface Compatible avec l'ancienne version JSON:
    - __init__(file_path): paramètre ignoré (compatibilité)
    - lire(): retourne {"places": [...]} au format JSON
    - ecrire(data): méthode conservée mais inutile (transactions DB)
    """
    
    def __init__(self, file_path: str = None):
        settings = get_settings()
        
        self.engine = create_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True
        )
        
        SQLModel.metadata.create_all(self.engine)
    
    def lire(self) -> dict:
        try:
            with Session(self.engine) as session:
                places = session.exec(select(PlaceDB)).all()
                
                result = {"places": []}
                
                for place in places:
                    place_dict = {
                        "numero": place.numero,
"etu": place.etu,
                        "vehicule": None
                    }
                    
                    if place.vehicule:
                        place_dict["vehicule"] = {
                            "immatriculation": place.vehicule.immatriculation,
                            "marque": place.vehicule.marque,
                            "modele": place.vehicule.modele,
                            "heure_entree": place.vehicule.heure_entree.isoformat()
                        }
                    
                    result["places"].append(place_dict)
                
                return result
                
        except Exception as e:
            raise StorageError(f"Erreur lecture DB: {e}")
    
    def ecrire(self, data: dict) -> None:
        pass
    
    def initiale(self, nombre: int) -> dict:
        try:
            with Session(self.engine) as session:
                existant = session.exec(select(PlaceDB)).first()
                if existant:
                    return {"message": "Parking deja initialise"}
                
                for i in range(1, nombre + 1):
                    place = PlaceDB(numero=i, etu=False)
                    session.add(place)
                
                session.commit()
                return {"message": f"Parking initialise avec {nombre} places"}
                
        except Exception as e:
            raise StorageError(f"Erreur initialisation: {e}")
    
    def trouver_place_libre(self) -> Optional[dict]:
        try:
            with Session(self.engine) as session:
                place = session.exec(
                    select(PlaceDB)
                    .where(PlaceDB.etu == False)
                    .order_by(PlaceDB.numero)
                ).first()
                
                if place:
                    return {"numero": place.numero}
                return None
                
        except Exception as e:
            raise StorageError(f"Erreur recherche place libre: {e}")
    
    def trouver_place_par_imm(self, imm: str) -> Optional[dict]:
        try:
            with Session(self.engine) as session:
                vehicule = session.exec(
                    select(VehiculeDB).where(
                        VehiculeDB.immatriculation == imm
                    )
                ).first()
                
                if vehicule and vehicule.place:
                    return {"numero": vehicule.place.numero}
                return None
                
        except Exception as e:
            raise StorageError(f"Erreur recherche par imm: {e}")
    
    def trouver_place_par_numero(self, numero: int) -> Optional[dict]:
        try:
            with Session(self.engine) as session:
                place = session.exec(
                    select(PlaceDB).where(PlaceDB.numero == numero)
                ).first()
                
                if place:
                    return {"numero": place.numero, "etu": place.etu}
                return None
                
        except Exception as e:
            raise StorageError(f"Erreur recherche par numero: {e}")
    
    def trouver_vehicule(self, imm: str) -> Optional[dict]:
        try:
            with Session(self.engine) as session:
                vehicule = session.exec(
                    select(VehiculeDB).where(
                        VehiculeDB.immatriculation == imm
                    )
                ).first()
                
                if vehicule:
                    return {
                        "immatriculation": vehicule.immatriculation,
                        "marque": vehicule.marque,
                        "modele": vehicule.modele,
                        "heure_entree": vehicule.heure_entree.isoformat()
                    }
                return None
                
        except Exception as e:
            raise StorageError(f"Erreur recherche vehicule: {e}")
    
    def garer(self, numero: int, imm: str, marque: str, modele: str) -> dict:
        try:
            with Session(self.engine) as session:
                place = session.exec(
                    select(PlaceDB).where(PlaceDB.numero == numero)
                ).first()
                
                if not place:
                    raise StorageError("Place introuvable")
                
                if place.etu:
                    raise StorageError("Place deja etu")
                
                vehicule = VehiculeDB(
                    immatriculation=imm,
                    marque=marque,
                    modele=modele,
                    heure_entree=datetime.now()
                )
                
                place.etu = True
                place.vehicule = vehicule
                
                session.add(place)
                session.add(vehicule)
                session.commit()
                session.refresh(place)
                
                return {
                    "numero": place.numero,
                    "etu": place.etu,
                    "vehicule": {
                        "immatriculation": imm,
                        "marque": marque,
                        "modele": modele,
                        "heure_entree": vehicule.heure_entree.isoformat()
                    }
                }
                
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(f"Erreur garer: {e}")
    
    def liberer(self, numero: int) -> Optional[dict]:
        try:
            with Session(self.engine) as session:
                place = session.exec(
                    select(PlaceDB).where(PlaceDB.numero == numero)
                ).first()
                
                if not place:
                    return None
                
                vehicule = place.vehicule
                place.etu = False
                place.vehicule = None
                
                if vehicule:
                    session.delete(vehicule)
                
                session.commit()
                return {"numero": place.numero, "etu": False}
                
        except Exception as e:
            raise StorageError(f"Erreur liberer: {e}")
    
    def supprimer_place(self, numero: int) -> bool:
        try:
            with Session(self.engine) as session:
                place = session.exec(
                    select(PlaceDB).where(PlaceDB.numero == numero)
                ).first()
                
                if place:
                    session.delete(place)
                    session.commit()
                    return True
                return False
                
        except Exception as e:
            raise StorageError(f"Erreur suppression: {e}")
    
    def vehicule_existe(self, imm: str) -> bool:
        try:
            with Session(self.engine) as session:
                vehicule = session.exec(
                    select(VehiculeDB).where(
                        VehiculeDB.immatriculation == imm
                    )
                ).first()
                return vehicule is not None
                
        except Exception as e:
            raise StorageError(f"Erreur verification vehicule: {e}")