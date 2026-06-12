import re
from app.core.logging import logger

class ParsingService:
    @staticmethod
    def parse(text: str, confidence: float) -> dict:
        logger.info(f"Parsing extracted text (len={len(text)}): {repr(text)}")
        
        parsed_data = {
            "nom": None,
            "prenom": None,
            "numeroId": None,
            "dateNaissance": None,
            "revenus": 0.0,
            "employeur": None,
            "confidence": confidence
        }
        
        # Date de naissance (DD/MM/YYYY ou DD-MM-YYYY)
        dob_match = re.search(r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b', text)
        if dob_match:
            parsed_data["dateNaissance"] = dob_match.group(1)
            
        # Revenus (salaire, net à payer, etc. followed by amount in XAF/FCFA)
        # e.g., "Salaire net : 500 000 FCFA", "Net à payer 150000 XAF"
        rev_match = re.search(r'(?:salaire|net[ \w]*payer|revenu)[^\d]*([\d\s]+)', text, re.IGNORECASE)
        if rev_match:
            amount_str = rev_match.group(1).replace(" ", "")
            try:
                parsed_data["revenus"] = float(amount_str)
            except ValueError:
                pass
                
        # Numéro ID (approximatif pour CNI/Passeport)
        # Supposons un numéro alphanumérique de 9 à 14 caractères
        id_match = re.search(r'\b([A-Z0-9]{9,14})\b', text)
        if id_match:
            parsed_data["numeroId"] = id_match.group(1)
            
        # Nom
        nom_match = re.search(r'\bnom[\s:]*([A-Za-zÀ-ÿ]+)', text, re.IGNORECASE)
        if nom_match:
            parsed_data["nom"] = nom_match.group(1).upper()
            
        # Prénom
        prenom_match = re.search(r'\bpr[eéè]nom[\s:]*([A-Za-zÀ-ÿ]+)', text, re.IGNORECASE)
        if prenom_match:
            parsed_data["prenom"] = prenom_match.group(1).capitalize()
            
        # Employeur (approximatif, après "Employeur :" ou "Raison sociale")
        emp_match = re.search(r'(?:employeur|raison sociale)[\s:]*([A-Za-z0-9\sÀ-ÿ]+)', text, re.IGNORECASE)
        if emp_match:
            # Nettoyage basique
            employeur = emp_match.group(1).strip()
            # Prendre jusqu'au premier saut de ligne ou mot clé perturbateur
            parsed_data["employeur"] = employeur.split('\n')[0][:50].strip()

        return parsed_data
