"""
Emergency directory and the simulated SOS endpoint (PRD section 15, D-02).

Nothing in this module contacts, notifies or queues work for any police,
medical, fire, CCTV or government dispatch system. The directory is seeded with
deliberately fake phone numbers and the SOS endpoint writes a row to our own
database and stops.
"""
from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.api.v1.helpers import LimitQuery, OffsetQuery, count_of, published_rows
from app.core.deps import DbSession
from app.core.notices import SOS_NOTICE
from app.models.emergency import EmergencyService, SosIncident
from app.models.enums import EmergencyCategory
from app.schemas.common import ListEnvelope, build_envelope
from app.schemas.emergency import EmergencyServiceOut, SosCreate, SosCreatedOut
from app.services.audit import record_audit
from app.services.references import allocate_case_reference

router = APIRouter(prefix="/emergency", tags=["emergency"])


@router.get(
    "/services",
    response_model=ListEnvelope[EmergencyServiceOut],
    summary="List seeded emergency help points",
    description=(
        "**Demo prototype directory.** Every seeded entry carries a "
        "deliberately fake `+91-00000-000NN` placeholder phone number. Real "
        "Indian emergency numbers and real station numbers are never seeded "
        "here, because a pilgrim must never tap-to-call a number this "
        "prototype implies is staffed. This endpoint is not connected to live "
        "emergency dispatch."
    ),
)
def list_emergency_services(
    db: DbSession,
    category: EmergencyCategory | None = Query(
        default=None, description="Filter by service category."
    ),
    limit: int = LimitQuery,
    offset: int = OffsetQuery,
) -> ListEnvelope[EmergencyServiceOut]:
    stmt = published_rows(EmergencyService)
    if category is not None:
        stmt = stmt.where(EmergencyService.category == category.value)

    total = count_of(db, stmt)
    rows = (
        db.execute(
            stmt.order_by(EmergencyService.id.asc()).limit(limit).offset(offset)
        )
        .scalars()
        .all()
    )
    # prototype_notice is a property on the model, so it serialises with every
    # row automatically - see EmergencyService.prototype_notice.
    items = [EmergencyServiceOut.model_validate(row) for row in rows]
    return ListEnvelope[EmergencyServiceOut].model_validate(
        build_envelope(rows, items, total)
    )


@router.post(
    "/sos",
    response_model=SosCreatedOut,
    status_code=status.HTTP_201_CREATED,
    summary="Record a SIMULATED SOS report",
    description=(
        "**This is a prototype endpoint. It dispatches nothing.** Calling it "
        "writes a row to this project's own test database and returns a "
        "reference. No police, ambulance, fire, medical, control-room or "
        "government system is contacted; no responder is notified; no alert "
        "is raised anywhere. The response always carries `\"simulated\": true`. "
        "In a real emergency, contact local emergency services directly.\n\n"
        "`consent_given` must be `true` (422 otherwise). Latitude and "
        "longitude are stored only when consent was given."
    ),
)
def create_sos(payload: SosCreate, db: DbSession) -> SosCreatedOut:
    reference = allocate_case_reference(db, SosIncident, "SOS")

    # Defence in depth: the schema already rejects consent_given=false, but the
    # persistence decision is made here too, so location can never be written
    # on the strength of a validator someone later relaxes.
    store_location = payload.consent_given is True

    incident = SosIncident(
        case_reference=reference,
        situation_category=payload.situation_category.value,
        note=payload.note,
        reporter_name=payload.reporter_name,
        reporter_phone=payload.reporter_phone,
        consent_given=payload.consent_given,
        latitude=payload.latitude if store_location else None,
        longitude=payload.longitude if store_location else None,
        status="recorded",
        simulated=True,
    )
    db.add(incident)
    db.flush()

    record_audit(
        db,
        action="sos.submitted",
        entity_type="sos_incident",
        entity_id=incident.id,
        actor_user_id=None,
        detail={
            "case_reference": reference,
            "situation_category": incident.situation_category,
            "consent_given": incident.consent_given,
            "location_stored": store_location
            and payload.latitude is not None
            and payload.longitude is not None,
            "simulated": True,
        },
    )
    db.commit()
    db.refresh(incident)

    return SosCreatedOut(
        case_reference=incident.case_reference,
        status=incident.status,
        simulated=True,
        created_at=incident.created_at,
        prototype_notice=SOS_NOTICE,
    )
