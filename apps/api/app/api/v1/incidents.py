"""
Incident management API (PRD section 25).

Every route here is gated by `require_admin`: this is operational data with
no legitimate public read, unlike the lost-found/missing-person case flow
which needs a narrow public status check. `status` is never accepted as a
free-form body field - the only way to move it is POST /{id}/transition,
which runs through app/services/incident_workflow.py's guarded transition
table.

NOTE ON MOUNTING: this router is not yet referenced by app/main.py, which is
owned by another workstream during this parallel build (see the final
report for the exact `app.include_router(...)` line to add there). Until
that line lands, tests/test_incidents.py mounts this router onto the shared
FastAPI `app` object itself so this feature is independently testable - see
that file's module-level comment.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.v1.helpers import LimitQuery, OffsetQuery, apply_updates, count_of, live_rows
from app.core.deps import AdminUser, DbSession, require_admin
from app.models.incident import Incident, IncidentPriority, IncidentStatus
from app.schemas.common import ListEnvelope, build_envelope
from app.schemas.incident import (
    IncidentCreate,
    IncidentOut,
    IncidentTransitionRequest,
    IncidentUpdate,
)
from app.services.audit import record_audit
from app.services.incident_workflow import (
    INCIDENT_TRANSITIONS,
    apply_transition,
    is_breached,
    sla_due_at_for,
)

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
    dependencies=[Depends(require_admin)],
    responses={
        401: {"description": "Missing, malformed or expired bearer token."},
        403: {"description": "Authenticated, but this role has no admin access."},
    },
)


def _get_or_404(db: Session, item_id: int) -> Incident:
    row = db.execute(live_rows(Incident).where(Incident.id == item_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return row


def _refresh_escalation(db: Session, incident: Incident, admin_id: int | None) -> None:
    """
    Recompute the SLA-breach flag on every touch.

    There is no live scheduler in this prototype to flip the flag the moment
    an SLA lapses, so it is recomputed whenever an incident is read or
    written instead. Escalation is monotonic - once true it stays true,
    because "this incident missed its SLA" remains a historical fact even
    after the incident is later resolved (see is_breached()'s docstring for
    why a resolved/closed incident can no longer newly escalate).
    """
    if incident.escalated:
        return
    if is_breached(incident.sla_due_at, incident.status):
        incident.escalated = True
        db.flush()
        record_audit(
            db,
            action="incident.escalated",
            entity_type="incident",
            entity_id=incident.id,
            actor_user_id=admin_id,
            detail={
                "priority": incident.priority,
                "status": incident.status,
                "sla_due_at": str(incident.sla_due_at),
            },
        )


@router.post(
    "",
    response_model=IncidentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Record a new incident",
    description=(
        "**Demo prototype.** Creates a record in this project's own database "
        "only - nothing is dispatched and no police/medical/fire/government "
        "system is notified. Starts at status='reported'; `sla_due_at` is "
        "stamped immediately from `priority` per PRD Table 3's response-time "
        "budget."
    ),
)
def create_incident(payload: IncidentCreate, db: DbSession, admin: AdminUser) -> Any:
    incident = Incident(
        category=payload.category.value,
        priority=payload.priority.value,
        status=IncidentStatus.REPORTED.value,
        title=payload.title,
        description=payload.description,
        zone_id=payload.zone_id,
        assigned_department=payload.assigned_department,
        reported_by_user_id=payload.reported_by_user_id,
        sla_due_at=sla_due_at_for(payload.priority.value),
        simulated=True,
    )
    db.add(incident)
    db.flush()
    record_audit(
        db,
        action="incident.created",
        entity_type="incident",
        entity_id=incident.id,
        actor_user_id=admin.id,
        detail={
            "category": incident.category,
            "priority": incident.priority,
            "status": incident.status,
        },
    )
    db.commit()
    db.refresh(incident)
    return IncidentOut.model_validate(incident)


@router.get(
    "",
    response_model=ListEnvelope[IncidentOut],
    summary="List incidents (admin operational view, filterable)",
)
def list_incidents(
    db: DbSession,
    admin: AdminUser,
    status_filter: IncidentStatus | None = Query(
        default=None, alias="status", description="Filter by lifecycle status."
    ),
    priority: IncidentPriority | None = Query(default=None, description="Filter by priority."),
    zone_id: int | None = Query(default=None, description="Filter by zone."),
    limit: int = LimitQuery,
    offset: int = OffsetQuery,
) -> Any:
    stmt = live_rows(Incident)
    if status_filter is not None:
        stmt = stmt.where(Incident.status == status_filter.value)
    if priority is not None:
        stmt = stmt.where(Incident.priority == priority.value)
    if zone_id is not None:
        stmt = stmt.where(Incident.zone_id == zone_id)

    total = count_of(db, stmt)
    rows = (
        db.execute(stmt.order_by(Incident.created_at.desc()).limit(limit).offset(offset))
        .scalars()
        .all()
    )
    for row in rows:
        _refresh_escalation(db, row, admin.id)
    db.commit()
    return ListEnvelope[IncidentOut].model_validate(
        build_envelope(rows, [IncidentOut.model_validate(r) for r in rows], total)
    )


@router.get("/{item_id}", response_model=IncidentOut, summary="Get one incident")
def get_incident(item_id: int, db: DbSession, admin: AdminUser) -> Any:
    incident = _get_or_404(db, item_id)
    _refresh_escalation(db, incident, admin.id)
    db.commit()
    db.refresh(incident)
    return IncidentOut.model_validate(incident)


@router.patch(
    "/{item_id}",
    response_model=IncidentOut,
    summary="Update incident fields (not status - see POST .../transition)",
    responses={404: {"description": "No such incident."}},
)
def update_incident(item_id: int, payload: IncidentUpdate, db: DbSession, admin: AdminUser) -> Any:
    incident = _get_or_404(db, item_id)
    data = {
        key: (value.value if hasattr(value, "value") else value)
        for key, value in payload.model_dump(exclude_unset=True).items()
    }

    priority_changed = "priority" in data and data["priority"] != incident.priority
    changed = apply_updates(incident, data)

    # Re-baseline the SLA clock from now when the priority itself changes,
    # unless the incident is already past the point where an SLA means
    # anything - matches is_breached()'s "in flight only" rule.
    if priority_changed and incident.status not in (
        IncidentStatus.RESOLVED.value,
        IncidentStatus.CLOSED.value,
    ):
        incident.sla_due_at = sla_due_at_for(incident.priority)

    db.flush()
    record_audit(
        db,
        action="incident.updated",
        entity_type="incident",
        entity_id=incident.id,
        actor_user_id=admin.id,
        detail={"changed_fields": sorted(changed)},
    )
    db.commit()
    db.refresh(incident)
    return IncidentOut.model_validate(incident)


@router.post(
    "/{item_id}/transition",
    response_model=IncidentOut,
    summary="Move an incident through its lifecycle",
    description=(
        "reported -> classified -> assigned -> in_response -> resolved -> "
        "closed. Any other move is rejected with **409**; status is never "
        "written as a free-form value."
    ),
    responses={
        404: {"description": "No such incident."},
        409: {"description": "Invalid status transition."},
    },
)
def transition_incident(
    item_id: int, payload: IncidentTransitionRequest, db: DbSession, admin: AdminUser
) -> Any:
    incident = _get_or_404(db, item_id)
    previous = incident.status
    incident.status = apply_transition(
        INCIDENT_TRANSITIONS, "incident", previous, payload.status.value
    )
    if incident.status == IncidentStatus.RESOLVED.value and incident.resolved_at is None:
        incident.resolved_at = datetime.now(timezone.utc)
    db.flush()
    record_audit(
        db,
        action="incident.status_changed",
        entity_type="incident",
        entity_id=incident.id,
        actor_user_id=admin.id,
        detail={"status_from": previous, "status_to": incident.status},
    )
    _refresh_escalation(db, incident, admin.id)
    db.commit()
    db.refresh(incident)
    return IncidentOut.model_validate(incident)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Retire an incident record (soft delete)",
    responses={404: {"description": "No such incident."}},
)
def delete_incident(item_id: int, db: DbSession, admin: AdminUser) -> Response:
    incident = _get_or_404(db, item_id)
    incident.deleted_at = datetime.now(timezone.utc)
    db.flush()
    record_audit(
        db,
        action="incident.deleted",
        entity_type="incident",
        entity_id=incident.id,
        actor_user_id=admin.id,
        detail={"soft_delete": True},
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
