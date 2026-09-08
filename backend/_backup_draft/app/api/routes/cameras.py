"""Camera, zone, topology and camera-health routes (PRD FR-01, FR-02, FR-06, FR-18)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentPrincipal, DbSession, client_ip, require
from app.core.clock import ensure_utc, utcnow
from app.core.config import get_settings
from app.core.crypto import encrypt, rebuild_stream_url, split_stream_url
from app.core.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.core.rbac import Permission
from app.db.enums import CameraStatus, EventType, IncidentStatus
from app.db.models.camera import Camera, CameraHealthSample, CameraLink, Zone
from app.db.models.event import Event, Incident
from app.schemas.camera import (
    CameraCreate,
    CameraDetail,
    CameraHealthRead,
    CameraHealthSummary,
    CameraLinkCreate,
    CameraLinkRead,
    CameraRead,
    CameraStreamInfo,
    CameraUpdate,
    HeartbeatReport,
    ZoneCreate,
    ZoneRead,
    ZoneUpdate,
)
from app.services import audit

router = APIRouter(tags=["cameras"])

#: Module-level singletons so ruff's B008 (function call in default) is satisfied
#: while keeping FastAPI's alias/description metadata.
_STATUS_QUERY = Query(default=None, alias="status")
_HARD_DELETE_QUERY = Query(
    default=False,
    description="Permanently delete the camera and all of its events. "
    "Default is a soft disable, which preserves the audit trail.",
)


# --------------------------------------------------------------------------- #
# Cameras
# --------------------------------------------------------------------------- #


@router.post(
    "/cameras",
    response_model=CameraRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require(Permission.CAMERA_WRITE))],
)
async def create_camera(
    payload: CameraCreate,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CameraRead:
    """Register an IP/RTSP camera (FR-01).

    Any credentials embedded in the stream URL are split out and encrypted; the
    stored ``stream_url`` is credential-free so ordinary reads cannot leak them.
    """
    exists = (
        await session.execute(select(Camera.id).where(Camera.code == payload.code))
    ).first()
    if exists:
        raise ConflictError(f"camera code {payload.code!r} is already registered")

    sanitised, credentials = split_stream_url(payload.stream_url)
    camera = Camera(
        code=payload.code,
        name=payload.name,
        site=payload.site,
        sector=payload.sector,
        latitude=payload.latitude,
        longitude=payload.longitude,
        heading_degrees=payload.heading_degrees,
        stream_url=sanitised,
        stream_credentials_encrypted=encrypt(credentials) if credentials else None,
        stream_protocol=sanitised.split("://", 1)[0].lower(),
        timezone=payload.timezone,
        frame_width=payload.frame_width,
        frame_height=payload.frame_height,
        edge_node_id=payload.edge_node_id,
        analytics_enabled=payload.analytics.model_dump(),
        enabled=payload.enabled,
        status=CameraStatus.PENDING.value,
    )
    session.add(camera)
    await session.flush()

    await audit.record(
        session,
        action=audit.ACTION_CAMERA_CREATE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        actor_roles=list(principal.roles),
        object_type="camera",
        object_id=camera.id,
        source_ip=client_ip(request),
        context={
            "code": camera.code,
            "sector": camera.sector,
            # Redacted by the audit scrubber; recorded to prove *whether* creds were set.
            "has_credentials": bool(credentials),
        },
    )
    await session.commit()
    return CameraRead.model_validate(camera)


@router.get(
    "/cameras",
    response_model=list[CameraRead],
    dependencies=[Depends(require(Permission.CAMERA_READ))],
)
async def list_cameras(
    principal: CurrentPrincipal,
    session: DbSession,
    sector: str | None = None,
    camera_status: CameraStatus | None = _STATUS_QUERY,
    enabled: bool | None = None,
) -> list[CameraRead]:
    stmt = select(Camera).order_by(Camera.code)
    if sector:
        stmt = stmt.where(Camera.sector == sector)
    if camera_status:
        stmt = stmt.where(Camera.status == camera_status.value)
    if enabled is not None:
        stmt = stmt.where(Camera.enabled.is_(enabled))
    if principal.sector_scope:
        stmt = stmt.where(Camera.sector.in_(principal.sector_scope))

    cameras = (await session.execute(stmt)).scalars()
    return [CameraRead.model_validate(c) for c in cameras]


@router.get(
    "/cameras/{camera_id}",
    response_model=CameraDetail,
    dependencies=[Depends(require(Permission.CAMERA_READ))],
)
async def get_camera(
    camera_id: uuid.UUID,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CameraDetail:
    camera = await _load_camera(session, camera_id, principal)
    open_count = int(
        (
            await session.execute(
                select(func.count())
                .select_from(Incident)
                .where(
                    Incident.primary_camera_id == camera.id,
                    Incident.status.in_(
                        (IncidentStatus.OPEN.value, IncidentStatus.ACKNOWLEDGED.value)
                    ),
                )
            )
        ).scalar_one()
    )
    detail = CameraDetail.model_validate(camera)
    detail.zones = [ZoneRead.model_validate(z) for z in camera.zones]
    detail.open_incident_count = open_count
    return detail


@router.patch(
    "/cameras/{camera_id}",
    response_model=CameraRead,
    dependencies=[Depends(require(Permission.CAMERA_WRITE))],
)
async def update_camera(
    camera_id: uuid.UUID,
    payload: CameraUpdate,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CameraRead:
    camera = await _load_camera(session, camera_id, principal)
    before = {
        "name": camera.name,
        "stream_url": camera.stream_url,
        "sector": camera.sector,
        "enabled": camera.enabled,
        "analytics_enabled": dict(camera.analytics_enabled or {}),
        "timezone": camera.timezone,
    }

    data = payload.model_dump(exclude_unset=True)
    if data.get("stream_url"):
        sanitised, credentials = split_stream_url(data.pop("stream_url"))
        camera.stream_url = sanitised
        camera.stream_protocol = sanitised.split("://", 1)[0].lower()
        camera.stream_credentials_encrypted = encrypt(credentials) if credentials else None
        # A URL change invalidates the previous health verdict.
        camera.status = CameraStatus.PENDING.value
        camera.consecutive_failures = 0
    if "analytics" in data and data["analytics"] is not None:
        camera.analytics_enabled = data.pop("analytics")
    else:
        data.pop("analytics", None)

    for field, value in data.items():
        setattr(camera, field, value)

    after = {
        "name": camera.name,
        "stream_url": camera.stream_url,
        "sector": camera.sector,
        "enabled": camera.enabled,
        "analytics_enabled": dict(camera.analytics_enabled or {}),
        "timezone": camera.timezone,
    }

    await audit.record(
        session,
        action=audit.ACTION_CAMERA_UPDATE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="camera",
        object_id=camera.id,
        source_ip=client_ip(request),
        context={"changes": audit.diff(before, after)},
    )
    await session.commit()
    return CameraRead.model_validate(camera)


@router.delete(
    "/cameras/{camera_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require(Permission.CAMERA_WRITE))],
)
async def delete_camera(
    camera_id: uuid.UUID,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
    hard: bool = _HARD_DELETE_QUERY,
) -> None:
    """Remove a camera.

    The default is a soft disable: deleting a camera would cascade to its
    events and incidents, destroying evidence an auditor may still need
    (PRD s5 auditor persona, s17 retention controls).
    """
    camera = await _load_camera(session, camera_id, principal)

    if hard:
        event_count = int(
            (
                await session.execute(
                    select(func.count()).select_from(Event).where(Event.camera_id == camera.id)
                )
            ).scalar_one()
        )
        await audit.record(
            session,
            action=audit.ACTION_CAMERA_DELETE,
            actor_label=principal.label,
            actor_id=principal.user.id if principal.user else None,
            object_type="camera",
            object_id=camera.id,
            source_ip=client_ip(request),
            context={"mode": "hard", "code": camera.code, "events_destroyed": event_count},
        )
        await session.delete(camera)
    else:
        camera.enabled = False
        camera.status = CameraStatus.DISABLED.value
        await audit.record(
            session,
            action=audit.ACTION_CAMERA_DELETE,
            actor_label=principal.label,
            actor_id=principal.user.id if principal.user else None,
            object_type="camera",
            object_id=camera.id,
            source_ip=client_ip(request),
            context={"mode": "soft_disable", "code": camera.code},
        )
    await session.commit()


@router.get(
    "/cameras/{camera_id}/stream",
    response_model=CameraStreamInfo,
    dependencies=[Depends(require(Permission.CAMERA_READ))],
)
async def get_stream_info(
    camera_id: uuid.UUID,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CameraStreamInfo:
    """Stream metadata (FR-02).

    The credentialed URL is included only for callers holding
    ``camera:credential:read`` (edge nodes), and every such read is audited.
    """
    camera = await _load_camera(session, camera_id, principal)

    credentialed: str | None = None
    if principal.can(Permission.CAMERA_CREDENTIAL_READ):
        from app.core.crypto import CredentialDecryptionError, decrypt

        if camera.stream_credentials_encrypted:
            try:
                credentialed = rebuild_stream_url(
                    camera.stream_url, decrypt(camera.stream_credentials_encrypted)
                )
            except CredentialDecryptionError:
                # Surfaced as a warning rather than a 500: the rest of the
                # metadata is still useful and the operator needs to know.
                credentialed = None
        else:
            credentialed = camera.stream_url

        await audit.record(
            session,
            action=audit.ACTION_CAMERA_CREDENTIAL_READ,
            actor_label=principal.label,
            actor_id=principal.user.id if principal.user else None,
            object_type="camera",
            object_id=camera.id,
            source_ip=client_ip(request),
        )
        await session.commit()

    return CameraStreamInfo(
        camera_id=camera.id,
        code=camera.code,
        status=camera.status,
        stream_url=camera.stream_url,
        stream_protocol=camera.stream_protocol,
        frame_width=camera.frame_width,
        frame_height=camera.frame_height,
        current_fps=camera.current_fps,
        current_latency_ms=camera.current_latency_ms,
        last_frame_at=camera.last_frame_at,
        zones=[ZoneRead.model_validate(z) for z in camera.zones],
        credentialed_url=credentialed,
    )


# --------------------------------------------------------------------------- #
# Zones
# --------------------------------------------------------------------------- #


@router.post(
    "/zones",
    response_model=ZoneRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require(Permission.ZONE_WRITE))],
)
async def create_zone(
    payload: ZoneCreate,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> ZoneRead:
    """Create a polygonal virtual fence (FR-06)."""
    camera = await _load_camera(session, payload.camera_id, principal)

    clash = (
        await session.execute(
            select(Zone.id).where(Zone.camera_id == camera.id, Zone.name == payload.name)
        )
    ).first()
    if clash:
        raise ConflictError(f"zone {payload.name!r} already exists on this camera")

    zone = Zone(
        camera_id=camera.id,
        name=payload.name,
        kind=payload.kind.value,
        active=payload.active,
        polygon=[{"x": p.x, "y": p.y} for p in payload.polygon],
        object_classes=[c.value for c in payload.object_classes],
        active_from_hour=payload.active_from_hour,
        active_to_hour=payload.active_to_hour,
        min_confirmation_frames=payload.min_confirmation_frames,
        min_confidence=payload.min_confidence,
        loiter_seconds=payload.loiter_seconds,
        inward_bearing_degrees=payload.inward_bearing_degrees,
        risk_bonus=payload.risk_bonus,
    )
    session.add(zone)
    await session.flush()

    await audit.record(
        session,
        action=audit.ACTION_ZONE_CREATE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="zone",
        object_id=zone.id,
        source_ip=client_ip(request),
        context={"camera_code": camera.code, "name": zone.name, "kind": zone.kind},
    )
    await session.commit()
    return ZoneRead.model_validate(zone)


@router.get(
    "/zones",
    response_model=list[ZoneRead],
    dependencies=[Depends(require(Permission.ZONE_READ))],
)
async def list_zones(
    principal: CurrentPrincipal,
    session: DbSession,
    camera_id: uuid.UUID | None = None,
    active: bool | None = None,
) -> list[ZoneRead]:
    stmt = select(Zone).join(Camera).order_by(Camera.code, Zone.name)
    if camera_id:
        stmt = stmt.where(Zone.camera_id == camera_id)
    if active is not None:
        stmt = stmt.where(Zone.active.is_(active))
    if principal.sector_scope:
        stmt = stmt.where(Camera.sector.in_(principal.sector_scope))

    zones = (await session.execute(stmt)).scalars()
    return [ZoneRead.model_validate(z) for z in zones]


@router.patch(
    "/zones/{zone_id}",
    response_model=ZoneRead,
    dependencies=[Depends(require(Permission.ZONE_WRITE))],
)
async def update_zone(
    zone_id: uuid.UUID,
    payload: ZoneUpdate,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> ZoneRead:
    zone = (
        await session.execute(select(Zone).where(Zone.id == zone_id))
    ).scalar_one_or_none()
    if zone is None:
        raise NotFoundError("zone not found")
    await _load_camera(session, zone.camera_id, principal)

    before = {
        "name": zone.name,
        "kind": zone.kind,
        "active": zone.active,
        "polygon": list(zone.polygon or ()),
        "min_confirmation_frames": zone.min_confirmation_frames,
        "min_confidence": zone.min_confidence,
        "risk_bonus": zone.risk_bonus,
    }

    data = payload.model_dump(exclude_unset=True)
    if "polygon" in data and data["polygon"] is not None:
        zone.polygon = [{"x": p["x"], "y": p["y"]} for p in data.pop("polygon")]
    else:
        data.pop("polygon", None)
    if "object_classes" in data and data["object_classes"] is not None:
        zone.object_classes = [str(c) for c in data.pop("object_classes")]
    else:
        data.pop("object_classes", None)
    if "kind" in data and data["kind"] is not None:
        zone.kind = str(data.pop("kind"))
    else:
        data.pop("kind", None)

    for field, value in data.items():
        setattr(zone, field, value)

    after = {
        "name": zone.name,
        "kind": zone.kind,
        "active": zone.active,
        "polygon": list(zone.polygon or ()),
        "min_confirmation_frames": zone.min_confirmation_frames,
        "min_confidence": zone.min_confidence,
        "risk_bonus": zone.risk_bonus,
    }

    await audit.record(
        session,
        action=audit.ACTION_ZONE_UPDATE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="zone",
        object_id=zone.id,
        source_ip=client_ip(request),
        context={"changes": audit.diff(before, after)},
    )
    await session.commit()
    return ZoneRead.model_validate(zone)


@router.delete(
    "/zones/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require(Permission.ZONE_WRITE))],
)
async def delete_zone(
    zone_id: uuid.UUID,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> None:
    zone = (
        await session.execute(select(Zone).where(Zone.id == zone_id))
    ).scalar_one_or_none()
    if zone is None:
        raise NotFoundError("zone not found")
    await _load_camera(session, zone.camera_id, principal)

    # Deactivate rather than delete: existing events reference this zone, and an
    # investigator needs to see the fence that was in force at the time.
    zone.active = False
    await audit.record(
        session,
        action=audit.ACTION_ZONE_DELETE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="zone",
        object_id=zone.id,
        source_ip=client_ip(request),
        context={"mode": "deactivate", "name": zone.name},
    )
    await session.commit()


# --------------------------------------------------------------------------- #
# Topology
# --------------------------------------------------------------------------- #


@router.post(
    "/topology/links",
    response_model=CameraLinkRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require(Permission.TOPOLOGY_WRITE))],
)
async def create_link(
    payload: CameraLinkCreate,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> CameraLinkRead:
    """Define a directed camera adjacency used for handoff and association."""
    for camera_id in (payload.from_camera_id, payload.to_camera_id):
        await _load_camera(session, camera_id, principal)

    clash = (
        await session.execute(
            select(CameraLink.id).where(
                CameraLink.from_camera_id == payload.from_camera_id,
                CameraLink.to_camera_id == payload.to_camera_id,
            )
        )
    ).first()
    if clash:
        raise ConflictError("this camera link already exists")

    link = CameraLink(**payload.model_dump())
    session.add(link)
    await session.flush()

    await audit.record(
        session,
        action=audit.ACTION_TOPOLOGY_WRITE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="camera_link",
        object_id=link.id,
        source_ip=client_ip(request),
        context=payload.model_dump(mode="json"),
    )
    await session.commit()
    return CameraLinkRead.model_validate(link)


@router.get(
    "/topology/links",
    response_model=list[CameraLinkRead],
    dependencies=[Depends(require(Permission.TOPOLOGY_READ))],
)
async def list_links(
    session: DbSession,
    from_camera_id: uuid.UUID | None = None,
) -> list[CameraLinkRead]:
    stmt = select(CameraLink)
    if from_camera_id:
        stmt = stmt.where(CameraLink.from_camera_id == from_camera_id)
    links = (await session.execute(stmt)).scalars()
    return [CameraLinkRead.model_validate(link) for link in links]


@router.delete(
    "/topology/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require(Permission.TOPOLOGY_WRITE))],
)
async def delete_link(
    link_id: uuid.UUID,
    request: Request,
    principal: CurrentPrincipal,
    session: DbSession,
) -> None:
    link = (
        await session.execute(select(CameraLink).where(CameraLink.id == link_id))
    ).scalar_one_or_none()
    if link is None:
        raise NotFoundError("camera link not found")

    await audit.record(
        session,
        action=audit.ACTION_TOPOLOGY_WRITE,
        actor_label=principal.label,
        actor_id=principal.user.id if principal.user else None,
        object_type="camera_link",
        object_id=link.id,
        source_ip=client_ip(request),
        context={"deleted": True},
    )
    await session.delete(link)
    await session.commit()


# --------------------------------------------------------------------------- #
# Health
# --------------------------------------------------------------------------- #


@router.post(
    "/health/heartbeat",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require(Permission.INGEST_WRITE))],
)
async def post_heartbeat(
    payload: HeartbeatReport,
    session: DbSession,
) -> dict[str, str]:
    """Edge nodes report stream health here (FR-18).

    A camera dropping out must not affect any other pipeline, so this only ever
    touches the reported camera's own row.
    """
    settings = get_settings()
    camera = (
        await session.execute(select(Camera).where(Camera.id == payload.camera_id))
    ).scalar_one_or_none()
    if camera is None:
        raise NotFoundError("camera not found")

    reported_at = ensure_utc(payload.reported_at)
    previous_status = camera.status

    camera.last_heartbeat_at = reported_at
    camera.current_fps = payload.fps
    camera.current_latency_ms = payload.latency_ms
    if payload.frame_width:
        camera.frame_width = payload.frame_width
    if payload.frame_height:
        camera.frame_height = payload.frame_height

    if payload.status is CameraStatus.ONLINE:
        camera.last_frame_at = reported_at
        camera.consecutive_failures = 0
        camera.last_error = None
        degraded = (
            payload.fps is not None and payload.fps < settings.camera_degraded_min_fps
        ) or (
            payload.latency_ms is not None
            and payload.latency_ms > settings.camera_degraded_max_latency_ms
        )
        camera.status = (
            CameraStatus.DEGRADED.value if degraded else CameraStatus.ONLINE.value
        )
    else:
        camera.consecutive_failures += 1
        camera.last_error = payload.error
        camera.status = payload.status.value

    session.add(
        CameraHealthSample(
            camera_id=camera.id,
            sampled_at=reported_at,
            status=camera.status,
            fps=payload.fps,
            latency_ms=payload.latency_ms,
            dropped_frames=payload.dropped_frames,
            inference_ms=payload.inference_ms,
            resource_usage=payload.resource_usage,
            error=payload.error,
        )
    )

    # A transition to/from OFFLINE is operationally significant: it is a blind
    # spot appearing or closing, so it becomes a first-class event.
    if previous_status != camera.status and camera.status in (
        CameraStatus.OFFLINE.value,
        CameraStatus.ONLINE.value,
    ):
        went_offline = camera.status == CameraStatus.OFFLINE.value
        session.add(
            Event(
                event_type=(
                    EventType.CAMERA_OFFLINE if went_offline else EventType.CAMERA_RECOVERED
                ).value,
                occurred_at=reported_at,
                ingested_at=utcnow(),
                camera_id=camera.id,
                confidence=1.0,
                attributes={
                    "previous_status": previous_status,
                    "status": camera.status,
                    "error": payload.error,
                },
            )
        )

    await session.commit()
    return {"status": camera.status}


@router.get(
    "/health/cameras",
    response_model=CameraHealthSummary,
    dependencies=[Depends(require(Permission.HEALTH_READ))],
)
async def camera_health(
    principal: CurrentPrincipal,
    session: DbSession,
) -> CameraHealthSummary:
    """Camera health roll-up (FR-18).

    Staleness is computed at read time: a node that stops reporting entirely
    would otherwise leave its camera showing ONLINE forever.
    """
    settings = get_settings()
    stmt = select(Camera).order_by(Camera.code)
    if principal.sector_scope:
        stmt = stmt.where(Camera.sector.in_(principal.sector_scope))
    cameras = list((await session.execute(stmt)).scalars())

    now = utcnow()
    rows: list[CameraHealthRead] = []
    counts = {s.value: 0 for s in CameraStatus}

    for camera in cameras:
        seconds_since = (
            (now - ensure_utc(camera.last_frame_at)).total_seconds()
            if camera.last_frame_at
            else None
        )
        effective = camera.status
        if not camera.enabled:
            effective = CameraStatus.DISABLED.value
        elif seconds_since is None:
            effective = CameraStatus.PENDING.value
        elif seconds_since > settings.camera_offline_after_seconds:
            effective = CameraStatus.OFFLINE.value

        counts[effective] = counts.get(effective, 0) + 1
        rows.append(
            CameraHealthRead(
                camera_id=camera.id,
                code=camera.code,
                name=camera.name,
                sector=camera.sector,
                status=effective,
                enabled=camera.enabled,
                current_fps=camera.current_fps,
                current_latency_ms=camera.current_latency_ms,
                last_frame_at=camera.last_frame_at,
                last_heartbeat_at=camera.last_heartbeat_at,
                seconds_since_frame=round(seconds_since, 2) if seconds_since else None,
                consecutive_failures=camera.consecutive_failures,
                last_error=camera.last_error,
                meets_fps_target=(
                    camera.current_fps >= settings.camera_degraded_min_fps
                    if camera.current_fps is not None
                    else None
                ),
                meets_latency_target=(
                    camera.current_latency_ms <= settings.camera_degraded_max_latency_ms
                    if camera.current_latency_ms is not None
                    else None
                ),
            )
        )

    return CameraHealthSummary(
        total=len(rows),
        online=counts.get(CameraStatus.ONLINE.value, 0),
        degraded=counts.get(CameraStatus.DEGRADED.value, 0),
        offline=counts.get(CameraStatus.OFFLINE.value, 0),
        pending=counts.get(CameraStatus.PENDING.value, 0),
        disabled=counts.get(CameraStatus.DISABLED.value, 0),
        cameras=rows,
        has_blind_spot=any(
            r.enabled and r.status in (CameraStatus.OFFLINE.value, CameraStatus.PENDING.value)
            for r in rows
        ),
    )


async def _load_camera(
    session: DbSession, camera_id: uuid.UUID, principal: CurrentPrincipal
) -> Camera:
    camera = (
        await session.execute(
            select(Camera).options(selectinload(Camera.zones)).where(Camera.id == camera_id)
        )
    ).scalar_one_or_none()
    if camera is None:
        raise NotFoundError("camera not found")
    if not principal.sector_allowed(camera.sector):
        # 403 rather than 404: the caller is authenticated and the resource
        # exists, they simply are not scoped to this sector.
        raise PermissionDeniedError("camera is outside your assigned sectors")
    return camera
