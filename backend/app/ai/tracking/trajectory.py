"""
IBVAP - Trajectory Analysis Engine
Calculates trajectory metrics: velocity, acceleration, heading degree, and total displacement.
"""
from typing import List, Dict, Any, Tuple
import math

class TrajectoryEngine:
    def __init__(self, max_history: int = 100):
        self.max_history = max_history

    def analyze(self, points: List[Tuple[float, float]], timestamps: List[float]) -> Dict[str, Any]:
        """
        Analyzes a sequence of (x, y) points with timestamps (in seconds).
        """
        if len(points) < 2:
            return {
                "velocity": (0.0, 0.0),
                "speed": 0.0,
                "heading_deg": 0.0,
                "total_distance": 0.0,
                "dwell_time": 0.0
            }

        total_distance = 0.0
        for i in range(1, len(points)):
            dx = points[i][0] - points[i-1][0]
            dy = points[i][1] - points[i-1][1]
            total_distance += math.sqrt(dx**2 + dy**2)

        p_start = points[-min(5, len(points))]
        p_end = points[-1]
        dt = max(0.01, timestamps[-1] - timestamps[-min(5, len(timestamps))])

        vx = (p_end[0] - p_start[0]) / dt
        vy = (p_end[1] - p_start[1]) / dt
        speed = math.sqrt(vx**2 + vy**2)
        heading_deg = math.degrees(math.atan2(vy, vx))
        dwell_time = timestamps[-1] - timestamps[0]

        return {
            "velocity": (round(vx, 3), round(vy, 3)),
            "speed": round(speed, 3),
            "heading_deg": round(heading_deg, 1),
            "total_distance": round(total_distance, 3),
            "dwell_time": round(dwell_time, 1)
        }

trajectory_engine = TrajectoryEngine()
