"""
IBVAP - Audit Log Schemas (DPDP Act 2023)
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class AuditLogCreate(BaseModel):
    actor: str
    action: str
    object_type: str
    object_id: Optional[str] = None
    result: str = "SUCCESS"
    details_json: Optional[Dict[str, Any]] = {}

class AuditLogResponse(BaseModel):
    log_id: str
    actor: str
    action: str
    object_type: str
    object_id: Optional[str] = None
    timestamp: datetime
    result: str
    source_ip: Optional[str] = None
    details_json: Optional[Dict[str, Any]] = {}

    model_config = ConfigDict(from_attributes=True)
