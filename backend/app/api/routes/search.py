"""
IBVAP - Video Intelligence Search Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.search import VideoIntelligenceSearchQuery, VideoIntelligenceSearchResponse
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Video Intelligence Search"])

@router.post("", response_model=VideoIntelligenceSearchResponse)
async def search_video_intelligence(query: VideoIntelligenceSearchQuery, db: AsyncSession = Depends(get_db)):
    """
    Search structured video metadata instead of manual video playback.
    Directly addresses Section 14 and Section 16 of the PRD.
    """
    return await search_service.search(db, query)
