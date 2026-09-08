"""
IBVAP - Explainable AI Alert Card Generator
Generates transparent human-in-the-loop decision cards answering WHAT, WHO, WHERE, WHEN, WHY, CONFIDENCE.
"""
from typing import Dict, Any, List

class ExplainabilityEngine:
    def build_card(
        self,
        what: str,
        who: str,
        where: str,
        when: str,
        why_factors: List[str],
        confidence: float,
        risk_score: int,
        severity: str,
        evidence_frame: str = None
    ) -> Dict[str, Any]:
        return {
            "what": what,
            "who": who,
            "where": where,
            "when": when,
            "why_factors": why_factors,
            "confidence_score": round(confidence, 2),
            "risk_score": risk_score,
            "severity": severity,
            "evidence_frame": evidence_frame,
            "advisory": "Decision support alert. Verify operational context before physical escalation."
        }

explainability_engine = ExplainabilityEngine()
