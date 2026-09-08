"""
IBVAP - Context-Aware Risk Calculator
Directly implements Section 12 of the PRD.
"""
from typing import Dict, Any, List

class RiskCalculator:
    def __init__(self):
        self.weights = {
            "restricted_zone_intrusion": 30,
            "night_context": 15,
            "prolonged_loitering": 15,
            "inward_movement": 20,
            "unknown_vehicle": 20,
            "multiple_correlated_signals": 10
        }

    def compute(self, flags: Dict[str, bool]) -> Dict[str, Any]:
        total = 0
        factors = []

        for key, pts in self.weights.items():
            if flags.get(key, False):
                total += pts
                factors.append({"factor": key.replace('_', ' ').title(), "points": pts})

        return {"total_score": total, "contributing_factors": factors}

risk_calculator = RiskCalculator()
