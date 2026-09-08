"""
IBVAP - Geometric and Spatial Trajectory Utilities
Implements Ray-Casting Point-in-Polygon containment, velocity vector, and direction estimation.
"""
import math
from typing import List, Tuple, Dict, Any, Optional

def is_point_in_polygon(point: List[float], polygon: List[List[float]]) -> bool:
    """
    Ray-Casting Algorithm to determine if point [x, y] is inside a polygon [[x1, y1], [x2, y2], ...].
    Works for both normalized coordinates (0.0 to 1.0) and pixel coordinates.
    """
    if len(polygon) < 3:
        return False

    x, y = point[0], point[1]
    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0]

    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y):
            if x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def calculate_velocity_and_direction(trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate velocity vector (vx, vy), speed, and heading direction from trajectory points.
    Each point is dict: {"x": float, "y": float, "t": float (timestamp in seconds)}
    """
    if len(trajectory) < 2:
        return {
            "vx": 0.0,
            "vy": 0.0,
            "speed": 0.0,
            "heading_deg": 0.0,
            "direction_label": "Stationary",
            "is_inward_movement": False
        }

    p_first = trajectory[-min(5, len(trajectory))]
    p_last = trajectory[-1]

    dx = p_last["x"] - p_first["x"]
    dy = p_last["y"] - p_first["y"]
    dt = max(0.01, p_last.get("t", 1.0) - p_first.get("t", 0.0))

    vx = dx / dt
    vy = dy / dt
    speed = math.sqrt(vx**2 + vy**2)

    # Angle in degrees (-180 to 180)
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)

    # Direction classification (Border convention: positive Y or angle towards lower center is inward)
    if speed < 0.02:
        direction_label = "Stationary / Loitering"
        is_inward = False
    elif 45 <= angle_deg <= 135:
        direction_label = "Inward (Toward Border Perimeter)"
        is_inward = True
    elif -135 <= angle_deg <= -45:
        direction_label = "Outward (Away from Perimeter)"
        is_inward = False
    elif -45 < angle_deg < 45:
        direction_label = "Lateral (Eastbound)"
        is_inward = False
    else:
        direction_label = "Lateral (Westbound)"
        is_inward = False

    return {
        "vx": round(vx, 3),
        "vy": round(vy, 3),
        "speed": round(speed, 3),
        "heading_deg": round(angle_deg, 1),
        "direction_label": direction_label,
        "is_inward_movement": is_inward
    }
