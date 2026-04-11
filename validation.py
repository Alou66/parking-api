import re

IMM_RE = re.compile(r"^[A-Z0-9\-]{3,15}$")

def normaliser_texte(s: str) -> str:
    return " ".join((s or "").strip().upper().split())

def valider_immatriculation(raw: str):
    raw = normaliser_texte(raw)
    if not raw:
        return None, "Immatriculation vide."
    if not IMM_RE.match(raw):
        return None, "Immatriculation invalide."
    return raw, None

def valider_texte(raw: str, champ: str):
    raw = normaliser_texte(raw)
    if not raw or len(raw) < 2:
        return None, f"{champ} invalide."
    return raw, None