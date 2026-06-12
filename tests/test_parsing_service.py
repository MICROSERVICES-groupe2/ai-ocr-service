import pytest
from app.services.parsing_service import ParsingService

def test_parsing_service_extracts_data():
    text = "NOM DUPONT\nPrénom Jean\nDate de naissance 12/05/1980\nSalaire net : 500 000 FCFA\nEmployeur : ACME Corp"
    result = ParsingService.parse(text, 95.0)
    
    assert result["nom"] == "DUPONT"
    assert result["prenom"] == "Jean"
    assert result["dateNaissance"] == "12/05/1980"
    assert result["revenus"] == 500000.0
    assert "ACME" in result["employeur"]
