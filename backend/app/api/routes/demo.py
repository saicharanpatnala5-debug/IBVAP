"""
IBVAP - SIH Demonstration API Routes
Allows judges and operators to trigger the end-to-end demo story or step through it.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.demo.sih_scenario import demo_scenario_engine

router = APIRouter(prefix="/demo", tags=["SIH Live Demonstration"])

@router.post("/run-scenario")
async def run_full_demo_scenario(db: AsyncSession = Depends(get_db)):
    """
    Executes all 8 steps of the SIH pitch demonstration in sequence.
    Generates genuine database records, AI risk cards, and WebSocket broadcasts.
    """
    results = await demo_scenario_engine.run_full_scenario(db)
    return {
        "status": "SUCCESS",
        "message": "Complete SIH 2026 8-step demonstration executed successfully.",
        "steps_count": len(results),
        "scenario_results": results
    }

@router.post("/step/{step_number}")
async def execute_demo_step(step_number: int, db: AsyncSession = Depends(get_db)):
    """Execute an individual step (1 through 8) during live presentation."""
    if step_number < 1 or step_number > 8:
        return {"error": "Step number must be between 1 and 8"}
    res = await demo_scenario_engine.execute_step(db, step_number)
    return res

@router.get("/status")
async def get_demo_status():
    return {
        "current_step": demo_scenario_engine.current_step,
        "total_steps": demo_scenario_engine.total_steps,
        "active_incident_id": demo_scenario_engine.active_incident_id,
        "history_count": len(demo_scenario_engine.history)
    }

@router.post("/reset")
async def reset_demo():
    demo_scenario_engine.current_step = 0
    demo_scenario_engine.history = []
    demo_scenario_engine.active_incident_id = None
    return {"status": "SUCCESS", "message": "Demo state reset to baseline"}
