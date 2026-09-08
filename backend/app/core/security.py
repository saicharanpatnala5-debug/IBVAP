"""
IBVAP - Security, Authentication & Role-Based Access Control (RBAC)
PBKDF2/SHA256 password hashing with salt and PyJWT token generation.
"""
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
import jwt
from enum import Enum
from app.core.config import settings

class UserRole(str, Enum):
    ADMIN = "admin"                     # Full system and configuration management
    SUPERVISOR = "supervisor"           # Incident overview, escalation, live command
    CCTV_OPERATOR = "cctv_operator"     # Real-time monitoring, alert acknowledgement
    FIELD_RESPONSE = "field_response"   # Incident viewing, evidence review
    AUDITOR = "auditor"                 # Audit logs, compliance, DPDP Act review

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a unique salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored PBKDF2 hash."""
    try:
        salt, stored_hash = hashed_password.split("$")
        key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return secrets.compare_digest(key.hex(), stored_hash)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now,
        "nbf": now
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
