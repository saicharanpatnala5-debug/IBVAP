"""
IBVAP - Risk Rules & Context Overrides
"""
from typing import Dict, Any

class RiskRules:
    @staticmethod
    def is_critical_escalation(risk_score: int, is_zone_breach: bool, is_night: bool) -> bool:
        return risk_score >= 120 or (is_zone_breach and is_night and risk_score >= 90)

risk_rules = RiskRules()
