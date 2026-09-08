"""
IBVAP - Audit Model
Cryptographically tamper-evident audit logs conforming to Section 8 of DPDP Act 2023.
"""
from app.models.audit_log import AuditLog

# Alias for architectural tree conformity
Audit = AuditLog

__all__ = ["Audit", "AuditLog"]
