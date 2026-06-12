import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}

def test_scoring_api():
    response = client.post("/api/scoring/calculate", json={
        "revenus_mensuels": 200000,
        "montant_demande": 1000000,
        "duree_mois": 12,
        "anciennete_emploi_mois": 36
    })
    assert response.status_code == 200
    assert response.json()["decision"] in ["APPROVE", "MANUAL_REVIEW", "REJECT"]
