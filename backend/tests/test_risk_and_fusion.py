"""
Unit Tests: Risk Scoring and Event Fusion
"""
import pytest
from app.ai.risk_engine import risk_engine
from app.ai.event_fusion import event_fusion_engine
from app.ai.geometry import is_point_in_polygon

def test_ray_casting_polygon():
    polygon = [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
    assert is_point_in_polygon([5.0, 5.0], polygon) is True
    assert is_point_in_polygon([15.0, 5.0], polygon) is False

def test_explainable_risk_scoring():
    # Evaluate critical intrusion scenario
    eval_res = risk_engine.evaluate_risk(
        is_zone_intrusion=True,   # +30
        is_night_time=True,       # +15
        is_loitering=True,        # +15
        is_inward_movement=True,  # +20
        is_unknown_vehicle=True   # +20
    )
    assert eval_res["risk_score"] == 100
    assert eval_res["severity"] == "HIGH"
    assert len(eval_res["contributing_factors"]) == 5

    # With multiple objects (+10 -> 110)
    critical_eval = risk_engine.evaluate_risk(
        is_zone_intrusion=True,
        is_night_time=True,
        is_loitering=True,
        is_inward_movement=True,
        is_unknown_vehicle=True,
        has_multiple_objects=True,
        additional_factors=[{"name": "Boundary Proximity", "points": 15}]
    )
    assert critical_eval["risk_score"] >= 120
    assert critical_eval["severity"] == "CRITICAL"

def test_event_fusion():
    events = [
        {"event_type": "ANPR_DETECTION", "risk_delta": 20},
        {"event_type": "ZONE_INTRUSION", "risk_delta": 30},
        {"event_type": "LOITERING", "risk_delta": 15}
    ]
    fused = event_fusion_engine.fuse_events_into_incident("CAM-01", events)
    assert "Intrusion" in fused["title"]
    assert fused["risk_score"] == 65
    assert len(fused["timeline"]) == 3
