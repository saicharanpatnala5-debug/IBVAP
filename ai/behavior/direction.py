"""
IBVAP - Direction & Velocity Heading Vector Analyzer
Determines whether target velocity vector is heading inward toward strategic border post.
"""
from typing import Dict, Any
import math

class DirectionAnalyzer:
    def classify_heading(self, vx: float, vy: float) -> Dict[str, Any]:
        """
        Classify direction vector:
        Inward toward installation: Positive Y or 45-135 degrees
        """
        speed = math.sqrt(vx**2 + vy**2)
        if speed < 0.01:
            return {"direction": "Stationary", "is_inward": False, "heading_deg": 0.0}

        angle_deg = math.degrees(math.atan2(vy, vx))
        is_inward = 30 <= angle_deg <= 150

        return {
            "direction": "Inward (Toward Perimeter)" if is_inward else "Outward",
            "is_inward": is_inward,
            "heading_deg": round(angle_deg, 1),
            "speed": round(speed, 3)
        }

direction_analyzer = DirectionAnalyzer()
