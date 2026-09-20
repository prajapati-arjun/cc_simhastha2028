"""
Public Missing Person API (PRD section 16, decision D-01, contract section 6).

The strictest privacy rules in this service live here.

  * Two public routes only: submit, and check status by opaque reference.
  * NO list endpoint. NO search by name, phone, age or location. Ever.
  * The read response is status and timestamps ONLY. It must never echo the
    person's name, age, gender, physical description, photo, last-seen
    location, coordinates, or any reporter detail.

At an event serving millions of pilgrims, an enumerable endpoint over
missing-person reports - most of them concerning children - would be a serious
privacy failure and would breach PRD section 31 (data minimisation, purpose
limitation). Full case detail exists, but only behind an authenticated admin
route where verification is the stated purpose.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DbSession
from app.core.notices import MISSING_PERSON_NOTICE
from app.models.cases import MissingPersonCase
from app.models.enums import MissingPersonStatus
from app.schemas.cases import (
    CaseCreatedOut,
    MissingPersonCreate,
    MissingPersonPublicOut,
)
from app.services.audit import record_audit
from app.services.references import allocate_case_reference

router = APIRouter(prefix="/missing-person", tags=["missing-person"])


@router.post(
    "",
    response_model=CaseCreatedOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a missing-person report",
    description=(
        "**Demo prototype.** The report is stored in this project's own test "
        "database for this pilot and is NOT automatically sent to police. No "
        "alert is raised, no control room is notified, and no facial "
        "recognition or CCTV system is involved. If a person is genuinely "
        "missing, contact local police directly.\n\n"
        "The returned `case_reference` is the ONLY way to check this report "
        "again. Validation: `person_name` required, `person_age` 0-120 if "
        "given, `reporter_phone` required, `last_seen_at` must not be in the "
        "future, `consent_given` must be true."
    ),
)
def create_missing_person(
    payload: MissingPersonCreate, db: DbSession
) -> CaseCreatedOut:
    reference = allocate_case_reference(db, MissingPersonCase, "MP")

    store_location = payload.consent_given is True

    case = MissingPersonCase(
        case_reference=reference,
        person_name=payload.person_name,
        person_age=payload.person_age,
        person_gender=payload.person_gender,
        physical_description=payload.physical_description,
        last_seen_location_text=payload.last_seen_location_text,
        latitude=payload.latitude if store_location else None,
        longitude=payload.longitude if store_location else None,
        last_seen_at=payload.last_seen_at,
        photo_url=payload.photo_url,
        reporter_name=payload.reporter_name,
        reporter_phone=payload.reporter_phone,
        reporter_relationship=payload.reporter_relationship,
        consent_given=payload.consent_given,
        status=MissingPersonStatus.SUBMITTED.value,
    )
    db.add(case)
    db.flush()

    # The audit detail records that a case was filed and its status - never the
    # child's name, description or photo. record_audit() redacts defensively.
    record_audit(
        db,
        action="missing_person.submitted",
        entity_type="missing_person_case",
        entity_id=case.id,
        actor_user_id=None,
        detail={
            "case_reference": reference,
            "status": case.status,
            "consent_given": case.consent_given,
            "has_photo": case.photo_url is not None,
        },
    )
    db.commit()
    db.refresh(case)

    return CaseCreatedOut(
        case_reference=case.case_reference,
        status=case.status,
        created_at=case.created_at,
        prototype_notice=MISSING_PERSON_NOTICE,
    )


@router.get(
    "/{case_reference}",
    response_model=MissingPersonPublicOut,
    summary="Check the status of a missing-person report by case reference",
    description=(
        "Returns **case status and timestamps only**. This endpoint never "
        "returns the reported person's name, age, gender, physical "
        "description, photo, last-seen location or coordinates, and never "
        "returns the reporter's name, phone number or relationship.\n\n"
        "There is no list endpoint and no search by name or phone. The opaque "
        "case reference is the only key."
    ),
    responses={404: {"description": "No report with that case reference."}},
)
def get_missing_person(case_reference: str, db: DbSession) -> MissingPersonPublicOut:
    case = db.execute(
        select(MissingPersonCase).where(
            # Exact match only - no LIKE, no prefix search, no id fallback.
            MissingPersonCase.case_reference == case_reference.strip().upper()
        )
    ).scalar_one_or_none()

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    # Fields are listed explicitly rather than spread from the ORM row, so a
    # column added to MissingPersonCase can never leak into this response by
    # default. tests/test_missing_person_privacy.py enforces the same rule.
    return MissingPersonPublicOut(
        case_reference=case.case_reference,
        status=case.status,
        created_at=case.created_at,
        updated_at=case.updated_at,
        prototype_notice=MISSING_PERSON_NOTICE,
    )
