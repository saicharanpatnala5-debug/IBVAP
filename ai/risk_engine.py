"""
IBVAP - Context-Aware Explainable Risk Scoring Engine
Converts heterogeneous multi-modal surveillance signals into transparent, explainable priority scores.
Directly implements Section 12 of the PRD and Section 10 of the TDD.
"""
from typing import List, Dict, Any, Tuple
from app.core.config import settings

class RiskScoringEngine:
    """
    Computes explainable risk score and categorizes severity into:
    0-29   : NORMAL   (No active alarm; logged as event)
    30-59  : LOW      (Low-priority event)
    60-89  : MEDIUM   (Operator notification)
    90-119 : HIGH     (Prominent alert + acknowledgement)
    120+   : CRITICAL (Escalation workflow + incident replay)
    """

    def __init__(self):
        self.weights = {
            "zone_intrusion": settings.WEIGHT_ZONE_INTRUSION,      # +30
            "night_context": settings.WEIGHT_NIGHT_CONTEXT,        # +15
            "loitering": settings.WEIGHT_LOITERING,                # +15
            "inward_direction": settings.WEIGHT_INWARD_DIRECTION,  # +20
            "unknown_vehicle": settings.WEIGHT_UNKNOWN_VEHICLE,    # +20
            "multiple_objects": settings.WEIGHT_MULTIPLE_OBJECTS   # +10
        }

    def evaluate_risk(
        self,
        is_zone_intrusion: bool = False,
        is_night_time: bool = False,
        is_loitering: bool = False,
        is_inward_movement: bool = False,
        is_unknown_vehicle: bool = False,
        has_multiple_objects: bool = False,
        additional_factors: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate all risk factors, calculate total score, determine severity,
        and generate explainable factor cards.
        """
        total_score = 0
        contributing_factors = []
        factor_explanations = []

        if is_zone_intrusion:
            pts = self.weights["zone_intrusion"]
            total_score += pts
            contributing_factors.append({
                "factor": "Restricted Zone Intrusion",
                "points": pts,
                "confidence": 0.95
            })
            factor_explanations.append("Object crossed configured virtual fence into high-security restricted area")

        if is_night_time:
            pts = self.weights["night_context"]
            total_score += pts
            contributing_factors.append({
                "factor": "Night-Time Surveillance Window",
                "points": pts,
                "confidence": 0.98
            })
            factor_explanations.append("Movement detected during low-visibility dark operational hours")

        if is_loitering:
            pts = self.weights["loitering"]
            total_score += pts
            contributing_factors.append({
                "factor": "Prolonged Loitering",
                "points": pts,
                "confidence": 0.91
            })
            factor_explanations.append(f"Target dwell time exceeded threshold (>{settings.LOITERING_DWELL_SECONDS}s) without departure")

        if is_inward_movement:
            pts = self.weights["inward_direction"]
            total_score += pts
            contributing_factors.append({
                "factor": "Inward Vector Toward Border Perimeter",
                "points": pts,
                "confidence": 0.88
            })
            factor_explanations.append("Calculated trajectory vector shows deliberate movement toward internal secure installation")

        if is_unknown_vehicle:
            pts = self.weights["unknown_vehicle"]
            total_score += pts
            contributing_factors.append({
                "factor": "Unregistered / Watchlist Vehicle Proximity",
                "points": pts,
                "confidence": 0.89
            })
            factor_explanations.append("Vehicle plate is not registered in authorized BOP database or matches watchlist alert")

        if has_multiple_objects:
            pts = self.weights["multiple_objects"]
            total_score += pts
            contributing_factors.append({
                "factor": "Multiple Correlated Entities",
                "points": pts,
                "confidence": 0.92
            })
            factor_explanations.append("Coordinated movement detected across multiple persons/vehicles in the sector")

        if additional_factors:
            for af in additional_factors:
                pts = af.get("points", 10)
                total_score += pts
                contributing_factors.append({
                    "factor": af.get("name", "Supplemental Signal"),
                    "points": pts,
                    "confidence": af.get("confidence", 0.85)
                })
                factor_explanations.append(af.get("description", "Supplementary detection flag"))

        # Determine severity
        if total_score <= settings.RISK_THRESHOLD_NORMAL:
            severity = "NORMAL"
        elif total_score <= settings.RISK_THRESHOLD_LOW:
            severity = "LOW"
        elif total_score <= settings.RISK_THRESHOLD_MEDIUM:
            severity = "MEDIUM"
        elif total_score <= settings.RISK_THRESHOLD_HIGH:
            severity = "HIGH"
        else:
            severity = "CRITICAL"

        return {
            "risk_score": total_score,
            "severity": severity,
            "contributing_factors": contributing_factors,
            "factor_explanations": factor_explanations
        }

    def build_explainability_card(
        self,
        what: str,
        who: str,
        where: str,
        when: str,
        why_factors: List[str],
        confidence: float,
        risk_score: int,
        severity: str,
        evidence_frame: str = None,
        evidence_clip: str = None
    ) -> Dict[str, Any]:
        """
        Builds the canonical Explainable AI Alert Card answering WHAT, WHO, WHERE, WHEN, WHY, CONFIDENCE.
        """
        return {
            "what": what,
            "who": who,
            "where": where,
            "when": when,
            "why_factors": why_factors,
            "confidence_score": round(confidence, 2),
            "evidence_frame": evidence_frame,
            "evidence_clip": evidence_clip,
            "risk_score": risk_score,
            "severity": severity,
            "advisory": "Human-in-the-loop decision support alert. Operator verification required."
        }

risk_engine = RiskScoringEngine()
