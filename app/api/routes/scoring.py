from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.scoring_service import ScoringService

router = APIRouter()

class ScoringRequest(BaseModel):
    revenus_mensuels: float
    montant_demande: float
    duree_mois: int
    anciennete_emploi_mois: Optional[int] = 12

@router.post("/calculate")
def calculate_score(request: ScoringRequest):
    ratio = request.montant_demande / (request.revenus_mensuels * request.duree_mois) if request.revenus_mensuels > 0 and request.duree_mois > 0 else 1.0
    
    features = {
        'ratio_endettement': ratio,
        'revenus_mensuels': request.revenus_mensuels,
        'anciennete_emploi_mois': request.anciennete_emploi_mois
    }
    
    result = ScoringService.compute_score(features)
    return result
