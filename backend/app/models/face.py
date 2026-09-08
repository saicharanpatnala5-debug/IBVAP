"""
IBVAP - Face Intelligence Model
Exposes FaceSighting, Watchlist, and FaceBiometrics entities for facial identification.
"""
from app.models.face_watchlist import Watchlist, FaceSighting

# Aliases for architectural tree conformity
Face = FaceSighting
FaceWatchlist = Watchlist

__all__ = ["Face", "FaceSighting", "Watchlist", "FaceWatchlist"]
