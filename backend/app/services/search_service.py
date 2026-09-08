"""
IBVAP - Video Intelligence Search Engine Service
Supports structured multi-parameter querying across past events, vehicle plates, incidents, and tracks.
Directly implements Section 14 & 16 of the PRD.
"""
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.models.incident import Incident
from app.models.event import Event
from app.models.vehicle_plate import VehiclePlate
from app.models.face_watchlist import FaceSighting
from app.schemas.search import VideoIntelligenceSearchQuery, VideoIntelligenceSearchResponse, SearchResultItem

class SearchService:
    async def search(self, db: AsyncSession, query: VideoIntelligenceSearchQuery) -> VideoIntelligenceSearchResponse:
        start_t = time.time()
        results: List[SearchResultItem] = []

        # 1. Search Incidents
        inc_query = select(Incident)
        if query.severity:
            inc_query = inc_query.where(Incident.severity == query.severity.upper())
        if query.camera_id:
            inc_query = inc_query.where(Incident.lead_camera_id == query.camera_id)
        if query.query_text:
            search_pattern = f"%{query.query_text}%"
            inc_query = inc_query.where(or_(Incident.title.ilike(search_pattern), Incident.incident_id.ilike(search_pattern)))

        inc_res = await db.execute(inc_query.limit(query.limit))
        for inc in inc_res.scalars().all():
            results.append(SearchResultItem(
                result_type="INCIDENT",
                id=inc.incident_id,
                camera_id=inc.lead_camera_id,
                sector="Sector-B",
                timestamp=inc.start_time,
                title=inc.title,
                description=f"Incident with Risk Score {inc.risk_score} ({inc.severity}). Status: {inc.status}.",
                confidence=0.95,
                metadata={"severity": inc.severity, "risk_score": inc.risk_score, "status": inc.status}
            ))

        # 2. Search Vehicle Plates (ANPR)
        plate_query = select(VehiclePlate)
        if query.plate_text:
            plate_query = plate_query.where(VehiclePlate.plate_text.ilike(f"%{query.plate_text}%"))
        if query.camera_id:
            plate_query = plate_query.where(VehiclePlate.camera_id == query.camera_id)

        plate_res = await db.execute(plate_query.limit(query.limit))
        for p in plate_res.scalars().all():
            results.append(SearchResultItem(
                result_type="VEHICLE",
                id=p.plate_id,
                camera_id=p.camera_id,
                sector="Sector-B",
                timestamp=p.first_seen,
                title=f"Vehicle Plate: {p.plate_text}",
                description=f"Class: {p.vehicle_class}, Direction: {p.direction or 'Unknown'}. Watchlist: {p.is_watchlist_match}.",
                confidence=p.ocr_confidence,
                evidence_url=p.evidence_frame_url,
                metadata={"plate": p.plate_text, "ocr_confidence": p.ocr_confidence, "watchlist_match": p.is_watchlist_match}
            ))

        # 3. Search Events
        ev_query = select(Event)
        if query.camera_id:
            ev_query = ev_query.where(Event.camera_id == query.camera_id)
        if query.object_class:
            ev_query = ev_query.where(Event.metadata_json["target_class"].as_string() == query.object_class)

        ev_res = await db.execute(ev_query.limit(query.limit))
        for ev in ev_res.scalars().all():
            results.append(SearchResultItem(
                result_type="EVENT",
                id=ev.event_id,
                camera_id=ev.camera_id,
                sector="Sector-B",
                timestamp=ev.timestamp,
                title=ev.event_type.replace("_", " ").title(),
                description=ev.metadata_json.get("description", f"Event registered on {ev.camera_id}"),
                confidence=ev.confidence,
                evidence_url=ev.evidence_frame_url,
                metadata=ev.metadata_json or {}
            ))

        elapsed_ms = (time.time() - start_t) * 1000.0
        return VideoIntelligenceSearchResponse(
            total_found=len(results),
            execution_time_ms=round(elapsed_ms, 2),
            results=results
        )

search_service = SearchService()
