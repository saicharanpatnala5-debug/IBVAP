"""
IBVAP - Temporal State Machine for Incidents
Tracks incident states: Initiation -> Active Threat -> Containment -> Resolved.
"""
class TemporalIncidentStateMachine:
    def evaluate_stage(self, dwell_seconds: float, has_breach: bool) -> str:
        if has_breach and dwell_seconds > 20:
            return "ACTIVE_HIGH_THREAT"
        elif has_breach:
            return "PERIMETER_BREACHED"
        elif dwell_seconds > 15:
            return "PROLONGED_LOITERING"
        else:
            return "MONITORING"

temporal_engine = TemporalIncidentStateMachine()
