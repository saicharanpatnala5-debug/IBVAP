"""
IBVAP - Face Watchlist Manager
Manages authorized border security personnel and blacklisted suspect profiles.
"""
from typing import Dict, Any, Optional
import numpy as np
from ai.face.embeddings import embedding_extractor

class FaceWatchlistManager:
    def __init__(self):
        self.authorized_personnel: Dict[str, Dict[str, Any]] = {
            "OFFICER-701": {
                "name": "Capt. Arjun Verma",
                "unit": "SSB Sector B Command",
                "embedding": embedding_extractor.extract_embedding(None)
            }
        }
        self.blacklist_suspects: Dict[str, Dict[str, Any]] = {
            "SUSPECT-902": {
                "name": "Unidentified Infiltrator Profile #902",
                "priority": "CRITICAL",
                "embedding": embedding_extractor.extract_embedding(None)
            }
        }

    def get_authorized_embeddings(self) -> Dict[str, np.ndarray]:
        return {k: v["embedding"] for k, v in self.authorized_personnel.items()}

face_watchlist_manager = FaceWatchlistManager()
