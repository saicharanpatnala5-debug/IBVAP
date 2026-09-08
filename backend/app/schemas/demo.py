"""
IBVAP - SIH 2026 Interactive Demo Simulation Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class DemoScenarioStep(BaseModel):
    step_number: int
    timestamp_offset_seconds: int
    phase_title: str
    description: str
    camera_id: str
    active_events: List[str]
    accumulated_risk_score: int
    severity: str
    explainable_factors: List[str]
    evidence_snapshot: str

class DemoScenarioTriggerRequest(BaseModel):
    sector: str = "Sector-B"
    auto_advance_seconds: Optional[float] = 2.0 # Simulate real-time steps automatically

class DemoScenarioStatus(BaseModel):
    is_running: bool
    current_step: int
    total_steps: int
    active_incident_id: Optional[str] = None
    last_action: str
    completed_steps: List[DemoScenarioStep] = []
