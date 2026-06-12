import pytest
from app.services.scoring_service import ScoringService

def test_scoring_service_approve():
    features = {
        'ratio_endettement': 0.20,
        'revenus_mensuels': 100000,
        'anciennete_emploi_mois': 24
    }
    result = ScoringService.compute_score(features)
    assert result["score"] == 100
    assert result["decision"] == "APPROVE"

def test_scoring_service_reject():
    features = {
        'ratio_endettement': 0.50, # -30
        'revenus_mensuels': 40000, # -20
        'anciennete_emploi_mois': 6  # -15
    }
    result = ScoringService.compute_score(features)
    assert result["score"] == 35 # 100 - 65 = 35
    assert result["decision"] == "REJECT"
