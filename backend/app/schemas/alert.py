"""
IBVAP - Alert Schemas with Explainable AI Cards
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

class ExplainabilityCard(BaseModel):
    what: str
    who: str
    where: str
    when: str
    why_factors: List[str]
    confidence_score: float
    evidence_frame: Optional[str] = None
    evidence_clip: Optional[str] = None
    risk_score: int
    severity: str

class AlertAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None

class AlertEscalateRequest(BaseModel):
    escalated_to: str
    reason: str

class AlertResponse(BaseModel):
    alert_id: str
    incident_id: str
    camera_id: str
    severity: str
    score: int
    title: str
    description: str
    explainability_card: Dict[str, Any]
    evidence_frame_url: Optional[str] = None
    evidence_clip_url: Optional[str] = None
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    is_escalated: bool
    escalated_to: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
