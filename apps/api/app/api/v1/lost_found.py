"""
Public Lost & Found API (PRD section 16, decision D-01, contract section 5).

There are exactly two public routes here: submit a report, and read one back by
its opaque case reference. There is deliberately NO list endpoint and NO lookup
by reporter name or phone.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DbSession
from app.core.notices import LOST_FOUND_NOTICE
from app.models.cases import LostFoundCase
from app.models.enums import LostFoundStatus
from app.schemas.cases import CaseCreatedOut, LostFoundCreate, LostFoundPublicOut
from app.services.audit import record_audit
from app.services.references import allocate_case_reference

router = APIRouter(prefix="/lost-found", tags=["lost-found"])


@router.post(
    "",
    response_model=CaseCreatedOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a lost or found item report",
    description=(
        "**Demo prototype.** The report is stored in this project's own test "
        "database. It is not shared with police, railway property offices, or "
        "any lost-property authority, and no one is notified.\n\n"
        "The returned `case_reference` is the ONLY way to check this report "
        "again - there is no lookup by name or phone. Validation: "
        "`description` 10-2000 characters, `reporter_phone` required and "
        "non-empty, `occurred_at` must not be in the future."
    ),
)
def create_lost_found(payload: LostFoundCreate, db: DbSession) -> CaseCreatedOut:
    reference = allocate_case_reference(db, LostFoundCase, "LF")

    case = LostFoundCase(
        case_reference=reference,
        report_type=payload.report_type.value,
        category=payload.category.value,
        description=payload.description,
        location_text=payload.location_text,
        latitude=payload.latitude,
        longitude=payload.longitude,
        occurred_at=payload.occurred_at,
        reporter_name=payload.reporter_name,
        reporter_phone=payload.reporter_phone,
        image_url=payload.image_url,
        status=LostFoundStatus.SUBMITTED.value,
    )
    db.add(case)
    db.flush()

    record_audit(
        db,
        action="lost_found.submitted",
        entity_type="lost_found_case",
        entity_id=case.id,
        actor_user_id=None,
        detail={
            "case_reference": reference,
            "report_type": case.report_type,
            "category": case.category,
            "status": case.status,
        },
    )
    db.commit()
    db.refresh(case)

    return CaseCreatedOut(
        case_reference=case.case_reference,
        status=case.status,
        created_at=case.created_at,
        prototype_notice=LOST_FOUND_NOTICE,
    )


@router.get(
    "/{case_reference}",
    response_model=LostFoundPublicOut,
    summary="Check the status of a lost/found report by case reference",
    description=(
        "The only public read path for this resource. Returns progress and the "
        "report's own non-identifying descriptors; it does not return the "
        "reporter's name or phone number, the free-text description, the "
        "uploaded image, or the coordinates.\n\n"
        "There is no list endpoint and no search by name or phone."
    ),
    responses={404: {"description": "No report with that case reference."}},
)
def get_lost_found(case_reference: str, db: DbSession) -> LostFoundPublicOut:
    case = db.execute(
        select(LostFoundCase).where(
            # Exact match on the stored reference only. No LIKE, no prefix
            # search, no fallback to id - any of those would turn this into an
            # enumeration surface.
            LostFoundCase.case_reference == case_reference.strip().upper()
        )
    ).scalar_one_or_none()

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Case not found"
        )

    return LostFoundPublicOut(
        case_reference=case.case_reference,
        report_type=case.report_type,
        category=case.category,
        status=case.status,
        created_at=case.created_at,
        updated_at=case.updated_at,
        prototype_notice=LOST_FOUND_NOTICE,
    )
