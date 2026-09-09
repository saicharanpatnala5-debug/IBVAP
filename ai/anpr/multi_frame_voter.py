"""
IBVAP - Multi-Frame ANPR Voting Engine
Aggregates OCR readings across consecutive frames for the same vehicle track.
Produces high-confidence plate results through temporal consensus voting.
"""
from typing import Dict, Any, Optional, List
from collections import defaultdict
import time
import re


class MultiFrameVoter:
    """
    Collects plate readings across multiple frames for the same tracked vehicle.
    Uses weighted voting to determine the most likely plate string.
    """

    def __init__(self, window_size: int = 5, min_agreement: float = 0.6):
        self.window_size = window_size
        self.min_agreement = min_agreement
        # track_id -> list of (plate_text, confidence, timestamp)
        self._readings: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def add_reading(self, track_id: str, plate_text: str, confidence: float) -> None:
        """Add a single-frame OCR reading for a tracked vehicle."""
        if not plate_text or plate_text == "UNKNOWN":
            return

        clean = re.sub(r"[^A-Za-z0-9]", "", plate_text).upper()
        if len(clean) < 4:
            return

        readings = self._readings[track_id]
        readings.append({
            "plate_text": clean,
            "confidence": confidence,
            "timestamp": time.time(),
        })

        # Keep only the last N readings
        if len(readings) > self.window_size * 2:
            self._readings[track_id] = readings[-self.window_size:]

    def get_consensus(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns the consensus plate reading for a track, or None if insufficient data.
        Uses confidence-weighted voting across the reading window.
        """
        readings = self._readings.get(track_id, [])
        if not readings:
            return None

        recent = readings[-self.window_size:]
        if len(recent) < 2:
            # Single reading — return with low confidence flag
            r = recent[0]
            return {
                "plate_text": r["plate_text"],
                "confidence": r["confidence"] * 0.7,  # Penalize single-frame
                "readings_count": 1,
                "agreement_ratio": 1.0,
                "is_consensus": False,
                "method": "single_frame",
            }

        # Weighted vote counting
        vote_weights: Dict[str, float] = defaultdict(float)
        vote_counts: Dict[str, int] = defaultdict(int)

        for r in recent:
            vote_weights[r["plate_text"]] += r["confidence"]
            vote_counts[r["plate_text"]] += 1

        # Find winner
        best_plate = max(vote_weights, key=vote_weights.get)
        best_count = vote_counts[best_plate]
        agreement = best_count / len(recent)

        # Calculate consensus confidence
        avg_conf = vote_weights[best_plate] / best_count
        consensus_boost = min(agreement * 1.2, 1.0)
        final_confidence = avg_conf * consensus_boost

        is_consensus = agreement >= self.min_agreement and len(recent) >= 3

        return {
            "plate_text": best_plate,
            "confidence": round(final_confidence, 4),
            "readings_count": len(recent),
            "agreement_ratio": round(agreement, 3),
            "total_candidates": len(vote_counts),
            "is_consensus": is_consensus,
            "method": "multi_frame_vote",
        }

    def clear_track(self, track_id: str) -> None:
        """Clear readings for a track that has left the scene."""
        self._readings.pop(track_id, None)

    def get_active_tracks(self) -> List[str]:
        """Returns IDs of tracks with active readings."""
        return list(self._readings.keys())


multi_frame_voter = MultiFrameVoter()
