"""
IBVAP - Alert Dispatch & Operator Acknowledgement Routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.alert import AlertResponse, AlertAcknowledgeRequest, AlertEscalateRequest
from app.services.alert_service import alert_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
async def get_alerts(limit: int = 50, db: AsyncSession = Depends(get_db)):
    return await alert_service.get_active_alerts(db, limit=limit)

@router.post("/{alert_id}/ack", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: str,
    ack_data: AlertAcknowledgeRequest = None,
    db: AsyncSession = Depends(get_db)
):
    notes = ack_data.notes if ack_data else "Acknowledged by Operator"
    alert = await alert_service.acknowledge_alert(
        db,
        alert_id=alert_id,
        acknowledged_by="CCTV_Operator_SectorB",
        notes=notes
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Log to audit trail (DPDP Act compliance)
    await audit_service.log_action(
        db=db,
        actor="CCTV_Operator_SectorB",
        action="ALERT_ACKNOWLEDGED",
        object_type="alert",
        object_id=alert_id,
        details={"notes": notes, "severity": alert.severity}
    )
    return alert
