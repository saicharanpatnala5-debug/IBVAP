"""
IBVAP - Face Recognition & Watchlist Verifier
ArcFace-compliant cosine matcher with Human-in-the-Loop review enforcement per Section 11.4.
"""
from typing import Dict, Any, Optional
import numpy as np

try:
    from ai.face.embeddings import embedding_extractor
except ImportError:
    from app.ai.face.embeddings import embedding_extractor

class FaceRecognizer:
    def __init__(self, similarity_threshold: float = 0.78):
        self.similarity_threshold = similarity_threshold

    def verify_against_watchlist(
        self,
        probe_embedding: np.ndarray,
        watchlist_embeddings: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Compares probe embedding against reference gallery.
        """
        best_match_id = None
        max_similarity = -1.0

        for identity_id, ref_emb in watchlist_embeddings.items():
            sim = embedding_extractor.compute_cosine_similarity(probe_embedding, ref_emb)
            if sim > max_similarity:
                max_similarity = sim
                best_match_id = identity_id

        is_match = max_similarity >= self.similarity_threshold
        return {
            "is_match": is_match,
            "matched_identity": best_match_id if is_match else None,
            "similarity_score": round(max_similarity, 4),
            "confidence_level": "HIGH" if max_similarity > 0.85 else "MODERATE" if is_match else "LOW",
            "review_required": True, # Mandatory Human-in-the-Loop requirement (DPDP Act 2023)
            "status": "AUTHORIZED MATCH" if is_match else "UNKNOWN PERSON / REVIEW REQUIRED"
        }

face_recognizer = FaceRecognizer()
