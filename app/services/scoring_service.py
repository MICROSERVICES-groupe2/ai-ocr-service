from app.core.logging import logger

class ScoringService:
    @staticmethod
    def compute_score(features: dict) -> dict:
        logger.info("Computing credit score")
        score = 100
        factors = []
        
        ratio_endettement = features.get('ratio_endettement', 0)
        revenus_mensuels = features.get('revenus_mensuels', 0)
        anciennete_emploi_mois = features.get('anciennete_emploi_mois', 12)
        
        if ratio_endettement > 0.40:
            score -= 30
            factors.append("ratio_endettement_eleve")
        else:
            factors.append("ratio_endettement_ok")
            
        if revenus_mensuels < 50000:
            score -= 20
            factors.append("revenus_insuffisants")
        else:
            factors.append("revenus_suffisants")
            
        if anciennete_emploi_mois < 12:
            score -= 15
            factors.append("anciennete_emploi_faible")
            
        score = max(0, score)
        
        if score > 70:
            decision = "APPROVE"
        elif score >= 40:
            decision = "MANUAL_REVIEW"
        else:
            decision = "REJECT"
            
        logger.info(f"Computed score: {score}, decision: {decision}")
        
        return {
            "score": score,
            "decision": decision,
            "factors": factors
        }
