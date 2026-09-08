"""
IBVAP - Suspicious Activity Pattern Evaluator
Detects compound behavioral patterns: vehicle drop-off, loitering breach, and multi-entity rendezvous.
"""
from typing import List, Dict, Any

class SuspiciousActivityEngine:
    def detect_compound_patterns(
        self,
        has_vehicle: bool,
        has_person: bool,
        is_night: bool,
        is_inside_red_zone: bool,
        dwell_seconds: float
    ) -> List[Dict[str, Any]]:
        patterns = []

        # Pattern 1: Coordinated Drop-off Breach
        if has_vehicle and has_person and is_inside_red_zone:
            patterns.append({
                "pattern_name": "Vehicle Drop-off & Perimeter Breach",
                "severity": "CRITICAL",
                "risk_points": 35,
                "description": "Vehicle approached boundary and disembarked target directly inside restricted buffer"
            })

        # Pattern 2: Night Reconnaissance Loitering
        if is_night and is_inside_red_zone and dwell_seconds > 25.0:
            patterns.append({
                "pattern_name": "Night-time Reconnaissance Loitering",
                "severity": "HIGH",
                "risk_points": 30,
                "description": "Target loitering at night without authorized transponder signal"
            })

        return patterns

suspicious_activity_engine = SuspiciousActivityEngine()
